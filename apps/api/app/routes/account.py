"""Account lifecycle. Welcome email on signup, delivered via n8n (not Supabase SMTP).

Public by design: the app calls this right after Supabase signup with the new email, so the
welcome arrives even when email confirmation is on (no session yet). Lightly rate limited and
email-validated to limit abuse.
"""
import re
import time

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from .. import email
from ..config import get_settings
from ..email_templates import welcome

router = APIRouter(prefix="/v1/account", tags=["account"])

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_recent: list[float] = []  # timestamps for a simple global rate limit


class WelcomeReq(BaseModel):
    email: str
    name: str | None = None


@router.post("/welcome")
async def send_welcome(body: WelcomeReq, bg: BackgroundTasks) -> dict:
    addr = (body.email or "").strip().lower()
    if not _EMAIL_RE.match(addr):
        return {"sent": False, "reason": "invalid email"}
    now = time.time()
    global _recent
    _recent = [t for t in _recent if now - t < 60]
    if len(_recent) >= 30:  # cap welcomes at 30/min across the service
        return {"sent": False, "reason": "rate_limited"}
    _recent.append(now)
    s = get_settings()
    name = body.name or addr.split("@")[0]
    bg.add_task(email.send, welcome(to=addr, name=name, app_url=s.app_public_url))
    return {"sent": True}
