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


_DEFAULT_EXPLANATIONS = {
    ReasonCode.ALLOW: "Estimated age is comfortably above the limit, with good confidence and photo quality.",
    ReasonCode.BLOCK_LIKELY_MINOR: "The model estimated a high chance of being under 18, so access needs a guardian to approve.",
    ReasonCode.SECONDARY_CHECK_NEAR_THRESHOLD: "The estimate is close to the age limit (the 18 to 21 band), so we ask for one more quick check.",
    ReasonCode.SECONDARY_CHECK_LOW_CONFIDENCE: "The model was not confident enough on this photo, so we ask for a second check.",
    ReasonCode.RECAPTURE_LOW_QUALITY: "We could not read a clear face, so please retake the photo in good light.",
    ReasonCode.RECAPTURE_NO_FACE: "We did not find a clear single face, so please retake the photo.",
    ReasonCode.RECAPTURE_MULTIPLE_FACES: "We saw more than one face, so please retake with just you in frame.",
}


def default_explanation(reason: ReasonCode) -> str:
    return _DEFAULT_EXPLANATIONS.get(reason, "A second check is needed before continuing.")
