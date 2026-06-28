---
name: kamari-cnn
description: Train, calibrate, export, and benchmark the Kámárí small CNN age-gating model in training/cnn. Use for PyTorch model design, augmentation, calibration, ONNX/TFLite export, and Modal serving of the age estimator.
---

# Kámárí CNN - small age-gating model

The CNN is the **biometric age estimator** (not Gemma). Fast, calibratable, exportable, on-device-capable later.

## Architecture (§8 / recommendation)
- Backbone: `tf_efficientnetv2_b0` or `mobilenetv3` via `timm`. Input 224×224 aligned face crop.
- Heads: age-distribution · exact-age regression · under-18 binary · uncertainty/calibration.
- Losses: SmoothL1 (exact age) · focal/BCE (under-18) · optional ordinal age-band (bracket-only data).
- Exports: PyTorch `.pt` → ONNX → TFLite.

Outputs per inference: `estimated_age, age_distribution, age_band, p_under_18, uncertainty, face_quality?`.

## Training order (§8.3)
1. Exact-age datasets → 2. add bracketed (auxiliary only) → 3. **oversample ages 13-21** → 4. add African-domain → 5. eval on frozen Kámárí-Safe Open v0 → 6. calibrate thresholds → 7. export ONNX/TFLite → 8. register in Supabase `model_versions` → 9. publish HF model card.

## Augmentation discipline (§8.4)
ALLOWED: flip, small rotation, small crop/scale, brightness/contrast/gamma, low light, motion/defocus blur, Gaussian noise, JPEG compression, up/downscale.
**FORBIDDEN: hue/saturation shifts, grayscale, channel shuffle, skin recoloring, heavy facial warping, synthetic children as benchmark truth.** These corrupt the age/skin signal that the fairness benchmark depends on.

## Commands
```bash
python training/cnn/train.py --config training/cnn/config.yaml
python training/cnn/calibrate.py --checkpoint outputs/cnn/best.pt
python training/cnn/export_onnx.py --checkpoint outputs/cnn/best.pt --out outputs/cnn/cnn_v0.onnx
python training/cnn/export_tflite.py --onnx outputs/cnn/cnn_v0.onnx --out outputs/cnn/cnn_v0.tflite
python benchmarks/age_gate/run_age_benchmark.py --model outputs/cnn/cnn_v0.onnx --manifest data/manifests/manifest_benchmark_v0.parquet
```

## Rules
- Face detect + align (MTCNN/RetinaFace/MediaPipe) before the crop; reject low-quality faces.
- Calibration is mandatory before release - uncertainty must be trustworthy near the 18 boundary.
- A model cannot ship without the §7.6 release bundle (frozen manifest, run ID, version ID, thresholds, subgroup report, latency report, known-limitations, release decision).

## Acceptance (§8.6): best.pt, cnn_v0.onnx, cnn_v0.tflite, thresholds_v0.json, benchmark_age_report_v0.md, latency_report_v0.md, MODEL_CARD_CNN.md, Supabase model_versions row, HF artifact.
