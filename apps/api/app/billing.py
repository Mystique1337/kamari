"""Plan resolution + privilege enforcement (rate limit + monthly quota).

Plan is stored on the org owner's Supabase user_metadata (no DB migration needed) and
cached briefly by user id, so an in-app upgrade takes effect immediately. Enforcement is
per organization. The single-replica in-memory limiter is fine for the current
deployment; move to Redis if you scale to multiple replicas.
"""
import time

import httpx

from . import repo
from .config import get_settings
from .plans import DEFAULT_PLAN

_plan_cache: dict[str, tuple[str, float]] = {}   # uid -> (plan, ts)
_usage_cache: dict[str, tuple[int, float]] = {}  # org_id -> (count, ts)
_rpm_hits: dict[str, list[float]] = {}           # org_id -> recent timestamps


def _admin_headers() -> dict | None:
    s = get_settings()
    if not (s.supabase_url and s.supabase_service_role_key):
        return None
    return {"apikey": s.supabase_service_role_key,
            "Authorization": f"Bearer {s.supabase_service_role_key}"}


async def plan_for_user(uid: str | None) -> str:
    if not uid:
        return DEFAULT_PLAN
    now = time.time()
    cached = _plan_cache.get(uid)
    if cached and now - cached[1] < 120:
        return cached[0]
    h = _admin_headers()
    name = DEFAULT_PLAN
    if h:
        s = get_settings()
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{s.supabase_url.rstrip('/')}/auth/v1/admin/users/{uid}", headers=h)
                if r.status_code < 300:
                    name = ((r.json().get("user_metadata") or {}).get("plan")) or DEFAULT_PLAN
        except Exception:  # noqa: BLE001
            pass
    _plan_cache[uid] = (name, now)
    return name


async def plan_for_org(org_id: str) -> str:
    owner = await repo.owner_for_org(org_id)
    return await plan_for_user(owner) if owner else DEFAULT_PLAN


async def set_user_plan(uid: str, plan: str) -> bool:
    s = get_settings()
    h = _admin_headers()
    if not h:
        return False
    h = {**h, "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.put(f"{s.supabase_url.rstrip('/')}/auth/v1/admin/users/{uid}",
                            headers=h, json={"user_metadata": {"plan": plan}})
            if r.status_code < 300:
                _plan_cache[uid] = (plan, time.time())  # reflect immediately
                return True
    except Exception:  # noqa: BLE001
        pass
    return False


async def monthly_usage(org_id: str) -> int:
    now = time.time()
    cached = _usage_cache.get(org_id)
    if cached and now - cached[1] < 30:
        return cached[0]
    count = await repo.month_count(org_id)
    _usage_cache[org_id] = (count, now)
    return count


def under_rpm(org_id: str, rpm: int) -> tuple[bool, int]:
    """Record a hit and return (allowed, remaining_this_minute)."""
    now = time.time()
    hits = _rpm_hits.setdefault(org_id, [])
    cutoff = now - 60
    hits[:] = [t for t in hits if t > cutoff]
    if len(hits) >= rpm:
        return False, 0
    hits.append(now)
    return True, max(0, rpm - len(hits))
