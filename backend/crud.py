from sqlalchemy.orm import Session

from models import User, Room
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


def create_room(db: Session, room):
    new_room = Room(
        title=room.title,
        description=room.description
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return new_room


def get_rooms(db: Session):
    return db.query(Room).all()


def get_room_by_id(db: Session, room_id: int):
    return db.query(Room).filter(Room.id == room_id).first()