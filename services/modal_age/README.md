# Kámárí CNN age model (Modal)

![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white) ![Modal](https://img.shields.io/badge/serve-Modal-7C3AED) ![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97-cnn--age--v0-ffcc4d) [![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](../../LICENSE)

*Part of the [Kámárí](../../README.md) monorepo.*

Trains the age-gating CNN on Modal (H200) from the Hugging Face dataset, and serves it on CPU with
face detection and crop. Returns raw signals only; the policy/decision engine lives in the gateway.

## Model
- Backbone EfficientNetV2-S (`tf_efficientnetv2_s`), ImageNet-pretrained.
- Three heads: age regression, under-18 logit, heteroscedastic uncertainty (log-variance).
- Loss: heteroscedastic Gaussian NLL (age) + BCE (minor head).
- Composite sampling over age-band x skin-band, with a 3x boost for ages 13 to 21 and 1.5x for brown
  and dark skin. Selection minimizes `MAE + 5 x MPTR@18`.

Full method: [`docs/methodology.md`](../../docs/methodology.md).

## Results (v0, held-out benchmark n=8,322)
| Metric | Value |
|---|---|
| MAE | 6.03 years |
| MPTR@18 | 0.317 |
| MPTR@18 (dark + brown skin) | 0.383 |
| MPTR@21 | 0.27 |
| Adult-block rate | 0.01 |
| MAE dark / light skin | 6.58 / 5.72 |
| Validation MAE / MPTR@18 | 5.73 / 0.20 |
| GPU eval latency p50 / p95 | 14.2 / 14.3 ms |

MAE is strong but MPTR@18 is high, so this is **not a standalone gate**. The policy engine,
uncertainty routing, liveness, and the guardian flow provide the safety margin. Lowering MPTR needs
more 13 to 17 and African-labelled data.

## Train
```bash
modal run services/modal_age/train_cnn.py            # or modal run --detach for long runs
```
Pulls `Shinzmann/kamari-faces-v0`, trains 30 epochs (H200, batch 512, ~15 min wall-clock),
checkpoints to a Modal Volume (resumable), and pushes `best.pt`, `cnn_v0.onnx`,
`thresholds_v0.json`, `metrics_v0.json`, and reports to `Shinzmann/cnn-age-v0`. W&B logging when
`WANDB_API_KEY` is set (the v0 run is tracked in project `kamari`).

## Serve (CPU, always-on)
```bash
modal deploy services/modal_age/serve_cnn.py
# -> https://<ns>--kamari-cnn-serve-endpoint.modal.run  (set as MODAL_AGE_ENDPOINT)
curl -F image=@selfie.jpg https://.../estimate
```
- Loads the PyTorch `best.pt` (the ONNX external-weights sidecar did not survive the HF download).
- **Detects and crops the largest face** with an OpenCV Haar cascade (30% margin) so inference
  matches the training crops. No face found returns `faces_detected: 0` and quality 0, so the
  gateway asks for a recapture. This is what stops every photo from failing the quality gate.
- `min_containers=1` keeps one warm container so there is no cold start
  (`KAMARI_CNN_MIN_CONTAINERS=0` to scale to zero).

Response: `{estimated_age, p_under_18, uncertainty, face_quality, faces_detected, model_version}`.
