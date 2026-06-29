"""POST /v1/age/estimate - the core flow: CNN signals -> policy -> (Gemma) message."""
import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile

from ..clients.modal_client import cnn_estimate, gemma_explain
from ..config import Settings, get_settings
from ..policy import (
    age_band, decide, default_explanation, default_message, sanitize_message,
)
from ..schemas.age import AgeEstimateResponse, Explanation, ReasonCode
from ..security.api_keys import require_key

router = APIRouter(prefix="/v1/age", tags=["age"])


@router.post("/estimate", response_model=AgeEstimateResponse)
async def estimate(
    image: UploadFile = File(...),
    language: str = Form("en"),
    country: str = Form("NG"),
    s: Settings = Depends(get_settings),
    _key: str | None = Depends(require_key),
) -> AgeEstimateResponse:
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    image_bytes = await image.read()

    signals = await cnn_estimate(image_bytes, image.filename or "selfie.jpg", s)
    decision, reason = decide(
        signals.p_under_18, signals.estimated_age, signals.uncertainty, signals.face_quality, s,
    )

    # Gemma writes the human, multilingual message and its reasoning; fall back to
    # approved templates (and a static explanation) when the model is unavailable.
    message = default_message(reason)
    explanation = Explanation(
        source="template",
        summary=default_explanation(reason),
        safety_note="This is an estimate, not a legal age determination.",
    )
    gemma = await gemma_explain(
        signals.model_dump(),
        {"decision": decision.value, "reason_code": reason.value,
         "legal_threshold": s.legal_threshold, "challenge_threshold": s.challenge_threshold},
        language, s,
    )
    if gemma and gemma.get("reason_code") == reason.value and gemma.get("user_message"):
        message = gemma["user_message"]
        explanation = Explanation(
            source="model",
            model_version="gemma-explain-lora-v0",
            summary=sanitize_message(gemma.get("admin_summary")) or default_explanation(reason),
            next_step=gemma.get("next_step"),
            safety_note=sanitize_message(gemma.get("safety_note")) or explanation.safety_note,
        )
    message = sanitize_message(message)

    # NB: image_bytes is never persisted (retention default = no-store).
    resp = AgeEstimateResponse(
        request_id=request_id,
        model_version=signals.model_version,
        estimated_age=signals.estimated_age,
        age_band=age_band(signals.estimated_age),
        p_under_18=signals.p_under_18,
        uncertainty=signals.uncertainty,
        face_quality=signals.face_quality,
        decision=decision,
        reason_code=ReasonCode(reason),
        message=message,
        explanation=explanation,
        retention=s.retention_default,
    )
    # Audit log: metadata only, never the image. Best-effort (no-op without DATABASE_URL).
    from .. import repo
    await repo.log_inference({
        "request_id": request_id, "endpoint": "/v1/age/estimate",
        "model_version": resp.model_version, "decision": resp.decision.value,
        "reason_code": resp.reason_code.value, "face_quality": resp.face_quality,
        "estimated_age": resp.estimated_age, "p_under_18": resp.p_under_18,
        "uncertainty": resp.uncertainty, "retention": resp.retention,
        "organization_id": _key,  # set when called with an API key; scopes usage analytics
    })
    return resp
