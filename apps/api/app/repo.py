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
    if row.get("organization_id"):
        rec["organization_id"] = row["organization_id"]
    try:
        await asyncio.to_thread(lambda: _tbl("inference_requests").insert(rec).execute())
    except Exception as e:  # noqa: BLE001 - logging must never break the request
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
    return {"name": name, "api_key": raw, "note": "shown once - store it now"}


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


async def org_id_for_user(user: dict) -> str | None:
    if get_client() is None:
        return None
    res = await asyncio.to_thread(
        lambda: _tbl("organizations").select("id").eq("owner_auth_id", user["id"]).limit(1).execute())
    return res.data[0]["id"] if res.data else None


async def owner_for_org(org_id: str) -> str | None:
    if get_client() is None:
        return None
    res = await asyncio.to_thread(
        lambda: _tbl("organizations").select("owner_auth_id").eq("id", org_id).limit(1).execute())
    return res.data[0]["owner_auth_id"] if res.data else None


async def month_count(org_id: str) -> int:
    """Count this org's age checks since the start of the current UTC month."""
    if get_client() is None:
        return 0
    from datetime import datetime, timezone
    start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    try:
        res = await asyncio.to_thread(
            lambda: _tbl("inference_requests").select("id", count="exact")
            .eq("organization_id", org_id).gte("created_at", start.isoformat()).execute())
        return res.count or 0
    except Exception as e:  # noqa: BLE001
        print("[repo] month_count failed:", e)
        return 0


async def get_key_name(user: dict, key_id: str) -> str | None:
    org_id = await org_id_for_user(user)
    if not org_id:
        return None
    res = await asyncio.to_thread(
        lambda: _tbl("api_keys").select("name").eq("id", key_id)
        .eq("organization_id", org_id).limit(1).execute())
    return res.data[0]["name"] if res.data else None


# ---------------- usage analytics (org-scoped) ----------------
async def usage_summary(org_id: str | None) -> dict:
    """Counts + decision mix for a developer's own traffic (their API keys)."""
    empty = {"total": 0, "allow": 0, "block": 0, "secondary_check": 0, "recapture": 0,
             "allow_rate": 0.0, "last_24h": 0}
    if get_client() is None or not org_id:
        return empty
    try:
        rows = await asyncio.to_thread(
            lambda: _tbl("inference_requests").select("decision,created_at")
            .eq("organization_id", org_id).order("created_at", desc=True).limit(5000).execute())
        data = rows.data or []
        out = dict(empty)
        out["total"] = len(data)
        for r in data:
            d = r.get("decision")
            if d in out:
                out[d] += 1
        out["allow_rate"] = round(out["allow"] / out["total"], 3) if out["total"] else 0.0
        return out
    except Exception as e:  # noqa: BLE001
        print("[repo] usage summary failed:", e)
        return empty


async def usage_logs(org_id: str | None, limit: int = 50) -> list[dict]:
    if get_client() is None or not org_id:
        return []
    try:
        rows = await asyncio.to_thread(
            lambda: _tbl("inference_requests")
            .select("request_id,endpoint,decision,reason_code,estimated_age,created_at")
            .eq("organization_id", org_id).order("created_at", desc=True).limit(limit).execute())
        return rows.data or []
    except Exception as e:  # noqa: BLE001
        print("[repo] usage logs failed:", e)
        return []
