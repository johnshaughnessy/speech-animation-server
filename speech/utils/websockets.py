from fastapi import WebSocket, WebSocketDisconnect
from speech.utils.serialize import serialize

websockets = {}


def websocket_for_session_id(session_id: str):
    return websockets.get(session_id)


async def send(websocket: WebSocket, name: str, data=None):
    message = {"name": name, "data": serialize(data)}
    await websocket.send_json(message)
