# Kámárí CNN (Modal)

Small multi-head age-gating model. **Training** reads private crops from a Modal Volume;
**serving** loads the licence-clean ONNX from Hugging Face.

## Artifacts
| File | Role |
|---|---|
| `train_cnn.py` | Modal training: **HF data** → train → eval → **W&B** → push `cnn-age-v0` |
| `serve_cnn.py` | Modal serving: ONNX endpoint → raw age signals |

## Train
Backbone **EfficientNetV2-S** (configurable). Reads the dataset from HF `kamari-faces-v0`,
checkpoints every epoch to the `kamari-cnn` Volume (resumable), tracks in **W&B**, and
uploads **best.pt + ONNX + thresholds + metrics + training log + benchmark/latency reports
+ card** back to HF. Model selection is **safety-weighted** (MAE + heavy Minor-Pass-Through).
```bash
modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=... WANDB_API_KEY=... WANDB_PROJECT=kamari
modal run services/modal_age/train_cnn.py --epochs 30
```
GPU defaults to **H200** (`export KAMARI_GPU=H100` to change). Sampling = inverse-freq over
(age-band × skin-band) + 13–21 boost + dark-skin boost. Eval = MAE overall + by
skin/age/dataset/gender, **MPTR@18/@21 (incl. dark-skin)**, Adult-Block, latency p50/p95.

## Serve
```bash
modal deploy services/modal_age/serve_cnn.py
# -> set the printed URL as MODAL_AGE_ENDPOINT in apps/api
curl -F image=@selfie.jpg https://<...>/estimate
```

## Output (raw signals — policy lives in the gateway)
```json
{ "estimated_age": 17.4, "p_under_18": 0.76, "uncertainty": 0.18,
  "face_quality": 0.93, "model_version": "cnn_v0.1.0" }
```

## Notes
- Training crops are never published (licence/consent). The ONNX + thresholds + reports are.
- Resumable: re-running `modal run` continues from `last.pt` in the `kamari-cnn` Volume.
- Estimate only — not a legal age determination.
