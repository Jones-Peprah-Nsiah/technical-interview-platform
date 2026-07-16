from conftest import register


def test_register_without_invite_code_is_candidate(client):
    resp = register(client, "alice@example.com")

    assert resp.status_code == 200
    assert resp.json()["role"] == "candidate"


def test_register_with_wrong_invite_code_is_still_candidate(client, monkeypatch):
    monkeypatch.setattr("routers.users.INTERVIEWER_INVITE_CODE", "correct-code")

    resp = register(client, "bob@example.com", invite_code="wrong-code")

    assert resp.status_code == 200
    assert resp.json()["role"] == "candidate"


def test_register_with_correct_invite_code_is_interviewer(client, monkeypatch):
    monkeypatch.setattr("routers.users.INTERVIEWER_INVITE_CODE", "correct-code")

    resp = register(client, "carol@example.com", invite_code="correct-code")

    assert resp.status_code == 200
    assert resp.json()["role"] == "interviewer"


def test_invite_code_disabled_when_blank(client, monkeypatch):
    monkeypatch.setattr("routers.users.INTERVIEWER_INVITE_CODE", "")

    resp = register(client, "dan@example.com", invite_code="anything-at-all")

    assert resp.status_code == 200
    assert resp.json()["role"] == "candidate"


def test_duplicate_email_rejected(client):
    first = register(client, "eve@example.com")
    second = register(client, "eve@example.com")

    assert first.status_code == 200
    assert second.status_code == 400
