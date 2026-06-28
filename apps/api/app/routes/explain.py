"""POST /v1/age/explain - re-render an explanation for a known decision (Gemma)."""
from fastapi import APIRouter, Depends

from ..clients.modal_client import gemma_explain
from ..config import Settings, get_settings
from ..policy import default_message
from ..schemas.age import ReasonCode

router = APIRouter(prefix="/v1/age", tags=["age"])


@router.post("/explain")
async def explain(payload: dict, s: Settings = Depends(get_settings)) -> dict:
    cnn_result = payload.get("cnn_result", {})
    policy_context = payload.get("policy_context", {})
    language = payload.get("language", "en")
    reason = policy_context.get("reason_code", "SECONDARY_CHECK_LOW_CONFIDENCE")

    gemma = await gemma_explain(cnn_result, policy_context, language, s)
    if gemma:
        if gemma.get("user_message"):
            from ..policy import sanitize_message
            gemma["user_message"] = sanitize_message(gemma["user_message"])
        return gemma
    # Fallback so the endpoint always returns valid content.
    return {
        "decision": policy_context.get("decision", "secondary_check"),
        "reason_code": reason,
        "user_message": default_message(ReasonCode(reason)) if reason in ReasonCode.__members__
        else "We need an additional age check before continuing.",
        "language": language,
        "safety_note": "This is an estimate, not a legal age determination.",
    }
