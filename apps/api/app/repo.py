"""DB writes for request logging + API keys (best-effort; no-ops when DATABASE_URL unset).

All statements target the configured schema (default `kamari`). Logging never raises —
an audit-write failure must not break an age check.
"""
import hashlib
import re
import secrets

from sqlalchemy import text

from .config import get_settings
from .db import async_session_maker

_settings = get_settings()
SCHEMA = re.sub(r"[^a-zA-Z0-9_]", "", _settings.supabase_db_schema or "kamari")


def _hash_key(raw: str) -> str:
    return hashlib.sha256(f"{_settings.api_key_pepper}:{raw}".encode()).hexdigest()


# ---------------- request logging ----------------
async def log_inference(row: dict) -> None:
    """Insert age-check metadata (never the image). Best-effort."""
    if async_session_maker is None:
        return
    try:
        async with async_session_maker() as s:
            await s.execute(text(f"""
                insert into {SCHEMA}.inference_requests
                  (request_id, endpoint, model_version, decision, reason_code, face_quality,
                   estimated_age, p_under_18, uncertainty, image_stored, retention_policy)
                values (:request_id, :endpoint, :model_version, :decision, :reason_code, :face_quality,
                   :estimated_age, :p_under_18, :uncertainty, false, :retention)
                on conflict (request_id) do nothing
            """), row)
            await s.commit()
    except Exception as e:  # noqa: BLE001 — logging must never break the request
        print("[repo] inference log failed:", e)


# ---------------- API keys ----------------
async def _ensure_org(session, user) -> str:
    if getattr(user, "organization_id", None):
        return str(user.organization_id)
    r = await session.execute(
        text(f"insert into {SCHEMA}.organizations (name) values (:n) returning id"),
        {"n": (user.email or "org")})
    org_id = r.scalar_one()
    await session.execute(
        text(f"update {SCHEMA}.app_users set organization_id = :o where id = :u"),
        {"o": org_id, "u": user.id})
    await session.commit()
    return str(org_id)


async def create_api_key(session, user, name: str) -> dict:
    org_id = await _ensure_org(session, user)
    raw = "kmr_live_" + secrets.token_urlsafe(24)
    r = await session.execute(text(f"""
        insert into {SCHEMA}.api_keys (organization_id, key_hash, name)
        values (:o, :h, :n) returning id"""),
        {"o": org_id, "h": _hash_key(raw), "n": name})
    await session.commit()
    return {"id": str(r.scalar_one()), "name": name, "api_key": raw, "note": "shown once — store it now"}


async def list_api_keys(session, user) -> list[dict]:
    org_id = getattr(user, "organization_id", None)
    if not org_id:
        return []
    rows = await session.execute(text(f"""
        select id, name, status, rate_limit_per_minute, created_at, last_used_at,
               substr(key_hash, 1, 8) as prefix
        from {SCHEMA}.api_keys where organization_id = :o order by created_at desc"""),
        {"o": str(org_id)})
    return [dict(r._mapping) for r in rows]


async def revoke_api_key(session, user, key_id: str) -> None:
    org_id = getattr(user, "organization_id", None)
    await session.execute(text(f"""
        update {SCHEMA}.api_keys set status = 'revoked'
        where id = :k and organization_id = :o"""),
        {"k": key_id, "o": str(org_id)})
    await session.commit()


async def validate_api_key(raw: str) -> dict | None:
    """Return {organization_id, scopes} for an active key, else None. Best-effort."""
    if async_session_maker is None:
        return None
    try:
        async with async_session_maker() as s:
            r = await s.execute(text(f"""
                select organization_id, scopes from {SCHEMA}.api_keys
                where key_hash = :h and status = 'active' limit 1"""),
                {"h": _hash_key(raw)})
            row = r.mappings().first()
            if not row:
                return None
            await s.execute(text(f"update {SCHEMA}.api_keys set last_used_at = now() where key_hash = :h"),
                            {"h": _hash_key(raw)})
            await s.commit()
            return dict(row)
    except Exception as e:  # noqa: BLE001
        print("[repo] api key validate failed:", e)
        return None
