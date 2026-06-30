---
license: apache-2.0
library_name: pytorch
pipeline_tag: image-classification
tags:
  - age-estimation
  - age-verification
  - fairness
  - africa
  - efficientnetv2
---

# Kámárí CNN Age Model (v0)

A small, calibrated CNN that produces the age-gating signal for [Kámárí](https://kamari.shinzii.tech),
an African-focused, privacy-first age verification system. It estimates age, the probability of being
under 18, and an uncertainty, from a single face crop. **It is a signal, not a standalone gate.**

- Backbone: EfficientNetV2-S (`tf_efficientnetv2_s`), ImageNet-pretrained.
- Heads: age regression, under-18 logit, heteroscedastic (aleatoric) uncertainty.
- Trained 30 epochs on an H200 (batch 512, AdamW lr 3e-4 wd 1e-4, cosine schedule, bf16; ~15 min
  wall-clock; 22,224 train / 2,529 val exact-age rows). Selection minimizes `MAE + 5 x MPTR@18`
  (a child-safety composite). The full run is tracked in Weights & Biases (project `kamari`).

## Intended use
Input: one detected, cropped, 224x224 RGB face. Output: `{estimated_age, p_under_18, uncertainty,
face_quality}`. A downstream policy engine (conservative through the 18 to 21 band), liveness, and a
guardian flow turn the signal into a decision. Not for legal age determination and not for 1:N face
search.

## Results (held-out benchmark, n=8,322)
| Metric | Value |
|---|---|
| MAE | 6.03 years |
| MPTR@18 (minors passed as adults) | 0.317 |
| MPTR@18, dark + brown skin | 0.383 |
| MPTR@21 | 0.27 |
| Adult-block rate | 0.01 |
| Validation MAE / MPTR@18 | 5.73 / 0.20 |

MAE by skin band: very_light 5.46, light 5.72, intermediate 5.50, tan 5.99, brown 6.23, dark 6.58.
MAE by age band: 0-12 4.04, 13-15 6.10, 16-17 5.37, 18-20 4.85, 21-25 4.30, 26-35 5.22, 36-50 6.67,
51+ 8.51. GPU eval latency p50 14.2 ms.

## Training curves
Pulled from the Weights & Biases run (project `kamari`, run `cnn-tf_efficientnetv2_s`). Training loss
is a heteroscedastic Gaussian NLL, so it is allowed to go negative as the variance head sharpens;
validation MAE falls to 5.74 and the safety metric (MPTR@18) is tracked alongside it.

![CNN training curves](https://raw.githubusercontent.com/Mystique1337/kamari/main/docs/assets/training/cnn_training_curves.png)

## Limitations and safety
MAE is competitive, but **MPTR@18 is high**: about a third of true minors are scored as adults, and
higher for dark and brown skin. So the CNN must not gate alone. Kámárí mitigates this with a
conservative policy (challenge band up to 21), uncertainty routing, on-device liveness, and a
guardian consent flow. Lowering MPTR needs more 13 to 17 and African-labelled training data.
**Minor-Pass-Through Rate (MPTR)** is the metric to track, not MAE.

## Training data
Open, license-checked face datasets (UTKFace, APPA-REAL, AgeDB, FG-NET for exact age; FAGE_v2 and
FairFace for African signal) with an auto label-quality gate, MTCNN face crops, ITA skin-tone
banding, and a leakage-free split. Composite sampling boosts ages 13 to 21 (3x) and dark/brown skin
(1.5x). Full methodology: https://github.com/Mystique1337/kamari/blob/main/docs/methodology.md

## Files
`best.pt` (PyTorch weights), `cnn_v0.onnx`, `thresholds_v0.json`, `metrics_v0.json`, and reports.
Serving loads `best.pt` on CPU with OpenCV face detection and crop (matching the training crops).

## License
Apache-2.0. This is an estimate, not a legal age determination.

## Links
- Code (Apache-2.0): https://github.com/Mystique1337/kamari
- Live demo: https://kamari.shinzii.tech
- Methodology: https://github.com/Mystique1337/kamari/blob/main/docs/methodology.md
