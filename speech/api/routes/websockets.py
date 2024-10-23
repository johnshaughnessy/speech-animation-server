from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from aiortc import RTCSessionDescription, RTCPeerConnection
from speech.utils.log import log
from speech.utils.websockets import send, websockets, websocket_for_session_id
from speech.utils.webrtc import peer_connections, peer_connection_for_session_id
from speech.types import WebsocketMessage
import asyncio
import json

router = APIRouter()


async def on_echo_message(websocket: WebSocket, message: WebsocketMessage):
    await send(websocket, "echo", message.data)


async def on_webrtc_icecandidate(websocket: WebSocket, message: WebsocketMessage):
    # log.info("Received ICE candidate: ", message.data)
    pass


async def on_webrtc_sdp_offer(websocket: WebSocket, message: WebsocketMessage):
    session_id = message.session_id
    if peer_connection_for_session_id(session_id):
        log.warn(
            "Received new webrtc session message, but we already have a connection. Closing old connection."
        )
        await peer_connection_for_session_id(session_id).close()
        peer_connections[session_id] = None
        logger.info("Closed old connection")

    pc = RTCPeerConnection()
    peer_connections[session_id] = pc

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log.info(f"Connection state change: {pc.connectionState}")
        if pc.connectionState == "closed":
            await pc.close()
            # TODO If we have an opus track, close it

    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
        # TODO: Is this necessary?
        await send(websocket, "webrtc_icecandidate", {"candidate": candidate})

    @pc.on("track")
    def on_track(track):
        log.info(f"Received track: {track.kind}")
        if track.kind == "audio":
            pc.addTrack(track)

    browser_sdp = message.data.get("sdp")
    offer = RTCSessionDescription(sdp=browser_sdp["sdp"], type=browser_sdp["type"])
    await pc.setRemoteDescription(offer)
    # TODO: Add opus track
    await pc.setLocalDescription(await pc.createAnswer())
    await send(
        websocket,
        "webrtc_sdp_answer",
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type},
    )


message_handlers = {
    "echo": on_echo_message,
    "webrtc_icecandidate": on_webrtc_icecandidate,
    "webrtc_sdp_offer": on_webrtc_sdp_offer,
}


async def handle_message(websocket: WebSocket, message: WebsocketMessage):
    handler = message_handlers.get(message.name)
    if handler:
        try:
            await handler(websocket, message)
        except Exception as e:
            log.error(f"Error handling websocket message: {str(message)}\n\n{str(e)}")
            await websocket.send_json(
                {"error": f"Error processing message: {str(message)}"}
            )
    else:
        log.warning(f"No handler for event: {message.name}")
        await websocket.send_json({"error": f"Unknown event: {message.name}"})


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    session_id = None
    try:
        while True:
            message = WebsocketMessage(**(await websocket.receive_json()))
            if session_id is None:
                session_id = message.session_id
                websockets[session_id] = websocket
            asyncio.create_task(handle_message(websocket, message))

    except WebSocketDisconnect:
        log.info("WebSocket disconnected")
    except json.JSONDecodeError:
        log.error("Received invalid JSON")
        await websocket.close(code=1003, reason="Invalid JSON")
    except Exception as e:
        log.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011, reason="Internal server error")
    finally:
        if session_id:
            if websocket_for_session_id(session_id):
                del websockets[session_id]
            if peer_connection_for_session_id(session_id):
                await peer_connection_for_session_id(session_id).close()
                del peer_connections[session_id]
        pass
