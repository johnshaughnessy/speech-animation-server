from aiortc.rtcrtpreceiver import RemoteStreamTrack
from aiortc import RTCPeerConnection
from aiortc import MediaStreamTrack
from typing import List, Optional
from aiortc.mediastreams import MediaStreamError
import numpy as np
from speech.utils.log import log


class IncomingAudioTrack:
    track: RemoteStreamTrack
    sample_rate: int
    channels: int
    frame_buffer: List[np.ndarray]
    is_buffering: bool

    def __init__(self, track: RemoteStreamTrack):
        self.track = track
        self.sample_rate = 0
        self.channels = 0
        self.frame_buffer = []
        self.is_buffering = False


class WebRTCConnection:
    pc: RTCPeerConnection
    incoming_audio_track: Optional[IncomingAudioTrack]
    outgoing_audio_track: Optional[MediaStreamTrack]
    delayed_echo_track: Optional[MediaStreamTrack]

    def __init__(self, pc: RTCPeerConnection):
        self.pc = pc
        self.incoming_audio_track = None
        self.outgoing_audio_track = None
        self.delayed_echo_track = None


webrtc_connections = {}


def webrtc_connection_for_session_id(session_id: str):
    return webrtc_connections.get(session_id)


async def on_incoming_audio_track(conn: WebRTCConnection, track: RemoteStreamTrack):
    if track.kind != "audio":
        return

    if conn.incoming_audio_track:
        log.warn("Received audio track, but we already have one. Closing old track.")
        conn.incoming_audio_track.track.stop()
        conn.incoming_audio_track = None

    conn.incoming_audio_track = IncomingAudioTrack(track)

    while True:
        try:
            frame = await track.recv()

            # Initialize audio properties if not set
            if conn.incoming_audio_track.sample_rate == 0:
                conn.incoming_audio_track.sample_rate = frame.sample_rate
                conn.incoming_audio_track.channels = len(frame.layout.channels)
                log.info(
                    f"Received audio track with sample rate {conn.incoming_audio_track.sample_rate} and "
                    f"{conn.incoming_audio_track.channels} channels"
                )

                # if conn.delayed_echo_track is not None:
                # conn.delayed_echo_track.configure(
                #     delay_seconds=3.0,
                #     sample_rate=conn.incoming_audio_track.sample_rate,
                #     channels=conn.incoming_audio_track.channels,
                # )

            if conn.incoming_audio_track.is_buffering:
                conn.incoming_audio_track.frame_buffer.append(frame.to_ndarray())

            if conn.delayed_echo_track is not None:
                conn.delayed_echo_track.add_frame(frame)

        except MediaStreamError:
            # This exception is raised when the track ends
            conn.incoming_audio_track = None
            break
