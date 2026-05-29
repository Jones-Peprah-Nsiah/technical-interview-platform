from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import RoomCreate, RoomResponse, RoomUpdate
from crud import (
    create_room,
    get_room_by_id,
    delete_room,
    update_room
)
from auth import get_current_user_from_token

router = APIRouter(tags=["Rooms"])


@router.post("/rooms", response_model=RoomResponse)
def create_interview_room(
    room: RoomCreate,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_token(token, db)

    if current_user.role != "interviewer":
        raise HTTPException(
            status_code=403,
            detail="Only interviewers can create rooms"
        )

    return create_room(db, room, current_user.id)


@router.get("/rooms/{room_id}", response_model=RoomResponse)
def get_single_room(room_id: int, db: Session = Depends(get_db)):
    room = get_room_by_id(db, room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    return room


@router.delete("/rooms/{room_id}")
def delete_interview_room(
    room_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_token(token, db)

    room = get_room_by_id(db, room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this room"
        )

    delete_room(db, room_id)

    return {
        "message": "Room deleted successfully"
    }


@router.put("/rooms/{room_id}", response_model=RoomResponse)
def update_interview_room(
    room_id: int,
    room_data: RoomUpdate,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_token(token, db)

    if current_user.role != "interviewer":
        raise HTTPException(
            status_code=403,
            detail="Only interviewers can update rooms"
        )

    room = get_room_by_id(db, room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this room"
        )

    return update_room(db, room_id, room_data)