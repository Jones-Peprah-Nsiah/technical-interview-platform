from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import CodeSessionCreate, CodeSessionResponse
from crud import (
    get_room_by_id,
    get_participant,
    get_code_session_by_room,
    create_or_update_code_session
)
from auth import get_current_user_from_token


router = APIRouter(tags=["Code Sessions"])


@router.get(
    "/rooms/{room_id}/code",
    response_model=CodeSessionResponse
)
def get_room_code(
    room_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_token(token, db)

    room = get_room_by_id(db, room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    participant = get_participant(db, current_user.id, room_id)

    if room.user_id != current_user.id and not participant:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to view this room code"
        )

    code_session = get_code_session_by_room(db, room_id)

    if not code_session:
        raise HTTPException(status_code=404, detail="Code session not found")

    return code_session


@router.put(
    "/rooms/{room_id}/code",
    response_model=CodeSessionResponse
)
def update_room_code(
    room_id: int,
    code_data: CodeSessionCreate,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_token(token, db)

    room = get_room_by_id(db, room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    participant = get_participant(db, current_user.id, room_id)

    if room.user_id != current_user.id and not participant:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this room code"
        )

    return create_or_update_code_session(db, room_id, code_data)