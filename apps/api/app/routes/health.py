"""GET /v1/health and GET /v1/models."""
from fastapi import APIRouter, Depends

from ..config import Settings, get_settings

router = APIRouter(prefix="/v1", tags=["meta"])


@router.get("/health")
async def health(s: Settings = Depends(get_settings)) -> dict:
    return {
        "status": "ok",
        "age_endpoint": "configured" if s.modal_age_endpoint else "mock",
        "gemma_endpoint": "configured" if s.modal_gemma_endpoint else "off/mock",
        "retention_default": s.retention_default,
    }


@router.get("/models")
async def models() -> dict:
    return {
        "models": [
            {"type": "cnn_age", "version": "cnn_v0.1.0", "hf_repo": "cnn-age-v0"},
            {"type": "gemma_explain", "version": "lora_v0", "hf_repo": "gemma-explain-lora-v0"},
        ]
    }
