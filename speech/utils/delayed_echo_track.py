from aiortc import MediaStreamTrack
from collections import deque
import numpy as np
import av
from aiortc.mediastreams import MediaStreamError
import time
from speech.utils.log import log

import asyncio
from speech.utils.log_errors import log_errors


class DelayedEchoTrack(MediaStreamTrack):
    kind = "audio"

    @log_errors
    def __init__(self):
        super().__init__()
        self.sample_rate = 48000
        self.channels = 2
        self.samples_per_frame = 960
        delay_seconds = 1.0
        delay_frames = int((delay_seconds * self.sample_rate) / self.samples_per_frame)
        silent_frame = np.zeros((self.channels, self.samples_per_frame), dtype=np.int16)
        self.buffer = deque(
            [silent_frame.copy() for _ in range(delay_frames)], maxlen=delay_frames
        )
        self.playhead = None
        self.pts = 0
        self._ended = False

    @log_errors
    def add_frame(self, frame: av.AudioFrame) -> None:
        samples = frame.to_ndarray()
        left = samples[0, ::2]  # Every even sample
        right = samples[0, 1::2]  # Every odd sample
        stereo = np.vstack([left, right])
        self.buffer.append(stereo)

    @log_errors
    async def recv(self):
        current_time = time.time()

        if self._ended:
            raise MediaStreamError

        if self.playhead is None:
            self.playhead = time.time()

        if current_time < self.playhead:
            wait_time = self.playhead - current_time
            await asyncio.sleep(wait_time)

        samples = self.buffer[0]
        frame = av.AudioFrame(
            format="s16", layout="stereo", samples=self.samples_per_frame
        )
        frame.planes[0].update(samples.T.tobytes())
        frame.sample_rate = self.sample_rate
        frame.pts = self.pts
        self.pts += self.samples_per_frame
        duration_of_frame = self.samples_per_frame / self.sample_rate
        self.playhead += duration_of_frame

        return frame
