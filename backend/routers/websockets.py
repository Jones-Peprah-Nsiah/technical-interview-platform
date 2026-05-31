from fastapi import APIRouter, WebSocket, WebSocketDisconnect


router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room(websocket: WebSocket, room_id: int):
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()

            await websocket.send_text(
                f"Room {room_id} received: {message}"
            )

    except WebSocketDisconnect:
        print(f"Client disconnected from room {room_id}")