"""API-key auth dependency.

Keys are validated by salted hash (pepper). In production, look up `key_hash` in
Supabase `api_keys` and enforce scopes/rate limits. In dev (require_api_key=False),
requests pass through so the app can be exercised locally.
"""
import hashlib

from fastapi import Header, HTTPException, Response, status

from ..config import get_settings


def hash_key(raw_key: str, pepper: str) -> str:
    return hashlib.sha256(f"{pepper}:{raw_key}".encode()).hexdigest()


async def require_key(
    response: Response, authorization: str | None = Header(default=None),
) -> str | None:
    """Validate an API key when one is provided and enforce the org's plan limits.

    Returns the organization_id when a valid key is used (so usage is org-scoped), or
    None for keyless public checks. A key is mandatory only when REQUIRE_API_KEY is set.
    """
    s = get_settings()
    has_key = bool(authorization and authorization.lower().startswith("bearer "))
    if not has_key:
        if s.require_api_key:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing bearer api key")
        return None

    raw = authorization.split(" ", 1)[1].strip()
    from .. import billing, repo
    from ..plans import plan_for
    info = await repo.validate_api_key(raw)
    if not info:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid api key")
    org_id = str(info.get("organization_id"))

    plan = plan_for(await billing.plan_for_org(org_id))
    ok, remaining = billing.under_rpm(org_id, plan["rpm"])
    used = await billing.monthly_usage(org_id)
    # Standard rate-limit headers so integrators can back off gracefully.
    response.headers["X-RateLimit-Limit"] = str(plan["rpm"])
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-Quota-Limit"] = str(plan["monthly_quota"])
    response.headers["X-Quota-Used"] = str(used)
    if not ok:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            f"Rate limit reached ({plan['rpm']}/min on the {plan['label']} plan).",
            headers={"Retry-After": "60"})
    if used >= plan["monthly_quota"]:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            f"Monthly quota reached ({plan['monthly_quota']} on the {plan['label']} plan). Upgrade to continue.",
            headers={"Retry-After": "3600"})
    return org_id
