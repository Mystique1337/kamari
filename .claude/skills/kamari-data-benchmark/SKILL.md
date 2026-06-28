---
name: kamari-data-benchmark
description: Build the Kámárí dataset registry, adapters, manifests, and the Kámárí-Safe Open v0 benchmark in data/ and benchmarks/. Use for dataset ETL, manifest schema, licensing/consent governance, and safety/fairness/verification/liveness metrics.
---

# Kámárí Data + Benchmark

The benchmark is the **evidence** that Kámárí is safe for African users near the under-18 boundary - treat it as a first-class deliverable, not a side task.

## Dataset governance (§6) - legally sensitive, do not shortcut
Classify every dataset as `train | auxiliary | benchmark | agreement_only | exclude` in `data/registry/datasets_free_open.yaml`.
- Exact-age training: UTKFace, APPA-REAL, AgeDB, FG-NET, All-Age-Faces, filtered IMDB-WIKI, AxonData (only if licence/consent allow).
- African signal: FAGE_v2 (resolvable age), FairFace Black subset. Agreement-only (CASIA-Face-Africa, BVC-UNN, NEFI) are excluded from v0 unless access approved.
- Verification benchmark: RFW African subset, BFW, LFW, AgeDB pairs. Liveness: CelebA-Spoof (+ OULU-NPU/Replay/SiW only if terms allow).
- **EXCLUDE:** MS-Celeb-1M & derivatives; commercial child datasets without licence+DPA+parental consent+ethics approval; bracket labels used as exact 18-truth; synthetic children as benchmark truth.

## Manifest (§6.3) - one standard row per image, never train from loose folders
`image_id, path, dataset, split, subject_id, age, age_exact, age_band, is_minor, gender, race_hint, country, skin_ita, skin_band, face_quality, bbox, license, consent_basis, source_url, source_hash, usable_for_age, usable_for_verification, usable_for_liveness, train_ok, eval_ok, synthetic, created_at`. Store as Parquet (pandas/pyarrow).

## Benchmark: "Kámárí-Safe Open v0" (§7)
Fixed splits: general, african_signal, black_subset, boundary_13_21, dark_skin, low_quality_camera.
- **Headline safety metric = Minor-Pass-Through Rate** @18 and @21 (esp. dark-skin / ITA-dark). Also: MAE overall + by age/skin/dataset/gender, Adult-Block Rate, False Secondary-Check Rate, detection-failure, quality-rejection, uncertainty calibration, latency p50/p95.
- Verification: EER, TAR@FAR=1e-3/1e-4, RFW-African, BFW subgroup drift, latency.
- Liveness: ACER, APCER, BPCER, spoof FAR, live FRR, latency.

## Release gate (§7.6): no model ships without frozen manifest + benchmark run ID + model version ID + threshold file + full subgroup report + latency report + known-limitations + release decision (pass/limited/fail).

## Outputs: datasets_free_open.yaml, manifest_{public,train,benchmark}_v0.parquet, DATASET_CARD.md, BENCHMARK_CARD.md, license_report.md, data_quality_report.md, adapter tests.
