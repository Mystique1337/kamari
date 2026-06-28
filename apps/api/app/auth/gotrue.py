"""Supabase GoTrue auth - verify Supabase-issued JWTs (HS256) on protected routes.

Users live in Supabase `auth.users`; the app logs in via Supabase directly and sends the
access token as `Authorization: Bearer <token>`. We verify it with the project JWT secret.
"""
from fastapi import Header, HTTPException, status

from ..config import get_settings


async def current_user(authorization: str | None = Header(default=None)) -> dict:
    s = get_settings()
    if not s.supabase_jwt_secret:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "auth not configured")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    import jwt
    try:
        payload = jwt.decode(token, s.supabase_jwt_secret, algorithms=["HS256"],
                             audience=s.supabase_jwt_aud)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"invalid token: {e}")
    return {"id": payload.get("sub"), "email": payload.get("email"),
            "role": payload.get("role"), "claims": payload}
