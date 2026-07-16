from auth import (
    create_access_token,
    verify_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("secret123")

    assert hashed != "secret123"
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_roundtrip():
    token = create_access_token({"user_id": 1, "sub": "a@example.com"})
    payload = verify_access_token(token)

    assert payload["user_id"] == 1
    assert payload["sub"] == "a@example.com"


def test_verify_access_token_rejects_garbage():
    assert verify_access_token("not-a-valid-token") is None
