---
license: apache-2.0
base_model: google/gemma-4-E4B-it
library_name: peft
pipeline_tag: text-generation
tags:
  - age-verification
  - explanation
  - lora
  - qlora
  - multilingual
  - africa
---

# Kámárí Gemma Explanation LoRA (v0)

A QLoRA adapter for `google/gemma-4-E4B-it` that turns Kámárí's CNN + policy signals into a safe,
multilingual, **strict-JSON** explanation. **Gemma explains a decision; it never estimates age and
never invents a reason code.**

- LoRA r=32, alpha 64, `target_modules="all-linear"`, 4-bit nf4 QLoRA, 3 epochs on H200.
- Output schema: `decision, reason_code, user_message, admin_summary, next_step, language,
  safety_note`. Reason codes come from a fixed list.

## Intended use
Input: `{cnn_result, policy_context:{decision, reason_code, legal_threshold, challenge_threshold},
language}`. Output: one strict-JSON object with the message in the requested language. Languages in
the SFT set: en, sw, yo, ha, am, fr, ar (more in the app picker). Non-English strings should get
native-speaker review before release.

## Training data
Synthesized from the Kámárí policy engine, not from child faces: sampled signals run through the same
`decide()` rules, and approved per-reason, per-language templates render the message. The set is
reason-code balanced (so it is not dominated by ALLOW): 8,000 rows, 7,200 train / 800 eval.

## Evaluation note (read this)
The v0 offline eval scored **0 on every metric**. That is not the model: the eval ran through the
multimodal Gemma 4 `generate()` path, which has a tensor-shape bug, so it produced no valid output.
**Serving uses a manual KV-cached greedy decode instead, and the deployed model returns valid
strict-JSON (verified live).** A corrected offline eval is pending. Treat the stored `metrics_v0.json`
eval block as a known-broken harness, not a result.

## Serving
Load base Gemma 4 + this adapter, `merge_and_unload()`, and decode greedily token by token (avoid
`generate()`). On any validation failure, return a deterministic safe fallback so the caller always
gets valid JSON. Served on a Modal L4 GPU, always-on.

Methodology: https://github.com/Mystique1337/kamari/blob/main/docs/methodology.md

## License
Apache-2.0. Every output carries: this is an estimate, not a legal age determination.
