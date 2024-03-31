"""FastAPI auth dependency."""
from fastapi import Header, HTTPException
from backend.auth.jwt_handler import verify_token

async def require_auth(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")
    try:
        return verify_token(authorization[7:])
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
