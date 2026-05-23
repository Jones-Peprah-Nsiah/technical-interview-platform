from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate


def create_user(db: Session, user: UserCreate):
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=user.password
    )

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user