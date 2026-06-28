# Kámárí Web-First Master Build Plan

**Updated direction:** build the app as a **web-first mobile-style app**, then ship the same codebase as a PWA, Android app, and iOS app using **Ionic React + Capacitor**.

**Core product idea:** Kámárí is an African-focused age-gating and face-verification system. The safest technical split is:

```text
Small CNN = measurable biometric age estimate
Gemma = explanation, policy, multilingual messaging, JSON reasoning layer
FastAPI = product API and orchestration
Ionic React + Capacitor = web, PWA, Android, iOS client
Supabase = auth, database, audit logs, storage metadata
Modal = GPU training, fine-tuning, and model serving
Railway = public API gateway
n8n = email, approvals, reports, alerts
Hugging Face = model cards, dataset cards, public artifacts
GitHub = monorepo, CI/CD, releases
Google Colab = early experiments and demos
```

---

## 1. Final deliverables

Present the project as **four major deliverables**, but build it internally as **six workstreams**.

### External deliverables

```text
1. Kámárí Dataset + Benchmark
2. Kámárí Small CNN age-gating model
3. Kámárí Gemma fine-tuned explanation/policy model
4. Kámárí API + Web/PWA/Android/iOS app
```

### Internal workstreams

```text
1. Dataset registry and manifest
2. Benchmark suite
3. Small CNN model
4. Gemma LoRA fine-tune
5. FastAPI + verification/liveness services
6. Ionic React app + PWA + Capacitor Android/iOS wrappers
```

The benchmark should not be treated as a small side task. For this project, the benchmark is the evidence that Kámárí works for African users and is safer around the under-18 boundary.

---

## 2. Revised architecture

### 2.1 Product pipeline

```text
User opens Kámárí web/PWA/mobile app
  -> consent and privacy notice
  -> camera capture
  -> face quality check
  -> liveness/spoof check
  -> face crop and alignment
  -> CNN age estimator
  -> decision engine
  -> Gemma explanation/policy layer
  -> result screen
  -> optional secondary verification / ID flow
```

### 2.2 System topology

```text
Ionic React Web App / PWA / Android / iOS
        |
        v
Railway FastAPI Gateway
        |
        +--> Supabase self-hosted
        |       - Auth
        |       - Postgres
        |       - Storage metadata
        |       - audit logs
        |       - API keys
        |       - model registry
        |
        +--> Modal CNN endpoint
        |       - age estimate
        |       - p_under_18
        |       - uncertainty
        |
        +--> Modal Gemma endpoint
        |       - explanation JSON
        |       - multilingual message
        |       - policy wording
        |
        +--> Face verification service
        |       - 1:1 verification only
        |
        +--> Liveness service
        |       - spoof/liveness check
        |
        +--> n8n webhooks
                - onboarding emails
                - API-key approval
                - benchmark reports
                - alerts
```

### 2.3 Why web-first is the right app direction now

Use **Ionic React + Capacitor + PWA** because you want to build the web app first and then make it work like mobile. This gives you one frontend codebase that can be deployed as:

```text
1. Normal web app
2. Installable PWA
3. Android app through Capacitor
4. iOS app through Capacitor
```

Capacitor is built specifically for running web apps as native iOS/Android apps while also supporting PWAs. Ionic React gives you mobile-style UI components and a React development workflow.

---

## 3. Main technical decisions

### 3.1 Do not make Gemma the age model

Gemma should not be the core biometric estimator. The CNN should estimate age because it is:

```text
fast
cheap to run
easier to calibrate
easier to benchmark
easier to export to ONNX/TFLite
easier to run on-device later
```

Gemma should do:

```text
strict JSON explanation
policy mapping
multilingual user messages
admin summaries
secondary-check instructions
compliance-friendly wording
```

### 3.2 Keep age estimation and face verification separate

Age estimation answers:

```text
How likely is this person to be under the required age threshold?
```

Face verification answers:

```text
Does this selfie match this enrolled/reference face or ID photo?
```

Do not build 1:N face search. Keep verification as **1:1 only**, with explicit consent.

### 3.3 Default privacy posture

For the MVP:

```text
Do not store uploaded face images by default.
Do not store embeddings by default.
Store only request metadata, model version, decision, and audit logs.
Allow temporary image processing with immediate deletion.
Make retention visible in API responses and app screens.
```

---

## 4. Technology stack mapping

| Layer | Tool | Role |
|---|---|---|
| Web/mobile frontend | Ionic React + TypeScript | One codebase for web, PWA, Android, iOS |
| Native wrapper | Capacitor | Package the web app as Android/iOS apps |
| PWA | Vite PWA plugin / service worker | Installable web app and offline shell |
| API gateway | FastAPI on Railway | Public API, auth checks, orchestration, OpenAPI docs |
| Database/auth | Supabase self-hosted | Auth, Postgres, Storage, model registry, audit logs |
| ML hosting | Modal | CNN inference, Gemma inference, GPU jobs |
| Training | Modal + Colab | Training, fine-tuning, experiments |
| Automation | n8n self-hosted | Emails, approvals, reports, alerts |
| Model registry/public artifacts | Hugging Face | Model cards, dataset cards, LoRA adapters, benchmark metadata |
| Source control | GitHub | Monorepo, actions, issues, releases |

---

## 5. Monorepo structure

Use one monorepo so the dataset, benchmark, models, API, and app are versioned together.

```text
kamari/
  README.md
  .github/
    workflows/
      api-ci.yml
      app-ci.yml
      model-tests.yml
      benchmark-nightly.yml

  apps/
    api/                         # FastAPI gateway deployed on Railway
      app/
        main.py
        routes/
          health.py
          age.py
          explain.py
          verification.py
          liveness.py
          sessions.py
          feedback.py
        clients/
          supabase_client.py
          modal_client.py
          n8n_client.py
        schemas/
          age.py
          verification.py
          liveness.py
        security/
          api_keys.py
          rate_limit.py
      tests/
      Dockerfile
      railway.json
      pyproject.toml

    kamari_app/                   # Ionic React + Capacitor app
      src/
        pages/
          Welcome.tsx
          Consent.tsx
          CameraCapture.tsx
          AgeResult.tsx
          SecondaryCheck.tsx
          DeveloperDashboard.tsx
          ApiKeys.tsx
          UsageLogs.tsx
          Settings.tsx
        components/
        lib/
          api.ts
          supabase.ts
          validators.ts
          camera.ts
        routes.tsx
      public/
      android/                    # generated by Capacitor
      ios/                        # generated by Capacitor
      capacitor.config.ts
      vite.config.ts
      package.json

  services/
    modal_age/
      modal_age.py
      inference.py
      preprocess.py
      weights/
    modal_gemma/
      modal_gemma.py
      inference.py
      prompts/
    verification/
      verify.py
      embeddings.py
    liveness/
      spoof.py

  data/
    registry/
      datasets_free_open.yaml
      licenses.md
      sources.md
    adapters/
      utkface.py
      fairface.py
      appa_real.py
      agedb.py
      fage_v2.py
      axondata.py
    manifests/
      manifest_public_v0.parquet
      manifest_train_v0.parquet
      manifest_benchmark_v0.parquet
    cards/
      DATASET_CARD.md
      BENCHMARK_CARD.md

  training/
    cnn/
      train.py
      model.py
      dataset.py
      losses.py
      augment.py
      config.yaml
      export_onnx.py
      export_tflite.py
      calibrate.py
    gemma/
      build_sft_dataset.py
      train_lora.py
      eval_schema.py
      eval_policy.py
      eval_languages.py
      merge_adapter.py

  benchmarks/
    age_gate/
      run_age_benchmark.py
      metrics.py
      thresholds.py
      reports/
    verification/
      run_rfw.py
      run_bfw.py
      metrics.py
    liveness/
      run_spoof_benchmark.py
      metrics.py

  infra/
    supabase/
      schema.sql
      rls_policies.sql
      storage_policies.sql
      seed.sql
    railway/
      railway.json
      Dockerfile
    modal/
      modal_age.py
      modal_gemma.py
    n8n/
      workflow_exports/

  docs/
    architecture.md
    api_contract.md
    privacy.md
    data_governance.md
    model_cards/
    release_checklist.md
```

---

## 6. Deliverable 1: Dataset + benchmark

### 6.1 Dataset principle

Do not say:

```text
We will use all datasets online.
```

Say:

```text
We will use all suitable free/open or free-for-research datasets whose licence and consent conditions allow our research use, separated into exact-age training, bracketed auxiliary training, African-domain adaptation, face-verification benchmarking, and liveness benchmarking.
```

### 6.2 Free/open or free-for-research dataset groups

#### A. Exact-age age-estimation training

Use for CNN age regression and under-18 classification:

```text
UTKFace
APPA-REAL
AgeDB
FG-NET
All-Age-Faces
Filtered IMDB-WIKI
AxonData 10-30 research sample, only if licence and access terms allow
```

#### B. African-domain signal

Use for African-domain adaptation and evaluation:

```text
FAGE_v2 rows with usable/resolvable age
FairFace Black subset for fairness/age-band evaluation
```

Agreement-only but very relevant:

```text
CASIA-Face-Africa
BVC-UNN
NEFI
```

Do not include agreement-only datasets in the free/open v0 unless access is approved and the licence allows the planned use.

#### C. Face verification benchmark

Use:

```text
RFW African subset
BFW
LFW
AgeDB verification pairs
```

#### D. Liveness / anti-spoof benchmark

Use:

```text
CelebA-Spoof
OULU-NPU / Replay-Attack / SiW only if terms allow
```

### 6.3 Manifest schema

Every image must become one standard manifest row. Do not train from loose folders.

```text
image_id
path
dataset
split
subject_id
age
age_exact
age_band
is_minor
gender
race_hint
country
skin_ita
skin_band
face_quality
bbox
license
consent_basis
source_url
source_hash
usable_for_age
usable_for_verification
usable_for_liveness
train_ok
eval_ok
synthetic
created_at
```

### 6.4 Dataset folder layout

```text
data/
  raw/
    utkface/
    fairface/
    appa_real/
    agedb/
    fage_v2/
  interim/
    aligned_faces/
    rejected_faces/
  processed/
    manifests/
    crops_224/
    crops_256/
  benchmark/
    age_gate_v0/
    verification_v0/
    liveness_v0/
```

### 6.5 Dataset deliverable outputs

```text
datasets_free_open.yaml
manifest_public_v0.parquet
manifest_train_v0.parquet
manifest_benchmark_v0.parquet
DATASET_CARD.md
BENCHMARK_CARD.md
license_report.md
data_quality_report.md
dataset_adapter_tests/
```

---

## 7. Benchmark design

### 7.1 Benchmark name

Use:

```text
Kámárí-Safe Open v0
```

### 7.2 Age-gating benchmark splits

Create these fixed splits:

```text
benchmark_age_general_v0
benchmark_age_african_signal_v0
benchmark_age_black_subset_v0
benchmark_age_boundary_13_21_v0
benchmark_age_dark_skin_v0
benchmark_age_low_quality_camera_v0
```

### 7.3 Age-gating metrics

The most important metric is not only MAE. For age-gating, the most important safety metric is:

```text
Minor-Pass-Through Rate
```

Track:

```text
MAE overall
MAE by age band
MAE by skin band
MAE by dataset
MAE by gender where available
Minor-Pass-Through Rate @18
Minor-Pass-Through Rate @21 challenge age
Adult-Block Rate
False Secondary-Check Rate
face-detection failure rate
face-quality rejection rate
uncertainty calibration
latency p50 / p95
```

### 7.4 Verification benchmark metrics

Track:

```text
EER
TAR @ FAR=1e-3
TAR @ FAR=1e-4
African-subset RFW score
BFW subgroup threshold drift
verification latency p50 / p95
```

### 7.5 Liveness benchmark metrics

Track:

```text
ACER
APCER
BPCER
spoof false-accept rate
live false-reject rate
latency p50 / p95
```

### 7.6 Benchmark acceptance criteria

A model cannot be released unless it has:

```text
frozen benchmark manifest
benchmark run ID
model version ID
threshold file
full subgroup report
latency report
known-limitations section
release decision: pass / limited release / fail
```

---

## 8. Deliverable 2: Small CNN age-gating model

### 8.1 Model design

Start with:

```text
Backbone: MobileNetV3-Large or EfficientNetV2-B0
Input: 224x224 aligned face crop
Exports: PyTorch checkpoint, ONNX, TFLite
```

Outputs:

```text
estimated_age
age_distribution
age_band
p_under_18
uncertainty
face_quality_optional
decision_hint_optional
```

### 8.2 Model heads

```text
shared CNN backbone
  -> age distribution head
  -> exact-age regression head
  -> under_18 binary classification head
  -> uncertainty/calibration head
```

### 8.3 Training order

```text
1. Train on exact-age datasets.
2. Add bracketed datasets only for auxiliary age-band learning.
3. Oversample ages 13-21.
4. Add African-domain data.
5. Evaluate on frozen Kámárí-Safe Open v0 benchmark.
6. Calibrate thresholds.
7. Export ONNX and TFLite.
8. Register model version in Supabase.
9. Publish model card to Hugging Face.
```

### 8.4 Augmentation policy

Allowed:

```text
horizontal flip
small rotation
small crop/scale
brightness/contrast/gamma
low light
motion blur
defocus blur
Gaussian noise
JPEG compression
downscale/upscale
```

Avoid:

```text
hue shifts
saturation shifts
grayscale
channel shuffle
skin recoloring
heavy facial warping
synthetic children as benchmark truth
```

### 8.5 CNN training commands

Example local or Modal-compatible flow:

```bash
python training/cnn/train.py --config training/cnn/config.yaml
python training/cnn/calibrate.py --checkpoint outputs/cnn/best.pt
python training/cnn/export_onnx.py --checkpoint outputs/cnn/best.pt --out outputs/cnn/cnn_v0.onnx
python training/cnn/export_tflite.py --onnx outputs/cnn/cnn_v0.onnx --out outputs/cnn/cnn_v0.tflite
python benchmarks/age_gate/run_age_benchmark.py --model outputs/cnn/cnn_v0.onnx --manifest data/manifests/manifest_benchmark_v0.parquet
```

### 8.6 CNN acceptance criteria

```text
best.pt
cnn_v0.onnx
cnn_v0.tflite
thresholds_v0.json
benchmark_age_report_v0.md
latency_report_v0.md
MODEL_CARD_CNN.md
Supabase model_versions row
Hugging Face model artifact
```

---

## 9. Deliverable 3: Gemma fine-tune

### 9.1 Gemma role

Gemma should receive structured outputs from the CNN and policy engine, then produce safe and consistent explanations.

Input:

```json
{
  "estimated_age": 17.4,
  "p_under_18": 0.76,
  "uncertainty": 0.18,
  "face_quality": 0.91,
  "country": "NG",
  "legal_threshold": 18,
  "challenge_threshold": 21,
  "language": "en",
  "policy_context": "age-gated service"
}
```

Output:

```json
{
  "decision": "secondary_check",
  "reason_code": "NEAR_AGE_THRESHOLD",
  "user_message": "We need an additional age check before continuing.",
  "admin_summary": "The estimate is close to the threshold and should not be auto-approved.",
  "next_step": "request_id_or_guardian_flow",
  "language": "en",
  "safety_note": "This is an estimate, not a legal age determination."
}
```

### 9.2 Gemma model strategy

Start with:

```text
Gemma small/efficient variant for low-cost serving
LoRA or QLoRA, not full fine-tuning
JSON-schema constrained outputs
Modal endpoint for inference
```

Do not train Gemma directly on raw child faces at the start. First fine-tune it on structured decision examples built from:

```text
CNN output
threshold policy
country/language settings
reason codes
approved explanation templates
edge cases
```

### 9.3 SFT dataset structure

Files:

```text
training/gemma/sft_train.jsonl
training/gemma/sft_eval.jsonl
training/gemma/policy_templates.yaml
training/gemma/output_schema.json
```

Each row:

```json
{
  "instruction": "Return a safe age-gating explanation as strict JSON.",
  "input": {
    "estimated_age": 16.8,
    "p_under_18": 0.84,
    "uncertainty": 0.16,
    "face_quality": 0.88,
    "country": "NG",
    "language": "yo",
    "legal_threshold": 18,
    "challenge_threshold": 21
  },
  "output": {
    "decision": "secondary_check",
    "reason_code": "LIKELY_UNDER_THRESHOLD",
    "user_message": "A nilo ayẹwo ọjọ-ori afikun ṣaaju ki o to tẹsiwaju.",
    "admin_summary": "The model predicts high under-18 probability; secondary verification required.",
    "next_step": "request_id_or_guardian_flow",
    "language": "yo",
    "safety_note": "This is an estimate, not a legal age determination."
  }
}
```

### 9.4 Supported languages for v0

Start with:

```text
English
Swahili
Yoruba
Hausa
Amharic
French
Arabic
```

Use English as the control language. Add other African languages only when you have enough reviewed examples and evaluation coverage.

### 9.5 Gemma evaluation

Track:

```text
JSON validity rate
schema compliance rate
decision consistency with rule engine
unsafe certainty rate
hallucination rate
language correctness
policy consistency
latency p50 / p95
cost per 1,000 requests
```

### 9.6 Gemma acceptance criteria

```text
gemma_lora_adapter/
sft_train.jsonl
sft_eval.jsonl
output_schema.json
schema_eval_report.md
policy_eval_report.md
language_eval_report.md
GEMMA_MODEL_CARD.md
Modal Gemma endpoint
Hugging Face adapter card
```

---

## 10. Deliverable 4A: API and backend

### 10.1 API service

Use:

```text
FastAPI
Railway deployment
Supabase auth/API-key validation
Modal function calls for ML
n8n webhooks for emails and reporting
```

### 10.2 API endpoints

```text
GET  /v1/health
GET  /v1/models
POST /v1/age/estimate
POST /v1/age/explain
POST /v1/face/verify
POST /v1/liveness/check
POST /v1/sessions
GET  /v1/sessions/{session_id}
POST /v1/feedback
POST /v1/webhooks/n8n/report-ready
```

### 10.3 Age estimate response

```json
{
  "request_id": "req_123",
  "model_version": "cnn_v0.1.0",
  "face_quality": 0.93,
  "estimated_age": 17.4,
  "age_band": "16-17",
  "p_under_18": 0.76,
  "uncertainty": 0.18,
  "decision": "secondary_check",
  "reason_code": "NEAR_AGE_THRESHOLD",
  "message": "We need an additional age check before continuing.",
  "retention": "image_not_stored"
}
```

### 10.4 Policy engine logic

Example:

```text
If face_quality < minimum_quality:
  decision = recapture

Else if p_under_18 >= block_threshold:
  decision = block_or_secondary_check

Else if estimated_age < challenge_threshold:
  decision = secondary_check

Else if uncertainty > uncertainty_threshold:
  decision = secondary_check

Else:
  decision = allow
```

For age-gated systems, be conservative near the threshold. The system should not auto-approve borderline cases.

### 10.5 API acceptance criteria

```text
OpenAPI docs available
API-key auth works
rate limiting works
Supabase logging works
Modal CNN endpoint integrated
Modal Gemma endpoint integrated
image retention defaults to no-store
request IDs on every response
structured errors
Postman/Insomnia collection
Railway production deployment
```

---

## 11. Deliverable 4B: Web/PWA/Android/iOS app

### 11.1 Chosen platform

Use:

```text
Ionic React + TypeScript + Capacitor + PWA
```

This is the revised decision. Do not use Flutter for this version unless your team later decides mobile-native performance is more important than web-first development.

### 11.2 Frontend packages

```bash
npm create vite@latest apps/kamari_app -- --template react-ts
cd apps/kamari_app

npm install @ionic/react @ionic/react-router ionicons
npm install @capacitor/core @capacitor/cli
npm install @capacitor/android @capacitor/ios
npm install @capacitor/camera @capacitor/preferences @capacitor/filesystem
npm install @supabase/supabase-js
npm install @tanstack/react-query
npm install zod
npm install vite-plugin-pwa
npm install react-router-dom
```

Initialize Capacitor:

```bash
npx cap init Kamari com.kamari.app
npx cap add android
npx cap add ios
```

Build and sync:

```bash
npm run build
npx cap sync
npx cap open android
npx cap open ios
```

### 11.3 App screens

Build these screens:

```text
Welcome
Consent and privacy notice
Login / signup
Camera capture
Face quality check
Liveness check
Age result
Secondary check / ID verification placeholder
Developer dashboard
API key management
Usage logs
Settings
Language selector
```

MVP screens only:

```text
Welcome
Consent and privacy notice
Camera capture
Age result
Developer dashboard
API key management
```

### 11.4 App user flow

```text
User opens app
  -> sees privacy/retention notice
  -> accepts consent
  -> camera opens
  -> user captures selfie
  -> app sends image to /v1/age/estimate
  -> API runs quality + CNN + decision engine
  -> API optionally calls Gemma explanation
  -> app shows allow / block / secondary check
```

### 11.5 Web/PWA behavior

Web version:

```text
runs at app.yourdomain.com
uses browser camera APIs
calls Railway API
can be installed as PWA
keeps offline shell cached
stores minimal local state
```

PWA version:

```text
home-screen icon
app-like launch screen
offline shell
cached static assets
no offline Gemma
no full offline verification in v0
```

### 11.6 Android/iOS Capacitor behavior

Native wrapper version:

```text
uses Capacitor Camera where needed
uses secure/preferences storage for tokens
calls the same Railway API
can later support push notifications
can later support local CNN inference
can be distributed through app stores
```

### 11.7 What should run locally vs server-side

MVP:

```text
Camera capture: local app/browser
Face quality: API first
Liveness: API first
CNN age model: Modal/API first
Gemma: Modal/API only
Verification: API only
```

Later:

```text
Small CNN: optional on-device/browser inference
Face quality: local precheck
Gemma: still server-side
Verification: server-side unless there is a strong privacy reason to move local
```

### 11.8 Frontend acceptance criteria

```text
Web build works
PWA install works on supported browsers
Android build opens through Capacitor
Ios project opens through Capacitor/Xcode
camera capture works
consent screen exists
age endpoint integration works
result screen handles allow/block/secondary_check/recapture
API-key dashboard works
privacy copy is visible
```


### 11.9 iOS build note

The app can be developed web-first on any platform, but the final iOS build and App Store submission path requires the iOS project to be opened and managed with Xcode. Plan for access to macOS/Xcode or a trusted cloud build service before the iOS release milestone.

---

## 12. Supabase design

### 12.1 Tables

```text
app_users
organizations
api_keys
model_versions
inference_requests
age_decisions
verification_sessions
benchmark_runs
benchmark_metrics
audit_events
feedback
n8n_events
```

### 12.2 Key fields

`model_versions`:

```text
id
model_type              # cnn_age, gemma_explain, verification, liveness
version
artifact_uri
hf_repo
metrics_summary
thresholds_json
status                  # staging, production, archived
created_at
```

`inference_requests`:

```text
id
request_id
organization_id
user_id_nullable
endpoint
model_version
decision
reason_code
face_quality
estimated_age_nullable
p_under_18_nullable
uncertainty_nullable
image_stored_boolean
retention_policy
created_at
```

`api_keys`:

```text
id
organization_id
key_hash
name
scopes
rate_limit_per_minute
status
created_at
last_used_at
```

`benchmark_runs`:

```text
id
model_version_id
benchmark_version
status
metrics_json
report_uri
created_at
```

### 12.3 Row-level security

Apply RLS so:

```text
users can only see their organization data
API keys can only access allowed scopes
admin-only tables require admin role
benchmark metadata can be public only if explicitly marked public
raw images are not accessible by default
```

### 12.4 Storage

Use Supabase Storage for:

```text
non-sensitive reports
model cards
dataset cards
benchmark reports
optional encrypted temporary uploads if needed
```

Do not store raw minor images in public buckets.

---

## 13. Modal design

### 13.1 Modal services

```text
modal_age_train
modal_age_infer
modal_gemma_train_lora
modal_gemma_infer
modal_benchmark_runner
```

### 13.2 CNN endpoint

Input:

```text
image bytes or signed temporary URL
```

Output:

```json
{
  "estimated_age": 17.4,
  "p_under_18": 0.76,
  "uncertainty": 0.18,
  "face_quality": 0.93,
  "model_version": "cnn_v0.1.0"
}
```

### 13.3 Gemma endpoint

Input:

```json
{
  "cnn_result": {},
  "policy_context": {},
  "language": "en"
}
```

Output:

```json
{
  "decision": "secondary_check",
  "reason_code": "NEAR_AGE_THRESHOLD",
  "user_message": "We need an additional age check before continuing.",
  "admin_summary": "Borderline age result; require secondary verification.",
  "next_step": "request_id_or_guardian_flow"
}
```

### 13.4 Modal acceptance criteria

```text
CNN inference endpoint deployed
Gemma inference endpoint deployed
cold-start behavior measured
p50/p95 latency measured
secrets configured securely
model artifact versions pinned
logs visible
fallback error responses handled by FastAPI
```

---

## 14. Railway FastAPI deployment

### 14.1 Railway role

Railway should host the public API gateway, not the heavy GPU models.

Railway handles:

```text
FastAPI app
OpenAPI docs
auth checks
rate limiting
request logging
Modal calls
Supabase calls
n8n webhooks
```

Modal handles:

```text
GPU inference
GPU training
fine-tuning
benchmarks
```

### 14.2 Railway project services

```text
kamari-api-staging
kamari-api-prod
```

### 14.3 Environment variables

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
SUPABASE_ANON_KEY
MODAL_AGE_ENDPOINT
MODAL_GEMMA_ENDPOINT
N8N_WEBHOOK_SECRET
API_KEY_PEPPER
RETENTION_DEFAULT=no_store
```

---

## 15. n8n workflows

Use n8n for operational automation, not core ML decisions.

### 15.1 Workflows

```text
New organization signup -> send welcome email
API key requested -> notify admin -> approve/reject -> email user
Benchmark completed -> email report summary
Model release candidate failed -> alert team
Weekly usage report -> email admins
High error rate -> incident email
Dataset licence review needed -> task/email flow
```

### 15.2 n8n acceptance criteria

```text
workflow exports committed to repo
webhook secrets configured
email templates written
staging and production workflows separated
failure alerts tested
```

---

## 16. GitHub and CI/CD

### 16.1 Branching

```text
main = production-ready
staging = staging deploy
feature/* = normal development
model/* = model experiments
```

### 16.2 GitHub Actions

Workflows:

```text
api-ci.yml
  - lint
  - type check
  - unit tests
  - build Docker image

app-ci.yml
  - npm install
  - lint
  - type check
  - test
  - build web/PWA

model-tests.yml
  - adapter tests
  - manifest schema tests
  - metric function tests

benchmark-nightly.yml
  - optional scheduled benchmark call to Modal
  - store result in Supabase
```

### 16.3 Release tags

Use tags like:

```text
api-v0.1.0
app-v0.1.0
cnn-v0.1.0
gemma-v0.1.0
benchmark-v0.1.0
```

---

## 17. Hugging Face artifacts

Use Hugging Face for:

```text
CNN model card
Gemma adapter card
dataset card
benchmark card
safe public artifacts
```

Do not upload raw face images unless the licence, consent, and redistribution rights explicitly allow it.

Recommended repositories:

```text
kamari/cnn-age-v0
kamari/gemma-explain-lora-v0
kamari/kamari-safe-open-v0
kamari/dataset-registry-v0
```

---

## 18. Build phases

### Phase 0: Project setup

Outputs:

```text
GitHub monorepo
Supabase local/self-hosted connected
Railway FastAPI health endpoint
Ionic React app shell
Modal hello-world endpoint
n8n test email workflow
```

Commands:

```bash
mkdir kamari && cd kamari
git init
mkdir -p apps services data training benchmarks infra docs
```

### Phase 1: Web-first app MVP

Outputs:

```text
Ionic React app
PWA config
camera capture screen
consent screen
result screen using mock API
```

Build:

```bash
npm create vite@latest apps/kamari_app -- --template react-ts
cd apps/kamari_app
npm install @ionic/react @ionic/react-router ionicons @tanstack/react-query zod
npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/ios @capacitor/camera
npm install vite-plugin-pwa @supabase/supabase-js
npx cap init Kamari com.kamari.app
npm run build
```

### Phase 2: FastAPI MVP

Outputs:

```text
/v1/health
/v1/age/estimate mock
OpenAPI docs
Railway deployment
```

### Phase 3: Dataset manifest v0

Outputs:

```text
datasets_free_open.yaml
adapters for first datasets
manifest_public_v0.parquet
manifest_train_v0.parquet
manifest_benchmark_v0.parquet
DATASET_CARD.md
```

### Phase 4: CNN v0

Outputs:

```text
trained CNN
benchmark report
ONNX export
TFLite export
Modal inference endpoint
/v1/age/estimate real endpoint
```

### Phase 5: App integration

Outputs:

```text
camera -> API -> result flow
consent screen connected
request IDs visible
error handling
PWA install metadata
```

### Phase 6: Capacitor Android/iOS

Outputs:

```text
Android project builds
Ios project builds
camera permissions configured
same API flow works
```

### Phase 7: Gemma LoRA

Outputs:

```text
SFT JSONL
LoRA adapter
schema eval
policy eval
Modal Gemma endpoint
/v1/age/explain endpoint
```

### Phase 8: Verification and liveness

Outputs:

```text
/v1/face/verify
/v1/liveness/check
RFW/BFW verification benchmark
CelebA-Spoof liveness benchmark
```

### Phase 9: Production hardening

Outputs:

```text
rate limits
API-key management
n8n emails
benchmark automation
release checklist
security review
privacy review
```

---

## 19. First MVP target

The first demo should be very focused:

```text
Web/PWA app camera
  -> FastAPI endpoint
  -> Modal CNN endpoint
  -> age estimate + decision
  -> result screen
```

Do not make the first demo depend on:

```text
full Gemma fine-tune
full ID verification
full liveness
app store release
on-device CNN
```

Those come after the basic web-first flow works.

---

## 20. API contract for MVP

### Request

```http
POST /v1/age/estimate
Content-Type: multipart/form-data
Authorization: Bearer <api_key_or_user_token>

image=<file>
language=en
country=NG
```

### Response

```json
{
  "request_id": "req_abc123",
  "model_version": "cnn_v0.1.0",
  "estimated_age": 17.4,
  "age_band": "16-17",
  "p_under_18": 0.76,
  "uncertainty": 0.18,
  "face_quality": 0.93,
  "decision": "secondary_check",
  "reason_code": "NEAR_AGE_THRESHOLD",
  "message": "We need an additional age check before continuing.",
  "retention": "image_not_stored"
}
```

---

## 21. Policy decision codes

Use a fixed list:

```text
ALLOW
BLOCK_LIKELY_MINOR
SECONDARY_CHECK_NEAR_THRESHOLD
SECONDARY_CHECK_LOW_CONFIDENCE
RECAPTURE_LOW_QUALITY
RECAPTURE_NO_FACE
RECAPTURE_MULTIPLE_FACES
ERROR_UNSUPPORTED_IMAGE
```

Gemma should not invent decision codes. It should choose from approved codes only.

---

## 22. Risk register

| Risk | Mitigation |
|---|---|
| Public datasets are not African enough | Keep benchmark honest; add African-domain signal; report limitations clearly |
| Age labels are noisy | Use exact-age flags, bracket flags, dataset weights, and uncertainty |
| Minor data compliance risk | Avoid storing raw minor faces; use consented/licensed data only; document retention |
| Gemma hallucinates | Constrain with schema, rule engine, and eval suite |
| PWA limitations on iOS/browser | Use Capacitor wrapper for app-store versions |
| Face verification becomes surveillance-like | Keep 1:1 only; no face search; no default embedding storage |
| Model bias | Benchmark by skin band, race hint, age band, dataset, gender where available |
| Railway overload | Keep ML on Modal; Railway only orchestrates |
| App-store review issues | Add clear privacy policy, consent, retention, and child-safety wording |

---

## 23. Updated acceptance checklist

### Dataset + benchmark

```text
[ ] Free/open dataset registry complete
[ ] Licence report complete
[ ] Manifest schema validated
[ ] Benchmark splits frozen
[ ] Dataset card written
[ ] Benchmark card written
```

### CNN

```text
[ ] CNN trained
[ ] CNN benchmarked
[ ] Thresholds calibrated
[ ] ONNX exported
[ ] TFLite exported
[ ] Modal endpoint deployed
[ ] Model card written
```

### Gemma

```text
[ ] SFT data generated
[ ] LoRA trained
[ ] JSON schema eval passed
[ ] Policy eval passed
[ ] Language eval complete
[ ] Modal endpoint deployed
[ ] Model card written
```

### API

```text
[ ] FastAPI deployed to Railway
[ ] Supabase auth/API keys integrated
[ ] Modal CNN integrated
[ ] Modal Gemma integrated
[ ] Logs/audit events stored
[ ] Rate limiting added
[ ] OpenAPI docs available
```

### App

```text
[ ] Ionic React web app built
[ ] PWA install support added
[ ] Camera capture works
[ ] API call works
[ ] Result screen works
[ ] Capacitor Android build works
[ ] Capacitor iOS project builds
[ ] Consent/privacy screen complete
```

### Operations

```text
[ ] n8n onboarding email works
[ ] n8n API-key approval flow works
[ ] Benchmark report email works
[ ] GitHub CI passes
[ ] Release checklist complete
```

---

## 24. Recommended order of work

Follow this exact order:

```text
1. Create monorepo.
2. Build Ionic React app shell.
3. Add PWA configuration.
4. Add Capacitor Android/iOS wrappers.
5. Build FastAPI health endpoint on Railway.
6. Connect Supabase auth and API-key tables.
7. Add mock /v1/age/estimate endpoint.
8. Connect app camera to mock endpoint.
9. Build dataset registry and manifest.
10. Freeze benchmark v0.
11. Train CNN v0.
12. Deploy CNN to Modal.
13. Replace mock age endpoint with real CNN inference.
14. Add result screen and decision codes.
15. Build Gemma SFT data.
16. Fine-tune Gemma LoRA.
17. Deploy Gemma to Modal.
18. Add /v1/age/explain.
19. Add face verification endpoint.
20. Add liveness endpoint.
21. Add n8n emails and reports.
22. Run full benchmark.
23. Publish model/dataset/benchmark cards.
24. Prepare demo release.
```

---

## 25. Final product story

The final Kámárí story should be:

```text
Kámárí-Data:
  free/open dataset registry, manifests, dataset cards, provenance

Kámárí-Safe:
  benchmark suite for African-focused age-gating, verification, and liveness

Kámárí-CNN:
  small deployable age-gating model with calibrated thresholds

Kámárí-Gemma:
  fine-tuned multilingual explanation and policy layer

Kámárí-API:
  FastAPI gateway with Modal ML, Supabase audit logs, and n8n operations

Kámárí-App:
  one Ionic React codebase deployed as web app, PWA, Android app, and iOS app
```

This is stronger than only building a model. It becomes a complete, benchmarked, deployable African-focused age-gating system.

---

## 26. Reference docs to keep nearby

- Capacitor docs: https://capacitorjs.com/docs
- Ionic React docs: https://ionicframework.com/docs/react
- Supabase self-hosting docs: https://supabase.com/docs/guides/self-hosting
- Modal docs: https://modal.com/docs
- Railway FastAPI guide: https://docs.railway.com/guides/fastapi
- Gemma LoRA tuning: https://ai.google.dev/gemma/docs/core/lora_tuning
- Hugging Face model cards: https://huggingface.co/docs/hub/model-cards
- Hugging Face dataset cards: https://huggingface.co/docs/hub/datasets-cards
- GitHub Actions docs: https://docs.github.com/en/actions
