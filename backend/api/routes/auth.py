"""JWT authentication routes for OdaTrade API."""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.auth.jwt_handler import create_token, verify_token
from backend.auth.middleware import require_auth

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory user store (replace with DB in production)
_USERS = {
    "admin": {"password": "odatrade-admin", "role": "admin"},
    "trader": {"password": "odatrade-trader", "role": "trader"},
    "viewer": {"password": "odatrade-viewer", "role": "viewer"},
}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    role: str


class UserInfo(BaseModel):
    username: str
    role: str


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    user = _USERS.get(req.username)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(req.username, expires_in=3600)
    return TokenResponse(access_token=token, role=user["role"])


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(auth=Depends(require_auth)):
    username = auth.get("sub", "unknown")
    user = _USERS.get(username, {"role": "viewer"})
    token = create_token(username, expires_in=3600)
    return TokenResponse(access_token=token, role=user["role"])


@router.get("/me", response_model=UserInfo)
def get_current_user(auth=Depends(require_auth)):
    username = auth.get("sub", "unknown")
    user = _USERS.get(username, {"role": "viewer"})
    return UserInfo(username=username, role=user["role"])


@router.get("/verify")
def verify(auth=Depends(require_auth)):
    return {"valid": True, "user": auth.get("sub"), "app": auth.get("app")}
