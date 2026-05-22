from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base
from schemas import UserCreate, UserResponse
from crud import create_user

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Technical Interview Platform API"}


@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)