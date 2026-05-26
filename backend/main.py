from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base
from schemas import (
    UserCreate,
    UserResponse,
    UserLogin,
    RoomCreate,
    RoomResponse,
    ParticipantCreate,
    ParticipantResponse,
    TokenResponse
)
from crud import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    create_room,
    get_rooms,
    get_room_by_id,
    delete_room,
    join_room,
    get_room_participants,
    get_participant
)
from auth import verify_password, create_access_token, verify_access_token

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_current_user_from_token(token: str, db: Session):
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.get("/")
def home():
    return {"message": "Technical Interview Platform API"}

@app.get("/me", response_model=UserResponse)
def read_current_user(token: str, db: Session = Depends(get_db)):
    return get_current_user_from_token(token, db)


@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return create_user(db, user)


@app.post("/login", response_model=TokenResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    access_token = create_access_token(
        data={
            "sub": existing_user.email,
            "user_id": existing_user.id
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/rooms", response_model=RoomResponse)
def create_interview_room(
    room: RoomCreate,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_token(token, db)

    return create_room(db, room, current_user.id)


@app.get("/rooms", response_model=list[RoomResponse])
def get_all_rooms(db: Session = Depends(get_db)):
    return get_rooms(db)


@app.get("/rooms/{room_id}", response_model=RoomResponse)
def get_single_room(room_id: int, db: Session = Depends(get_db)):
    room = get_room_by_id(db, room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    return room


@app.delete("/rooms/{room_id}")
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

@app.post("/join-room", response_model=ParticipantResponse)
def join_interview_room(
    participant: ParticipantCreate,
    db: Session = Depends(get_db)
):
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


@app.get(
    "/rooms/{room_id}/participants",
    response_model=list[ParticipantResponse]
)
def get_participants(room_id: int, db: Session = Depends(get_db)):
    return get_room_participants(db, room_id)