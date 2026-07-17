import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user_from_token
from schemas import CodeSessionCreate
from crud import (
    get_room_by_id,
    get_participant,
    create_or_update_code_session
)


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
        if room_id in self.active_rooms and websocket in self.active_rooms[room_id]:
            self.active_rooms[room_id].remove(websocket)

            if len(self.active_rooms[room_id]) == 0:
                del self.active_rooms[room_id]

    async def broadcast(self, room_id: int, message: dict):
        if room_id not in self.active_rooms:
            return

        dead_connections = []

        for connection in self.active_rooms[room_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(room_id, connection)


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

    room = get_room_by_id(db, room_id)

    if not room:
        await websocket.close(code=1008)
        return

    participant = get_participant(db, current_user.id, room_id)

    if room.user_id != current_user.id and not participant:
        await websocket.close(code=1008)
        return

    await manager.connect(room_id, websocket)

    try:
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

            if message_type not in ["code_update", "chat_message", "question_selected", "run_output"]:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Invalid message type"
                    }
                )
                continue

            if message_type == "question_selected":
                if current_user.role != "interviewer" or current_user.id != room.user_id:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": "Only the interviewer who owns this room can select a question"
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

            elif message_type == "code_update":
                language = message.get("language", "python")

                code_data = CodeSessionCreate(
                    code=content,
                    language=language
                )

                create_or_update_code_session(db, room_id, code_data)

                await manager.broadcast(
                    room_id,
                    {
                        "type": message_type,
                        "room_id": room_id,
                        "user_id": current_user.id,
                        "role": current_user.role,
                        "content": content,
                        "language": language
                    }
                )

            else:
                await manager.broadcast(
                    room_id,
                    {
                        "type": message_type,
                        "room_id": room_id,
                        "user_id": current_user.id,
                        "role": current_user.role,
                        "full_name": current_user.full_name,
                        "content": content
                    }
                )

    except WebSocketDisconnect:
        pass
    finally:
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