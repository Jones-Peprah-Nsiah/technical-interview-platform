from sqlalchemy.orm import Session

from models import User, Room, Participant
from schemas import UserCreate
from auth import hash_password


def create_user(db: Session, user: UserCreate):
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_room(db: Session, room):
    new_room = Room(
        title=room.title,
        description=room.description,
        user_id=room.user_id
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return new_room


def get_rooms(db: Session):
    return db.query(Room).all()


def get_room_by_id(db: Session, room_id: int):
    return db.query(Room).filter(Room.id == room_id).first()


def delete_room(db: Session, room_id: int):
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        return None

    db.delete(room)
    db.commit()

    return room


def join_room(db: Session, participant):
    new_participant = Participant(
        user_id=participant.user_id,
        room_id=participant.room_id
    )

    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)

    return new_participant


def get_room_participants(db: Session, room_id: int):
    return (
        db.query(Participant)
        .filter(Participant.room_id == room_id)
        .all()
    )

