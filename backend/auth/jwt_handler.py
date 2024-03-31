"""JWT token handling for OdaTrade API."""
import time
import hmac
import hashlib
import json
import base64
from config.config import JWT_SECRET

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def create_token(user_id: str, expires_in: int = 3600) -> str:
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64(json.dumps({"sub": user_id, "exp": int(time.time()) + expires_in, "app": "OdaTrade"}).encode())
    sig = _b64(hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}"

def verify_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token")
    header, payload, sig = parts
    expected = _b64(hmac.new(JWT_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(sig, expected):
        raise ValueError("Invalid signature")
    data = json.loads(base64.urlsafe_b64decode(payload + "=="))
    if data.get("exp", 0) < time.time():
        raise ValueError("Token expired")
    return data
