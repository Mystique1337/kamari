# Kámárí CNN (Modal)

Small multi-head age-gating model. **Training** reads private crops from a Modal Volume;
**serving** loads the licence-clean ONNX from Hugging Face.

## Artifacts
| File | Role |
|---|---|
| `train_cnn.py` | Modal training: data → train → ONNX → push `cnn-age-v0` |
| `serve_cnn.py` | Modal serving: ONNX endpoint → raw age signals |

## Train
```bash
modal secret create kamari-hf HF_TOKEN=... HF_NAMESPACE=...
modal volume create kamari-data
modal volume put kamari-data data/manifests/manifest_train_v0.parquet manifest_train_v0.parquet
modal volume put kamari-data data/processed/crops_224 crops_224
modal run services/modal_age/train_cnn.py --epochs 20
```
GPU defaults to `A100-80GB` (`export KAMARI_GPU=H100` for fastest).

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
- Training crops are never published (licence/consent). The ONNX + thresholds are.
- The 13–21 boundary is oversampled 3×. Thresholds ship in `thresholds_v0.json`.
- Estimate only — not a legal age determination.
