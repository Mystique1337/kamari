"""POST /v1/age/estimate — the core flow: CNN signals -> policy -> (Gemma) message."""
import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile

from ..clients.modal_client import cnn_estimate, gemma_explain
from ..config import Settings, get_settings
from ..policy import age_band, decide, default_message
from ..schemas.age import AgeEstimateResponse, ReasonCode
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

    # Gemma writes the human, multilingual message; fall back to approved templates.
    message = default_message(reason)
    gemma = await gemma_explain(
        signals.model_dump(),
        {"decision": decision.value, "reason_code": reason.value,
         "legal_threshold": s.legal_threshold, "challenge_threshold": s.challenge_threshold},
        language, s,
    )
    if gemma and gemma.get("reason_code") == reason.value and gemma.get("user_message"):
        message = gemma["user_message"]

    # NB: image_bytes is never persisted (retention default = no-store).
    return AgeEstimateResponse(
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
        retention=s.retention_default,
    )
