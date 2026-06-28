"""Age API schemas - the contract the app (apps/kamari_app) depends on (plan §20/§21)."""
from enum import Enum

from pydantic import BaseModel, Field


class Decision(str, Enum):
    allow = "allow"
    block = "block"
    secondary_check = "secondary_check"
    recapture = "recapture"


class ReasonCode(str, Enum):
    ALLOW = "ALLOW"
    BLOCK_LIKELY_MINOR = "BLOCK_LIKELY_MINOR"
    SECONDARY_CHECK_NEAR_THRESHOLD = "SECONDARY_CHECK_NEAR_THRESHOLD"
    SECONDARY_CHECK_LOW_CONFIDENCE = "SECONDARY_CHECK_LOW_CONFIDENCE"
    RECAPTURE_LOW_QUALITY = "RECAPTURE_LOW_QUALITY"
    RECAPTURE_NO_FACE = "RECAPTURE_NO_FACE"
    RECAPTURE_MULTIPLE_FACES = "RECAPTURE_MULTIPLE_FACES"
    ERROR_UNSUPPORTED_IMAGE = "ERROR_UNSUPPORTED_IMAGE"


class CnnSignals(BaseModel):
    estimated_age: float
    p_under_18: float
    uncertainty: float
    face_quality: float
    model_version: str = "cnn_v0.1.0"


class AgeEstimateResponse(BaseModel):
    request_id: str
    model_version: str
    estimated_age: float
    age_band: str
    p_under_18: float
    uncertainty: float
    face_quality: float
    decision: Decision
    reason_code: ReasonCode
    message: str
    retention: str


class ErrorResponse(BaseModel):
    request_id: str
    error: str = Field(..., description="machine-readable error code")
    detail: str
