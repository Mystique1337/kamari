"""Guardian consent flow for likely-minors.

When the age check blocks or flags a likely minor, the app can ask for a guardian to
review. We email a one-time code via n8n, then verify it. Sessions live in memory with a
short TTL: no guardian PII is persisted. (For multi-instance deploys, back this with a
short-lived table or cache; documented in the API README.)
"""
import secrets
import time

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from .. import email
from ..config import get_settings
from ..email_templates import guardian_consent

router = APIRouter(prefix="/v1/guardian", tags=["guardian"])

_TTL_SECONDS = 15 * 60
_sessions: dict[str, dict] = {}


def _prune() -> None:
    now = time.time()
    for sid in [k for k, v in _sessions.items() if v["expires"] < now]:
        _sessions.pop(sid, None)


class GuardianRequest(BaseModel):
    guardian_email: str
    guardian_name: str = ""
    app_name: str = "an app"


class GuardianVerify(BaseModel):
    session_id: str
    code: str


@router.post("/request")
async def request_consent(body: GuardianRequest, bg: BackgroundTasks) -> dict:
    _prune()
    s = get_settings()
    session_id = "gd_" + secrets.token_urlsafe(16)
    code = f"{secrets.randbelow(1_000_000):06d}"
    _sessions[session_id] = {
        "code": code, "approved": False, "expires": time.time() + _TTL_SECONDS,
    }
    consent_url = f"{s.app_public_url}/guardian?session={session_id}"
    bg.add_task(email.send, guardian_consent(
        to=body.guardian_email, guardian_name=body.guardian_name,
        consent_url=consent_url, code=code, app_name=body.app_name,
    ))
    # Never return the code to the requester; it goes only to the guardian's inbox.
    return {"session_id": session_id, "expires_in": _TTL_SECONDS}


@router.post("/verify")
async def verify_consent(body: GuardianVerify) -> dict:
    _prune()
    sess = _sessions.get(body.session_id)
    if not sess:
        raise HTTPException(404, "session not found or expired")
    if sess["expires"] < time.time():
        _sessions.pop(body.session_id, None)
        raise HTTPException(410, "consent code expired")
    if body.code.strip() != sess["code"]:
        raise HTTPException(401, "incorrect code")
    sess["approved"] = True
    return {"approved": True}


@router.get("/status/{session_id}")
async def status(session_id: str) -> dict:
    _prune()
    sess = _sessions.get(session_id)
    if not sess:
        return {"approved": False, "found": False}
    return {"approved": sess["approved"], "found": True}
