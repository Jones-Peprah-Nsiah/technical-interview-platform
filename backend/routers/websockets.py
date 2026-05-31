from fastapi import APIRouter, WebSocket, WebSocketDisconnect


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

    async def broadcast(self, room_id: int, message: str):
        if room_id in self.active_rooms:
            for connection in self.active_rooms[room_id]:
                await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room(websocket: WebSocket, room_id: int):
    await manager.connect(room_id, websocket)

    try:
        while True:
            message = await websocket.receive_text()

            await manager.broadcast(
                room_id,
                f"Room {room_id}: {message}"
            )

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
        await manager.broadcast(
            room_id,
            "A user left the room"
        )