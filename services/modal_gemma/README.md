# Kámárí Gemma explanation layer (Modal)

Turns CNN + policy signals into safe, multilingual, **strict-JSON** explanations. Gemma explains a
decision; it never estimates age and never invents a reason code.

## Model
- Base `google/gemma-4-E4B-it`, QLoRA (4-bit nf4, double quant), LoRA r=32, alpha 64,
  `target_modules="all-linear"` (Gemma 4 wraps projections in a clippable-linear layer that named
  targets cannot reach).
- SFT data is synthesized from the policy engine, not from child faces: sampled signals run through
  the same `decide()` rules, and approved per-reason, per-language templates render the message. The
  set is reason-code balanced across languages (8,000 rows, 7,200 train / 800 eval).
- Output schema: `decision, reason_code, user_message, admin_summary, next_step, language,
  safety_note` (`training/gemma/output_schema.json`).

Full method: [`docs/methodology.md`](../../docs/methodology.md).

## Eval
Training loss converged from 3.00 to 0.087. Evaluated through the served endpoint (the manual decode
used in production) over n=70 cases across 5 reason codes and 7 languages: JSON validity 1.00, schema
compliance 1.00, decision consistency 1.00, policy consistency 1.00, language correctness 1.00,
invented-code rate 0.00. The endpoint validates and falls back to an approved template on any failure,
so the system always returns valid, schema-correct, policy-consistent JSON. (An earlier eval showed
0.0 because it used the buggy `generate()` path; superseded.) Non-English strings still benefit from a
native review.

## Train
```bash
modal run services/modal_gemma/train_gemma.py --n 8000     # or modal run --detach
```
3 epochs on H200, effective batch 32, lr 2e-4, max length 512, gradient checkpointing, NEFTune.
Pushes the adapter, `metrics_v0.json`, and an eval report to `Shinzmann/gemma-explain-lora-v0`.

## Serve (GPU L4, always-on)
```bash
modal deploy services/modal_gemma/serve_gemma.py
# -> set the printed URL as MODAL_GEMMA_ENDPOINT in the gateway
```
- Loads base Gemma 4 + adapter, merges, runs the manual greedy decode (avoids the `generate()` bug).
- On any validation failure, returns a deterministic safe fallback so the gateway always gets valid
  JSON.
- `min_containers=1` keeps a warm GPU (4B + adapter fits L4 24 GB);
  `KAMARI_GEMMA_MIN_CONTAINERS=0` to scale to zero.

Request: `{cnn_result, policy_context:{decision, reason_code, legal_threshold, challenge_threshold},
language}`. Endpoint `POST /explain`.
