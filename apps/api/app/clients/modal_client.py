"""Clients for the Modal CNN + Gemma endpoints, with safe fallbacks.

If an endpoint is unconfigured (dev), a deterministic mock keeps the gateway runnable
end-to-end without the models — mirroring the app's mock so the contract is exercised.
"""
import random

import httpx

from ..config import Settings
from ..schemas.age import CnnSignals


async def cnn_estimate(image_bytes: bytes, filename: str, s: Settings) -> CnnSignals:
    if not s.modal_age_endpoint:
        return _mock_cnn()
    async with httpx.AsyncClient(timeout=180) as client:
        resp = await client.post(
            s.modal_age_endpoint,
            files={"image": (filename or "selfie.jpg", image_bytes, "image/jpeg")},
        )
        resp.raise_for_status()
        return CnnSignals(**resp.json())


async def gemma_explain(cnn_result: dict, policy_context: dict, language: str, s: Settings) -> dict | None:
    """Return a Gemma explanation dict, or None to fall back to default messages."""
    if not s.modal_gemma_endpoint or not s.use_gemma_message:
        return None
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            resp = await client.post(
                s.modal_gemma_endpoint,
                json={"cnn_result": cnn_result, "policy_context": policy_context, "language": language},
            )
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None  # gateway degrades gracefully to template messages


def _mock_cnn() -> CnnSignals:
    age = round(13 + random.random() * 14, 1)
    p_under = round(max(0.0, min(1.0, (19 - age) / 8 + random.random() * 0.1)), 3)
    return CnnSignals(
        estimated_age=age,
        p_under_18=p_under,
        uncertainty=round(0.1 + random.random() * 0.25, 3),
        face_quality=round(0.7 + random.random() * 0.3, 3),
        model_version="cnn_v0-mock",
    )
