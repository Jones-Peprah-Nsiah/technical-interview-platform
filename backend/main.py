from fastapi import FastAPI

from database import engine
from models import Base
from routers import users, rooms, participants, questions

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(participants.router)
app.include_router(questions.router)


@app.get("/")
def home():
    return {"message": "Technical Interview Platform API"}