"""Developer API-key management (JWT-protected) — stored hashed in kamari.api_keys."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .. import repo
from ..auth.models import User
from ..auth.users import current_active_user
from ..db import get_async_session

router = APIRouter(prefix="/v1/keys", tags=["keys"])


@router.post("")
async def create_key(name: str = "default",
                     session: AsyncSession = Depends(get_async_session),
                     user: User = Depends(current_active_user)) -> dict:
    return await repo.create_api_key(session, user, name)


@router.get("")
async def list_keys(session: AsyncSession = Depends(get_async_session),
                    user: User = Depends(current_active_user)) -> list[dict]:
    return await repo.list_api_keys(session, user)


@router.delete("/{key_id}")
async def revoke_key(key_id: str,
                     session: AsyncSession = Depends(get_async_session),
                     user: User = Depends(current_active_user)) -> dict:
    await repo.revoke_api_key(session, user, key_id)
    return {"revoked": key_id}
