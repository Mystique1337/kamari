# Kámárí v2 recommendation: free/open datasets, Gemma fine-tune, benchmark, API, app

## Recommendation in one sentence
Build Kámárí as a two-model system: a small calibrated CNN makes the age-gate decision, while Gemma 4 explains the decision and handles multilingual user-facing reasoning. Keep face verification as a separate API module with its own benchmark and consent rules.

## Deliverables

### 1. Small CNN age model
Purpose: fast, auditable, low-cost age estimation for African deployment conditions.

Recommended architecture:
- Backbone: `tf_efficientnetv2_b0` or `mobilenetv3_small_100` via `timm`.
- Heads:
  - exact age regression, trained only on exact-age rows;
  - under-18 / 18+ classification;
  - uncertainty/confidence bucket.
- Loss:
  - SmoothL1 for exact age;
  - focal/BCE loss for under-18 decision;
  - optional ordinal age-band loss for bracket-only datasets.
- Export: ONNX and TFLite.

Use exact-age datasets for regression: UTKFace, APPA-REAL, AgeDB, FG-NET, All-Age-Faces, filtered IMDB-WIKI, AxonData CC-BY-NC research set if accepted. Use bracketed datasets such as FairFace and Adience for fairness stress testing and age-band auxiliary training, not exact 18-boundary truth.

### 2. Gemma fine-tune
Purpose: explanation, policy, multilingual UX, and optional second-opinion classification. Gemma should not be the only age estimator unless you are willing to accept higher latency and weaker calibration.

Recommended model:
- Production/local: Gemma 4 E2B or E4B.
- Server/GPU demo: Gemma 4 12B.
- Fallback if tooling is easier: Gemma 3n or PaliGemma 2.

Fine-tuning format:
- Input: image plus CNN outputs, e.g. `estimated_age`, `p_under_18`, `legal_age`, `challenge_age`, `language`, `country`.
- Output: strict JSON with `decision`, `explanation`, `safety_note`, and `next_step`.
- Languages: English, Swahili, Yoruba, Hausa, Amharic first.
- African-language data: use task-specific templates plus native-speaker review. FLORES-200, MasakhaNER, MasakhaNEWS, and AfriSenti are useful for language evaluation/adaptation, but they are not age-estimation datasets.

### 3. Dataset + benchmark
Do not release raw minor faces publicly. Release:
- dataset registry;
- dataset adapters;
- hashes/provenance;
- public benchmark protocol;
- private/NGO benchmark statistics where raw images cannot be shared.

Benchmark headline metrics:
- Minor-Pass-Through Rate at legal age 18 and challenge ages 18/21/25;
- Minor-Pass-Through Rate for dark-skin / Fitzpatrick V-VI / ITA-dark groups;
- Adult-Block Rate;
- MAE overall and by age band / country / skin band;
- face-detection failure rate;
- latency on Raspberry Pi / Android / server;
- zero outbound network requests at inference.

Verification API benchmark metrics:
- EER;
- TAR at FAR = 1e-3 and 1e-4;
- African-subset score on RFW;
- subgroup threshold drift on BFW;
- liveness ACER/APCER/BPCER if liveness is included.

### 4. Face verification API
Keep age estimation and face verification separate.

Suggested API endpoints:
- `POST /v1/age/estimate`
- `POST /v1/age/explain`
- `POST /v1/face/verify`
- `POST /v1/liveness/check`
- `GET /v1/health`

Privacy defaults:
- Age check stores no image and no embedding by default.
- Face verification stores encrypted embeddings only when a user explicitly opts in.
- Every response should include model version, threshold, and confidence.

### 5. Own app
Recommended MVP:
- Android-first Flutter or React Native app.
- On-device face capture and quality checks.
- Local CNN inference where possible; API fallback for weaker phones.
- Gemma explanation optional/server-side for MVP, on-device later.
- User-facing explanations in English, Swahili, Yoruba, Hausa, and Amharic.

## Free/open dataset plan

### Core now
- UTKFace: exact age, gender, broad ethnicity; non-commercial research; pretraining only.
- FairFace: CC BY 4.0, balanced race/gender/age brackets; fairness and bracket training.
- APPA-REAL: real/apparent age; calibration and validation.
- Adience: phone/selfie-like in-the-wild age groups; robustness benchmark.
- AgeDB: age, gender, identity; age estimation and age-invariant verification.
- FG-NET: small longitudinal aging sanity check.
- All-Age-Faces: exact age, mostly Asian; pretraining only.
- IMDB-WIKI: large noisy celebrity dataset; use only after strict cleaning.
- FAGE_v2: African public-figure images across 10 African countries; use for African-domain signal where age labels are resolvable.
- AxonData CC-BY-NC HF set: useful research-only 10-30 boundary set if the dataset files and consent terms are accepted.

### Free but not open-download
- CASIA-Face-Africa: research/education only, no redistribution; useful if access is approved.
- BVC-UNN Face: free/publicly available after formal request; useful for Nigerian diversity.
- NEFI: useful for Nigerian diversity; verify download and training terms.

### Verification benchmarks
- LFW: general face verification sanity benchmark.
- RFW: use African subset as the key fairness benchmark.
- BFW: balanced subgroup threshold benchmark.
- AgeDB-30: age-invariant verification benchmark.

### Liveness / spoofing
- CelebA-Spoof: large anti-spoofing dataset.
- CeFA / CASIA-SURF-CeFA: cross-ethnicity anti-spoofing benchmark, likely agreement-based.
- OULU-NPU: mobile PAD benchmark, EULA-based.

## Exclude or keep out of training
- MS-Celeb-1M and derivatives: consent/reputation problem and withdrawn history.
- Commercial child datasets unless you have a signed licence, DPA, parental consent proof, and ethics approval.
- Bracket-only age labels as exact labels near 18.
- Synthetic child faces as benchmark truth.

## Concrete build order

1. Freeze the registry into `datasets_free_open.yaml` with each dataset marked as `train`, `auxiliary`, `benchmark`, `agreement_only`, or `exclude`.
2. Extend `kamari_gather.py` adapters for APPA-REAL, Adience, AgeDB, FG-NET, All-Age-Faces, IMDB-WIKI, RFW, BFW, and LFW.
3. Build `manifest_public_v0.csv` with columns: path, dataset, split, subject_id, age, age_exact, age_band, is_minor, gender, race_hint, country, ita, skin_band, source_url, license, consent_status, train_ok, eval_ok, benchmark_ok.
4. Train CNN v0 on exact-age public data, then evaluate on held-out African/public subsets.
5. Fine-tune Gemma 4 using CNN outputs and native-reviewed multilingual explanations.
6. Package FastAPI service with OpenAPI spec, Dockerfile, ONNX/TFLite CNN, Gemma adapter, and benchmark CLI.
7. Build the app as a demo client for the API and on-device CNN.
