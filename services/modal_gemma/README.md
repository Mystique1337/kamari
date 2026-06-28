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

## Eval note (important)
The v0 offline eval scored 0 on every metric because it ran through the multimodal Gemma 4
`generate()` path, which has a tensor-shape bug. Those numbers are **not representative**. Serving
uses a manual KV-cached greedy decode instead, and the deployed model returns valid strict-JSON
(verified live). A corrected offline eval is pending. Non-English strings still need native-speaker
review before release.

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
