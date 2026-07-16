from conftest import register, login, register_and_login


def test_login_wrong_password_rejected(client):
    register(client, "u@example.com", password="correctpw")

    resp = login(client, "u@example.com", password="wrongpw")

    assert resp.status_code == 401


def test_login_unknown_email_rejected(client):
    resp = login(client, "nobody@example.com", password="whatever")

    assert resp.status_code == 404


def test_me_requires_a_token(client):
    resp = client.get("/me")

    assert resp.status_code == 401


def test_me_rejects_garbage_token(client):
    resp = client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert resp.status_code == 401


def test_me_returns_current_user(client):
    token = register_and_login(client, "me@example.com")

    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"
