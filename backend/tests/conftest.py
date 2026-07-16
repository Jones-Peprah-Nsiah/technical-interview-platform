import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import database
from database import Base, get_db
from routers import users, rooms, participants, questions, websockets, code_sessions


@pytest.fixture()
def test_engine(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def client(test_engine, monkeypatch):
    test_session_local = sessionmaker(
        bind=test_engine, autoflush=False, autocommit=False
    )

    # auth.get_current_user opens its own session via `from database import
    # SessionLocal` at call time, so patching the module attribute redirects
    # it to the test database too, not just the get_db-injected sessions.
    monkeypatch.setattr(database, "SessionLocal", test_session_local)

    def override_get_db():
        db = test_session_local()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.dependency_overrides[get_db] = override_get_db
    app.include_router(users.router)
    app.include_router(rooms.router)
    app.include_router(participants.router)
    app.include_router(questions.router)
    app.include_router(websockets.router)
    app.include_router(code_sessions.router)

    with TestClient(app) as test_client:
        yield test_client


def register(client, email, password="password123", invite_code=None, full_name="Test User"):
    payload = {"full_name": full_name, "email": email, "password": password}
    if invite_code is not None:
        payload["invite_code"] = invite_code
    return client.post("/register", json=payload)


def login(client, email, password="password123"):
    return client.post("/login", json={"email": email, "password": password})


def register_and_login(client, email, password="password123", invite_code=None, full_name="Test User"):
    register(client, email, password=password, invite_code=invite_code, full_name=full_name)
    return login(client, email, password=password).json()["access_token"]
