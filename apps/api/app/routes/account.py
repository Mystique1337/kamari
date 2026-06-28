"""Account lifecycle. Welcome email after signup (GoTrue-protected)."""
from fastapi import APIRouter, BackgroundTasks, Depends

from .. import email
from ..auth.gotrue import current_user
from ..config import get_settings
from ..email_templates import welcome

router = APIRouter(prefix="/v1/account", tags=["account"])


@router.post("/welcome")
async def send_welcome(bg: BackgroundTasks, user: dict = Depends(current_user)) -> dict:
    if user.get("email"):
        s = get_settings()
        bg.add_task(email.send, welcome(
            to=user["email"], name=user.get("email", "").split("@")[0],
            app_url=s.app_public_url,
        ))
        return {"sent": True}
    return {"sent": False}
