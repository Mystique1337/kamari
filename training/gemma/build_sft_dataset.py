"""Build the Gemma SFT dataset from the policy engine - NOT from raw child faces.

Generates strict-JSON instruction/input/output rows by sampling CNN-style signals,
running the same decision rules as the gateway, and rendering approved explanation
templates per language. Native-speaker review is still required for non-English strings.

Usage:
    python training/gemma/build_sft_dataset.py --n 4000 --out training/gemma/sft_train.jsonl
"""
from __future__ import annotations

import argparse
import json
import random

LANGUAGES = ["en", "sw", "yo", "ha", "am", "fr", "ar"]

# Approved user-facing templates per (reason_code, language). English is the control;
# other languages are seeded here and MUST be reviewed by native speakers before release.
USER_MSG = {
    "ALLOW": {
        "en": "You’re verified. Welcome in.",
        "sw": "Umethibitishwa. Karibu.",
        "yo": "A ti fọwọ́ sí ọ. Káàbọ̀.",
        "ha": "An tabbatar da kai. Barka da zuwa.",
        "am": "ተረጋግጧል። እንኳን ደህና መጡ።",
        "fr": "Vous êtes vérifié. Bienvenue.",
        "ar": "تم التحقق منك. مرحبًا بك.",
    },
    "SECONDARY_CHECK_NEAR_THRESHOLD": {
        "en": "You’re close to the age limit, so we need one more quick check.",
        "sw": "Uko karibu na kikomo cha umri, tunahitaji ukaguzi mmoja zaidi.",
        "yo": "O wà nítòsí òpin ọjọ́-orí, a nílò àyẹ̀wò kan sí i.",
        "ha": "Kana kusa da iyakar shekaru, muna bukatar ƙarin bincike.",
        "am": "ከእድሜ ገደቡ ቅርብ ነዎት፣ ተጨማሪ ማረጋገጫ ያስፈልጋል።",
        "fr": "Vous êtes proche de la limite d’âge, une vérification supplémentaire est nécessaire.",
        "ar": "أنت قريب من حد العمر، نحتاج إلى فحص إضافي.",
    },
    "BLOCK_LIKELY_MINOR": {
        "en": "We can’t confirm you meet the age requirement. A guardian check is needed.",
        "sw": "Hatuwezi kuthibitisha umri wako. Ukaguzi wa mlezi unahitajika.",
        "yo": "A kò lè jẹ́rìí ọjọ́-orí rẹ. A nílò àyẹ̀wò alámòjútó.",
        "ha": "Ba za mu iya tabbatar da shekarunka ba. Ana buƙatar binciken mai kula.",
        "am": "እድሜዎን ማረጋገጥ አልቻልንም። የአሳዳጊ ማረጋገጫ ያስፈልጋል።",
        "fr": "Nous ne pouvons pas confirmer votre âge. Une vérification par un tuteur est requise.",
        "ar": "لا يمكننا تأكيد عمرك. يلزم تحقق من ولي الأمر.",
    },
    "RECAPTURE_LOW_QUALITY": {
        "en": "The photo was unclear - let’s try once more in better light.",
        "sw": "Picha haikuwa wazi - jaribu tena kwenye mwanga bora.",
        "yo": "Àwòrán náà kò ṣe kedere - jọ̀wọ́ tún gbìyànjú nínú ìmọ́lẹ̀ tó dára.",
        "ha": "Hoton bai bayyana ba - gwada sake a cikin haske mai kyau.",
        "am": "ፎቶው ግልጽ አልነበረም - እባክዎ በተሻለ ብርሃን እንደገና ይሞክሩ።",
        "fr": "La photo n’était pas nette - réessayons avec une meilleure lumière.",
        "ar": "الصورة لم تكن واضحة - لنحاول مرة أخرى في إضاءة أفضل.",
    },
}
USER_MSG["SECONDARY_CHECK_LOW_CONFIDENCE"] = USER_MSG["SECONDARY_CHECK_NEAR_THRESHOLD"]

NEXT_STEP = {
    "ALLOW": "proceed",
    "SECONDARY_CHECK_NEAR_THRESHOLD": "request_id_or_guardian_flow",
    "SECONDARY_CHECK_LOW_CONFIDENCE": "request_id_or_guardian_flow",
    "BLOCK_LIKELY_MINOR": "request_id_or_guardian_flow",
    "RECAPTURE_LOW_QUALITY": "retake_photo",
}
DECISION = {
    "ALLOW": "allow",
    "SECONDARY_CHECK_NEAR_THRESHOLD": "secondary_check",
    "SECONDARY_CHECK_LOW_CONFIDENCE": "secondary_check",
    "BLOCK_LIKELY_MINOR": "block",
    "RECAPTURE_LOW_QUALITY": "recapture",
}
SAFETY_NOTE = "This is an estimate, not a legal age determination."
ADMIN = {
    "ALLOW": "Clear adult estimate; auto-approved.",
    "SECONDARY_CHECK_NEAR_THRESHOLD": "Estimate near the threshold; do not auto-approve.",
    "SECONDARY_CHECK_LOW_CONFIDENCE": "Low confidence; require secondary verification.",
    "BLOCK_LIKELY_MINOR": "High under-18 probability; route to guardian/ID flow.",
    "RECAPTURE_LOW_QUALITY": "Low image quality; request a retake.",
}


def decide(p_under_18, estimated_age, uncertainty, quality,
           block=0.70, challenge=21, unc_thr=0.28, min_q=0.40) -> str:
    """Mirror of the gateway policy engine (master plan §10.4)."""
    if quality < min_q:
        return "RECAPTURE_LOW_QUALITY"
    if p_under_18 >= block:
        return "BLOCK_LIKELY_MINOR"
    if estimated_age < challenge:
        return "SECONDARY_CHECK_NEAR_THRESHOLD"
    if uncertainty > unc_thr:
        return "SECONDARY_CHECK_LOW_CONFIDENCE"
    return "ALLOW"


def sample_row(rng: random.Random) -> dict:
    age = round(rng.uniform(12, 30), 1)
    p_under = round(max(0.0, min(1.0, (19 - age) / 8 + rng.uniform(-0.05, 0.1))), 2)
    uncertainty = round(rng.uniform(0.05, 0.4), 2)
    quality = round(rng.uniform(0.25, 1.0), 2)
    country = rng.choice(["NG", "KE", "GH", "ET", "ZA", "SN"])
    language = rng.choice(LANGUAGES)
    reason = decide(p_under, age, uncertainty, quality)
    msg = USER_MSG[reason].get(language, USER_MSG[reason]["en"])
    return {
        "instruction": "Return a safe age-gating explanation as strict JSON matching the Kámárí schema.",
        "input": {
            "estimated_age": age, "p_under_18": p_under, "uncertainty": uncertainty,
            "face_quality": quality, "country": country, "language": language,
            "legal_threshold": 18, "challenge_threshold": 21,
        },
        "output": {
            "decision": DECISION[reason], "reason_code": reason, "user_message": msg,
            "admin_summary": ADMIN[reason], "next_step": NEXT_STEP[reason],
            "language": language, "safety_note": SAFETY_NOTE,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--out", default="training/gemma/sft_train.jsonl")
    ap.add_argument("--eval-out", default="training/gemma/sft_eval.jsonl")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    # Balance across reason codes (random sampling skews to ALLOW); balanced labels +
    # uniform languages give the adapter even coverage -> better schema/policy accuracy.
    from collections import defaultdict
    pool = [sample_row(rng) for _ in range(args.n * 6)]
    by_reason = defaultdict(list)
    for r in pool:
        by_reason[r["output"]["reason_code"]].append(r)
    per = max(1, args.n // len(by_reason))
    balanced = []
    for reason, items in by_reason.items():
        rng.shuffle(items)
        while len(items) < per:
            items = items + items
        balanced += items[:per]
    rng.shuffle(balanced)
    print("reason-code balance:", {k: len(v) for k, v in by_reason.items()})
    print("balanced rows:", len(balanced))

    split = int(len(balanced) * 0.9)
    for path, chunk in [(args.out, balanced[:split]), (args.eval_out, balanced[split:])]:
        with open(path, "w", encoding="utf-8") as fh:
            for r in chunk:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"wrote {len(chunk)} -> {path}")


if __name__ == "__main__":
    main()
