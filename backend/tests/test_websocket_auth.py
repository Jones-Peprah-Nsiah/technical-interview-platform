import pytest
from starlette.websockets import WebSocketDisconnect

from conftest import register_and_login, register, login


def create_room(client, token, title="Interview room"):
    resp = client.post(
        "/rooms",
        json={"title": title, "description": "desc"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    return resp.json()["id"]


def test_websocket_rejects_invalid_token(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/rooms/1?token=not-a-real-token"):
            pass


def test_websocket_rejects_nonexistent_room(client, monkeypatch):
    monkeypatch.setattr("routers.users.INTERVIEWER_INVITE_CODE", "interviewer-code")
    token = register_and_login(client, "owner@example.com", invite_code="interviewer-code")

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/ws/rooms/999?token={token}"):
            pass


def test_websocket_rejects_non_participant(client, monkeypatch):
    monkeypatch.setattr("routers.users.INTERVIEWER_INVITE_CODE", "interviewer-code")
    owner_token = register_and_login(client, "owner2@example.com", invite_code="interviewer-code")
    room_id = create_room(client, owner_token)

    outsider_token = register_and_login(client, "outsider@example.com")

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/ws/rooms/{room_id}?token={outsider_token}"):
            pass


def test_websocket_owner_can_connect_and_receives_join_broadcast(client, monkeypatch):
    monkeypatch.setattr("routers.users.INTERVIEWER_INVITE_CODE", "interviewer-code")
    owner_token = register_and_login(client, "owner3@example.com", invite_code="interviewer-code")
    room_id = create_room(client, owner_token)

    with client.websocket_connect(f"/ws/rooms/{room_id}?token={owner_token}") as ws:
        message = ws.receive_json()
        assert message["type"] == "user_joined"


def test_websocket_participant_can_connect(client, monkeypatch):
    monkeypatch.setattr("routers.users.INTERVIEWER_INVITE_CODE", "interviewer-code")
    owner_token = register_and_login(client, "owner4@example.com", invite_code="interviewer-code")
    room_id = create_room(client, owner_token)

    candidate_token = register_and_login(client, "candidate@example.com")
    resp = client.post(
        "/join-room",
        json={"user_id": 2, "room_id": room_id, "role": "candidate"},
        headers={"Authorization": f"Bearer {candidate_token}"},
    )
    assert resp.status_code == 200

    with client.websocket_connect(f"/ws/rooms/{room_id}?token={candidate_token}") as ws:
        message = ws.receive_json()
        assert message["type"] == "user_joined"


def test_question_selected_rejected_for_non_owner(client, monkeypatch):
    monkeypatch.setattr("routers.users.INTERVIEWER_INVITE_CODE", "interviewer-code")
    owner_token = register_and_login(client, "owner5@example.com", invite_code="interviewer-code")
    room_id = create_room(client, owner_token)

    candidate_token = register_and_login(client, "candidate2@example.com")
    client.post(
        "/join-room",
        json={"user_id": 2, "room_id": room_id, "role": "candidate"},
        headers={"Authorization": f"Bearer {candidate_token}"},
    )

    with client.websocket_connect(f"/ws/rooms/{room_id}?token={candidate_token}") as ws:
        ws.receive_json()  # user_joined

        ws.send_json({"type": "question_selected", "content": {"id": 1}})

        response = ws.receive_json()
        assert response["type"] == "error"
