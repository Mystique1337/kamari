# Kámárí CNN (Modal)

Small, multi-head age-gating model. **Training** pulls the dataset from Hugging Face;
**serving** loads the licence-clean **ONNX on CPU** (no GPU needed to host).

## Trained model — `Shinzmann/cnn-age-v0`
- Model: https://huggingface.co/Shinzmann/cnn-age-v0  ·  backbone `tf_efficientnetv2_s`, 30 epochs (H200)
- Benchmark (held-out, n=8,322): **MAE 6.03 yrs** · MPTR@18 **0.317** (dark-skin **0.383**) ·
  MPTR@21 0.27 · Adult-Block 0.01 · MAE dark-skin 6.58 / light 5.72
- Artifacts: `best.pt`, **`cnn_v0.onnx`** (CPU serving), `thresholds_v0.json`, `metrics_v0.json`,
  `training_log.jsonl`, `benchmark_age_report_v0.md`, `latency_report_v0.md`
- **Note:** MAE is strong; MPTR@18 is still high, so the model is **not a standalone gate** —
  the policy engine + secondary checks + uncertainty provide the safety margin. Lowering MPTR
  needs more 13–17 and African-labelled data.

## Artifacts (code)
| File | Role |
|---|---|
| `train_cnn.py` | Modal training: **HF data** → train → full subgroup/latency eval → **W&B** → push `cnn-age-v0` |
| `serve_cnn.py` | Modal serving: **ONNX on CPU** → raw age signals |

## Train
Backbone `tf_efficientnetv2_s` (configurable). Reads `Shinzmann/kamari-faces-v0`, **auto-gates
bad/categorical-age datasets**, composite-samples (age-band × skin-band + 13–21 boost +
dark-skin boost), checkpoints each epoch to the `kamari-cnn` Volume (resumable), tracks in **W&B**.
```bash
modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=Shinzmann WANDB_API_KEY=... WANDB_PROJECT=kamari
modal run --detach services/modal_age/train_cnn.py --epochs 30    # --detach survives client drops
```
GPU defaults to **H200** (`KAMARI_GPU` to change). Optional `KAMARI_TRUSTED_AGE_DATASETS` to pin
an exact-age allowlist; `KAMARI_BENCH_MAX` caps benchmark eval size.

## Serve (CPU)
```bash
modal deploy services/modal_age/serve_cnn.py     # CPUExecutionProvider — cheap, ~14 ms/req
# -> set the printed URL as MODAL_AGE_ENDPOINT in apps/api
curl -F image=@selfie.jpg https://<...>/estimate
```

## Output (raw signals — policy lives in the gateway)
```json
{ "estimated_age": 17.4, "p_under_18": 0.76, "uncertainty": 0.18,
  "face_quality": 0.93, "model_version": "cnn_v0.1.0" }
```

## Notes
- Training crops are never published publicly; the ONNX + thresholds + reports are.
- Resumable: re-running `modal run` continues from `last.pt` in the `kamari-cnn` Volume.
- Estimate only — not a legal age determination.
