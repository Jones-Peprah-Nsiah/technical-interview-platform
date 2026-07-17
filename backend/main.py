from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models import Base
from routers import users, rooms, participants, questions, websockets, code_sessions, execution, question_bank

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(participants.router)
app.include_router(questions.router)
app.include_router(websockets.router)
app.include_router(code_sessions.router)
app.include_router(execution.router)
app.include_router(question_bank.router)


@app.get("/")
def home():
    return {"message": "Technical Interview Platform API"}