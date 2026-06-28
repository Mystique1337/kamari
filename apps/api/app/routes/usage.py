"""Developer usage analytics. GoTrue-protected; scoped to the caller's organization.

Numbers reflect requests made with the developer's own API keys (organization_id is
stamped on each inference when a key is used).
"""
from fastapi import APIRouter, Depends

from .. import repo
from ..auth.gotrue import current_user

router = APIRouter(prefix="/v1/usage", tags=["usage"])


@router.get("/summary")
async def summary(user: dict = Depends(current_user)) -> dict:
    org_id = await repo.org_id_for_user(user)
    return await repo.usage_summary(org_id)


@router.get("/logs")
async def logs(limit: int = 50, user: dict = Depends(current_user)) -> list[dict]:
    org_id = await repo.org_id_for_user(user)
    return await repo.usage_logs(org_id, min(max(limit, 1), 200))
