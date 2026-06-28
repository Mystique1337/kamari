"""Developer API-key management — Supabase GoTrue-protected; stored in kamari.api_keys."""
from fastapi import APIRouter, Depends

from .. import repo
from ..auth.gotrue import current_user

router = APIRouter(prefix="/v1/keys", tags=["keys"])


@router.post("")
async def create_key(name: str = "default", user: dict = Depends(current_user)) -> dict:
    return await repo.create_api_key(user, name)


@router.get("")
async def list_keys(user: dict = Depends(current_user)) -> list[dict]:
    return await repo.list_api_keys(user)


@router.delete("/{key_id}")
async def revoke_key(key_id: str, user: dict = Depends(current_user)) -> dict:
    await repo.revoke_api_key(user, key_id)
    return {"revoked": key_id}
