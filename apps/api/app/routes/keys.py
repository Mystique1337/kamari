"""Developer API-key management. Supabase GoTrue-protected; stored in api_keys.

On create and revoke we send a transactional email through the n8n workflow (best effort).
"""
from fastapi import APIRouter, BackgroundTasks, Depends

from .. import email, repo
from ..auth.gotrue import current_user
from ..config import get_settings
from ..email_templates import api_key_created, api_key_revoked

router = APIRouter(prefix="/v1/keys", tags=["keys"])


@router.post("")
async def create_key(
    bg: BackgroundTasks, name: str = "default", user: dict = Depends(current_user),
) -> dict:
    result = await repo.create_api_key(user, name)
    if user.get("email"):
        s = get_settings()
        bg.add_task(email.send, api_key_created(
            to=user["email"], name=user.get("email", "").split("@")[0],
            key_name=name, api_key=result["api_key"], app_url=f"{s.app_public_url}/developer/keys",
        ))
    return result


@router.get("")
async def list_keys(user: dict = Depends(current_user)) -> list[dict]:
    return await repo.list_api_keys(user)


@router.delete("/{key_id}")
async def revoke_key(
    key_id: str, bg: BackgroundTasks, user: dict = Depends(current_user),
) -> dict:
    key_name = await repo.get_key_name(user, key_id) or "a key"
    await repo.revoke_api_key(user, key_id)
    if user.get("email"):
        s = get_settings()
        bg.add_task(email.send, api_key_revoked(
            to=user["email"], name=user.get("email", "").split("@")[0],
            key_name=key_name, app_url=f"{s.app_public_url}/developer/keys",
        ))
    return {"revoked": key_id}
