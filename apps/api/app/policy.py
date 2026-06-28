"""The Kámárí decision/policy engine (master plan §10.4).

Conservative near the threshold - borderline cases are NEVER auto-approved.
Pure function so it is trivially unit-tested and identical to the Gemma SFT rules.
"""
from .config import Settings
from .schemas.age import Decision, ReasonCode


def sanitize_message(text: str) -> str:
    """House style: no em or en dashes in any user-facing copy, including model output."""
    if not text:
        return text
    return (text.replace(" — ", ", ").replace(" – ", ", ")
            .replace("—", "-").replace("–", "-"))

_DEFAULT_MESSAGES = {
    ReasonCode.ALLOW: "You’re verified. Welcome in.",
    ReasonCode.BLOCK_LIKELY_MINOR: "We can’t confirm you meet the age requirement. A guardian check is needed.",
    ReasonCode.SECONDARY_CHECK_NEAR_THRESHOLD: "You’re close to the age limit, so we need one more quick check.",
    ReasonCode.SECONDARY_CHECK_LOW_CONFIDENCE: "We’d like a second check to be sure.",
    ReasonCode.RECAPTURE_LOW_QUALITY: "The photo was unclear - let’s try once more in better light.",
}


def age_band(age: float) -> str:
    a = int(age)
    for lo, hi in [(0, 12), (13, 15), (16, 17), (18, 20), (21, 25), (26, 35), (36, 50), (51, 120)]:
        if lo <= a <= hi:
            return f"{lo}-{hi}"
    return "unknown"


def decide(p_under_18: float, estimated_age: float, uncertainty: float,
           face_quality: float, s: Settings) -> tuple[Decision, ReasonCode]:
    if face_quality < s.min_quality:
        return Decision.recapture, ReasonCode.RECAPTURE_LOW_QUALITY
    if p_under_18 >= s.block_p_under_18:
        return Decision.block, ReasonCode.BLOCK_LIKELY_MINOR
    if estimated_age < s.challenge_threshold:
        return Decision.secondary_check, ReasonCode.SECONDARY_CHECK_NEAR_THRESHOLD
    if uncertainty > s.uncertainty_threshold:
        return Decision.secondary_check, ReasonCode.SECONDARY_CHECK_LOW_CONFIDENCE
    return Decision.allow, ReasonCode.ALLOW


def default_message(reason: ReasonCode) -> str:
    return _DEFAULT_MESSAGES.get(reason, "We need an additional age check before continuing.")
