from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import ParticipantCreate, ParticipantResponse
from crud import (
    get_room_by_id,
    get_participant,
    join_room,
    get_room_participants,
    get_user_by_id
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

    new_participant = join_room(db, participant, current_user.id, current_user.role)

    return {
        "id": new_participant.id,
        "user_id": new_participant.user_id,
        "room_id": new_participant.room_id,
        "role": new_participant.role,
        "full_name": current_user.full_name,
        "email": current_user.email,
    }


@router.get(
    "/rooms/{room_id}/participants",
    response_model=list[ParticipantResponse]
)
def get_participants(room_id: int, db: Session = Depends(get_db)):
    participants = get_room_participants(db, room_id)
    enriched = []

    for p in participants:
        user = get_user_by_id(db, p.user_id)
        enriched.append({
            "id": p.id,
            "user_id": p.user_id,
            "room_id": p.room_id,
            "role": p.role,
            "full_name": user.full_name if user else "Unknown user",
            "email": user.email if user else "",
        })

    return enriched