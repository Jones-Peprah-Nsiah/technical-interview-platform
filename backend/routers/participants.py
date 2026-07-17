from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import ParticipantCreate, ParticipantResponse
from crud import (
    get_room_by_id,
    get_participant,
    join_room,
    get_room_participants
)
from auth import get_current_user


router = APIRouter(tags=["Participants"])


@router.post("/join-room", response_model=ParticipantResponse)
def join_interview_room(
    participant: ParticipantCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    room = get_room_by_id(db, participant.room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    existing_participant = get_participant(
        db,
        current_user.id,
        participant.room_id
    )

    if existing_participant:
        raise HTTPException(
            status_code=400,
            detail="User already joined this room"
        )

    return join_room(db, participant, current_user.id, current_user.role)


@router.get(
    "/rooms/{room_id}/participants",
    response_model=list[ParticipantResponse]
)
def get_participants(room_id: int, db: Session = Depends(get_db)):
    return get_room_participants(db, room_id)