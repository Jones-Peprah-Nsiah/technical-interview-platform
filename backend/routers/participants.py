from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import ParticipantCreate, ParticipantResponse
from crud import (
    get_user_by_id,
    get_room_by_id,
    get_participant,
    join_room,
    get_room_participants
)


router = APIRouter(tags=["Participants"])


@router.post("/join-room", response_model=ParticipantResponse)
def join_interview_room(
    participant: ParticipantCreate,
    db: Session = Depends(get_db)
):
    allowed_roles = ["candidate", "interviewer"]

    if participant.role not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Use candidate or interviewer"
        )

    user = get_user_by_id(db, participant.user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    room = get_room_by_id(db, participant.room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    existing_participant = get_participant(
        db,
        participant.user_id,
        participant.room_id
    )

    if existing_participant:
        raise HTTPException(
            status_code=400,
            detail="User already joined this room"
        )

    return join_room(db, participant)


@router.get(
    "/rooms/{room_id}/participants",
    response_model=list[ParticipantResponse]
)
def get_participants(room_id: int, db: Session = Depends(get_db)):
    return get_room_participants(db, room_id)