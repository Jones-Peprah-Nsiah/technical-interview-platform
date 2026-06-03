import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user_from_token


router = APIRouter(tags=["WebSockets"])


class ConnectionManager:
    def __init__(self):
        self.active_rooms = {}

    async def connect(self, room_id: int, websocket: WebSocket):
        await websocket.accept()

        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = []

        self.active_rooms[room_id].append(websocket)

    def disconnect(self, room_id: int, websocket: WebSocket):
        if room_id in self.active_rooms:
            self.active_rooms[room_id].remove(websocket)

            if len(self.active_rooms[room_id]) == 0:
                del self.active_rooms[room_id]

    async def broadcast(self, room_id: int, message: dict):
        if room_id in self.active_rooms:
            for connection in self.active_rooms[room_id]:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room(
    websocket: WebSocket,
    room_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    try:
        current_user = get_current_user_from_token(token, db)
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(room_id, websocket)

    await manager.broadcast(
        room_id,
        {
            "type": "user_joined",
            "room_id": room_id,
            "user_id": current_user.id,
            "role": current_user.role,
            "message": f"{current_user.full_name} joined the room"
        }
    )

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Invalid JSON format"
                    }
                )
                continue

            message_type = message.get("type")
            content = message.get("content")

            if message_type not in ["code_update", "chat_message"]:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Invalid message type"
                    }
                )
                continue

            await manager.broadcast(
                room_id,
                {
                    "type": message_type,
                    "room_id": room_id,
                    "user_id": current_user.id,
                    "role": current_user.role,
                    "content": content
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)

        await manager.broadcast(
            room_id,
            {
                "type": "user_left",
                "room_id": room_id,
                "user_id": current_user.id,
                "role": current_user.role,
                "message": f"{current_user.full_name} left the room"
            }
        )