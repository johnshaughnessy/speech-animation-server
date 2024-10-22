from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from speech.utils.log import log
from speech.utils.serialize import serialize
from speech.types import WebsocketMessage
import asyncio
import json


async def send(websocket: WebSocket, name: str, data=None):
    message = {"name": name, "data": serialize(data)}
    await websocket.send_json(message)  # TODO: Retries?


router = APIRouter()

websockets = {}


def websocket_for_session_id(session_id: str):
    return websockets.get(session_id)


async def on_echo_message(websocket: WebSocket, message: WebsocketMessage):
    log.info(f"Echoing message: {message.data}")
    await send(websocket, "echo", message.data)


message_handlers = {
    "echo": on_echo_message,
    # "webrtc_candidate_message": on_webrtc_candidate_message,
    # "webrtc_session_message": on_webrtc_session_message,
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
            websocket_message = WebsocketMessage(**(await websocket.receive_json()))
            if session_id is None:
                session_id = websocket_message.session_id
                websockets[session_id] = websocket

            log.info(f"Received message", websocket_message)
            asyncio.create_task(handle_message(websocket, websocket_message))

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
            del websockets[session_id]
        pass
