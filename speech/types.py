from pydantic import BaseModel
from typing import Optional, List, Any


class WebsocketMessage(BaseModel):
    session_id: str
    name: str
    data: Any
