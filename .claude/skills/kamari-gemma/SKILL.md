---
name: kamari-gemma
description: Build the Gemma explanation/policy layer in training/gemma and services/modal_gemma. Use for LoRA/QLoRA fine-tuning, SFT dataset construction, strict-JSON schema output, multilingual eval, and Modal serving. Gemma explains decisions; it never estimates age.
---

# Kámárí Gemma - explanation & policy layer

Gemma turns CNN + policy outputs into safe, consistent, multilingual explanations. It is **not** the age estimator and must **not** invent decision codes.

## Strategy (§9)
- Model: Gemma small/efficient variant (E2B/E4B for prod; 12B for GPU demo). LoRA/QLoRA, never full fine-tune.
- JSON-schema-constrained output. Modal endpoint for inference.
- Fine-tune on **structured decision examples** (CNN output + threshold policy + country/language + reason codes + approved templates + edge cases) - not raw child faces.

## I/O contract
Input: `estimated_age, p_under_18, uncertainty, face_quality, country, legal_threshold, challenge_threshold, language, policy_context`.
Output (strict JSON): `decision, reason_code, user_message, admin_summary, next_step, language, safety_note`.
`safety_note` always conveys "estimate, not a legal age determination". `reason_code` ∈ the fixed list (see kamari-api / §21).

## Files
`training/gemma/{build_sft_dataset.py, train_lora.py, eval_schema.py, eval_policy.py, eval_languages.py, merge_adapter.py}`, `sft_train.jsonl`, `sft_eval.jsonl`, `policy_templates.yaml`, `output_schema.json`.

## Languages v0 (§9.4)
English (control), Swahili, Yoruba, Hausa, Amharic, French, Arabic. Add a language only with reviewed examples + eval coverage; African-language strings need native-speaker review. FLORES-200 / Masakha* for eval, not for age truth.

## Eval (§9.5): JSON validity, schema compliance, decision consistency vs rule engine, unsafe-certainty rate, hallucination rate, language correctness, policy consistency, latency p50/p95, cost/1k.

## Acceptance (§9.6): gemma_lora_adapter/, sft_train.jsonl, sft_eval.jsonl, output_schema.json, schema_eval_report.md, policy_eval_report.md, language_eval_report.md, GEMMA_MODEL_CARD.md, Modal endpoint, HF adapter card.
