"""API-key auth dependency.

Keys are validated by salted hash (pepper). In production, look up `key_hash` in
Supabase `api_keys` and enforce scopes/rate limits. In dev (require_api_key=False),
requests pass through so the app can be exercised locally.
"""
import hashlib

from fastapi import Header, HTTPException, status

from ..config import get_settings


def hash_key(raw_key: str, pepper: str) -> str:
    return hashlib.sha256(f"{pepper}:{raw_key}".encode()).hexdigest()


async def require_key(authorization: str | None = Header(default=None)) -> str | None:
    s = get_settings()
    if not s.require_api_key:
        return None
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer api key")
    raw = authorization.split(" ", 1)[1].strip()
    from .. import repo
    info = await repo.validate_api_key(raw)
    if not info:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid api key")
    return str(info.get("organization_id"))
