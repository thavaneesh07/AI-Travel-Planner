from backend.auth.password import get_password_hash, verify_password
from backend.auth.jwthandler import create_access_token, decode_access_token

def test_password_hash():
    hashed = get_password_hash("secret")
    assert verify_password("secret", hashed)
    assert not verify_password("not-secret", hashed)

def test_jwt_tokens():
    token = create_access_token({"sub": "user@example.com"})
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded.get("sub") == "user@example.com"
