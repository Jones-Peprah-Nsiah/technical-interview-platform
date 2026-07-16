import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config import INTERVIEWER_INVITE_CODE
from database import get_db
from schemas import UserCreate, UserResponse, UserLogin, TokenResponse
from crud import create_user, get_user_by_email, get_user_by_id
from auth import verify_password, create_access_token, get_current_user


router = APIRouter(tags=["Users"])



@router.get("/me", response_model=UserResponse)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    role = "candidate"
    if INTERVIEWER_INVITE_CODE and secrets.compare_digest(
        user.invite_code or "", INTERVIEWER_INVITE_CODE
    ):
        role = "interviewer"

    return create_user(db, user, role)


@router.post("/login", response_model=TokenResponse)
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