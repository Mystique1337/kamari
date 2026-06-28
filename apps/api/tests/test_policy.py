"""Policy engine tests — the safety-critical core. Borderline never auto-approves."""
from app.config import Settings
from app.policy import age_band, decide
from app.schemas.age import Decision, ReasonCode

S = Settings()


def test_low_quality_recaptures():
    d, r = decide(p_under_18=0.1, estimated_age=30, uncertainty=0.1, face_quality=0.2, s=S)
    assert d == Decision.recapture and r == ReasonCode.RECAPTURE_LOW_QUALITY


def test_high_p_under_blocks():
    d, r = decide(p_under_18=0.85, estimated_age=16, uncertainty=0.1, face_quality=0.9, s=S)
    assert d == Decision.block and r == ReasonCode.BLOCK_LIKELY_MINOR


def test_near_threshold_secondary():
    d, r = decide(p_under_18=0.2, estimated_age=19.5, uncertainty=0.1, face_quality=0.9, s=S)
    assert d == Decision.secondary_check and r == ReasonCode.SECONDARY_CHECK_NEAR_THRESHOLD


def test_low_confidence_secondary():
    d, r = decide(p_under_18=0.2, estimated_age=30, uncertainty=0.4, face_quality=0.9, s=S)
    assert d == Decision.secondary_check and r == ReasonCode.SECONDARY_CHECK_LOW_CONFIDENCE


def test_clear_adult_allows():
    d, r = decide(p_under_18=0.05, estimated_age=35, uncertainty=0.1, face_quality=0.95, s=S)
    assert d == Decision.allow and r == ReasonCode.ALLOW


def test_age_band():
    assert age_band(16) == "16-17"
    assert age_band(19) == "18-20"
