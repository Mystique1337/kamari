---
name: kamari-privacy
description: Enforce Kámárí's privacy, consent, child-safety, and responsible-AI posture across every layer. Use whenever handling face images, embeddings, retention, logging, verification, or user-facing age/decision wording. This is cross-cutting, not a single phase.
---

# Kámárí Privacy & Responsible-AI Guardrails

Kámárí processes faces - many of them minors. These rules override convenience anywhere they conflict.

## Default privacy posture (§3.3) - MVP defaults
- **Do not store uploaded face images by default.** Do not store embeddings by default.
- Store only request metadata, model version, decision, and audit logs.
- Temporary processing only, with immediate deletion.
- Retention must be **visible** in API responses (`retention` field) and on app screens.

## Age vs verification separation (§3.2)
- Age estimation answers "how likely under the threshold". Verification answers "does this selfie match this 1 reference".
- **1:1 verification only. Never build 1:N face search.** Embeddings stored encrypted only on explicit opt-in.

## Wording & framing
- Every age result is an **estimate, not a legal age determination** - say so (`safety_note`).
- Be conservative near the boundary; never auto-approve borderline cases.
- Gemma/UI choose only from the fixed decision-code list; never invent codes or certainty.

## Data governance (ties to kamari-data-benchmark)
- No raw minor faces in public buckets or on Hugging Face.
- Commercial child datasets require signed licence + DPA + parental-consent proof + ethics approval - otherwise exclude.
- Report fairness by skin band / ITA / race hint / age band / gender; surface known limitations honestly.

## Surveillance avoidance & compliance
- Keep verification consent explicit and scoped. Clear privacy policy, consent flow, retention, and child-safety wording for app-store review.
- Phase 9 hardening: security review + privacy review before any demo/release.

When a change would store an image/embedding by default, broaden verification beyond 1:1, weaken consent, or hide retention - stop and flag it to the user.
