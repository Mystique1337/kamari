"""DB ops via Supabase REST (PostgREST) against the `kamari` schema.

Best-effort: a logging failure must never break an age check. No-ops when Supabase
isn't configured. Requires `kamari` to be exposed in PostgREST (db-schemas).
"""
import asyncio
import hashlib
import secrets

from .config import get_settings
from .supa import get_client

_settings = get_settings()
SCHEMA = _settings.supabase_db_schema or "kamari"


def _hash_key(raw: str) -> str:
    return hashlib.sha256(f"{_settings.api_key_pepper}:{raw}".encode()).hexdigest()


def _tbl(name: str):
    cli = get_client()
    return cli.schema(SCHEMA).table(name) if cli else None


# ---------------- request logging ----------------
async def log_inference(row: dict) -> None:
    if get_client() is None:
        return
    rec = {
        "request_id": row.get("request_id"), "endpoint": row.get("endpoint"),
        "model_version": row.get("model_version"), "decision": row.get("decision"),
        "reason_code": row.get("reason_code"), "face_quality": row.get("face_quality"),
        "estimated_age": row.get("estimated_age"), "p_under_18": row.get("p_under_18"),
        "uncertainty": row.get("uncertainty"), "image_stored": False,
        "retention_policy": row.get("retention") or row.get("retention_policy"),
    }
    try:
        await asyncio.to_thread(lambda: _tbl("inference_requests").insert(rec).execute())
    except Exception as e:  # noqa: BLE001 — logging must never break the request
        print("[repo] inference log failed:", e)


# ---------------- API keys ----------------
async def _ensure_org(user: dict) -> str:
    auth_id = user["id"]
    res = await asyncio.to_thread(
        lambda: _tbl("organizations").select("id").eq("owner_auth_id", auth_id).limit(1).execute())
    if res.data:
        return res.data[0]["id"]
    ins = await asyncio.to_thread(
        lambda: _tbl("organizations").insert(
            {"name": user.get("email") or "org", "owner_auth_id": auth_id}).execute())
    return ins.data[0]["id"]


async def create_api_key(user: dict, name: str) -> dict:
    org_id = await _ensure_org(user)
    raw = "kmr_live_" + secrets.token_urlsafe(24)
    await asyncio.to_thread(
        lambda: _tbl("api_keys").insert(
            {"organization_id": org_id, "key_hash": _hash_key(raw), "name": name}).execute())
    return {"name": name, "api_key": raw, "note": "shown once — store it now"}


async def list_api_keys(user: dict) -> list[dict]:
    res = await asyncio.to_thread(
        lambda: _tbl("organizations").select("id").eq("owner_auth_id", user["id"]).limit(1).execute())
    if not res.data:
        return []
    org_id = res.data[0]["id"]
    keys = await asyncio.to_thread(
        lambda: _tbl("api_keys").select("id,name,status,rate_limit_per_minute,created_at,last_used_at")
        .eq("organization_id", org_id).order("created_at", desc=True).execute())
    return keys.data or []


async def revoke_api_key(user: dict, key_id: str) -> None:
    res = await asyncio.to_thread(
        lambda: _tbl("organizations").select("id").eq("owner_auth_id", user["id"]).limit(1).execute())
    if not res.data:
        return
    org_id = res.data[0]["id"]
    await asyncio.to_thread(
        lambda: _tbl("api_keys").update({"status": "revoked"})
        .eq("id", key_id).eq("organization_id", org_id).execute())


async def validate_api_key(raw: str) -> dict | None:
    if get_client() is None:
        return None
    try:
        res = await asyncio.to_thread(
            lambda: _tbl("api_keys").select("organization_id,scopes,status")
            .eq("key_hash", _hash_key(raw)).eq("status", "active").limit(1).execute())
        if not res.data:
            return None
        await asyncio.to_thread(
            lambda: _tbl("api_keys").update({"last_used_at": "now()"})
            .eq("key_hash", _hash_key(raw)).execute())
        return res.data[0]
    except Exception as e:  # noqa: BLE001
        print("[repo] api key validate failed:", e)
        return None
