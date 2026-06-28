# Kámárí Skills Matrix

Tracked inventory of every skill the Kámárí build needs, mapped to the master plan
(`docs/master_plan.md`), plus the Claude Code tooling installed to support it.

Last updated: 2026-06-28

---

## 1. Installed Claude Code plugins

Enabled in `.claude/settings.json` (tracked, marketplace `claude-plugins-official`):

| Plugin | Supports |
|---|---|
| `typescript-lsp` | Ionic React + TypeScript frontend, Capacitor config |
| `pyright-lsp` | FastAPI, PyTorch CNN, Gemma, dataset/benchmark Python |
| `swift-lsp` | Capacitor iOS project |
| `kotlin-lsp` | Capacitor Android project |
| `frontend-design` | App UI / screens |
| `feature-dev` | Feature-by-feature development workflow |
| `commit-commands` | Commit helpers (feature-scoped history) |
| `code-review` | Diff review |
| `pr-review-toolkit` | PR reviews |
| `code-simplifier` | Reuse/simplification passes |
| `security-guidance` | Privacy/minor-data/security-sensitive work |
| `claude-md-management` | Keep CLAUDE.md / READMEs current |
| `skill-creator` | Author further project skills |

## 2. Project skills (in `.claude/skills/`)

Custom, version-controlled skills encoding the plan's conventions:

| Skill | Workstream |
|---|---|
| `kamari-frontend` | Ionic React + Capacitor + PWA client |
| `kamari-api` | FastAPI gateway, policy engine, security |
| `kamari-cnn` | PyTorch age model, calibration, ONNX/TFLite |
| `kamari-gemma` | Gemma LoRA explanation/policy layer |
| `kamari-data-benchmark` | Dataset registry, manifests, Kámárí-Safe Open v0 |
| `kamari-infra` | Supabase, Modal, Railway, n8n, HF, CI/CD |
| `kamari-privacy` | Cross-cutting privacy / child-safety / responsible-AI |

---

## 3. Technical skill inventory by domain

`MVP` = needed for the first demo (§19: camera → FastAPI → Modal CNN → result). `Later` = deferred phase.

### Frontend (Ionic React + Capacitor + PWA)
| Skill | Phase |
|---|---|
| TypeScript (strong) | MVP |
| React (hooks, context) | MVP |
| Ionic React + `@ionic/react-router` | MVP |
| Vite build/config | MVP |
| Browser camera APIs (`getUserMedia`) | MVP |
| TanStack React Query | MVP |
| Zod validation | MVP |
| Capacitor (camera/preferences/filesystem) | Phase 6 |
| PWA / service workers (`vite-plugin-pwa`, Workbox) | Phase 1/5 |
| `@supabase/supabase-js` auth | MVP+ |
| Multipart upload / media handling | MVP |
| i18n incl. RTL Arabic (en/sw/yo/ha/am/fr/ar) | Phase 7 |
| Android (Gradle/Android Studio) | Phase 6 |
| iOS (Xcode, signing, App Store) - macOS | Phase 6 |
| Consent/privacy UX + accessibility | MVP |

### Backend / API (FastAPI on Railway)
| Skill | Phase |
|---|---|
| Python 3.11+ async | MVP |
| FastAPI (routing, multipart, OpenAPI) | MVP |
| Pydantic v2 | MVP |
| REST design + versioning + structured errors | MVP |
| API-key security (hash + pepper, scopes) | Phase 9 |
| Rate limiting | Phase 9 |
| httpx (Modal/n8n clients) | MVP |
| Docker | MVP |
| Railway deploy (env, staging/prod) | MVP |
| Signed webhooks | Phase 7+ |
| Policy/decision engine | MVP |

### ML / AI - Computer Vision CNN
| Skill | Phase |
|---|---|
| PyTorch | Phase 4 |
| `timm` backbones (MobileNetV3 / EfficientNetV2-B0) | Phase 4 |
| Multi-head model design | Phase 4 |
| Losses (SmoothL1, focal/BCE, ordinal) | Phase 4 |
| Face detection & alignment (MTCNN/RetinaFace/MediaPipe) | Phase 4 |
| Augmentation (Albumentations, with avoid-list) | Phase 4 |
| Calibration (temperature/conformal/uncertainty) | Phase 4 |
| ONNX export + ONNX Runtime | Phase 4 |
| TFLite export | Phase 4 |
| Class imbalance / oversampling 13-21 | Phase 4 |
| Fairness-aware evaluation | Phase 3/4 |

### ML / AI - LLM fine-tuning (Gemma)
| Skill | Phase |
|---|---|
| LoRA/QLoRA (PEFT, TRL, transformers) | Phase 7 |
| Gemma family (E2B/E4B/12B) | Phase 7 |
| SFT dataset construction (JSONL) | Phase 7 |
| Constrained/structured JSON output | Phase 7 |
| LLM evaluation (schema/hallucination/policy) | Phase 7 |
| Multilingual NLP eval (FLORES-200, Masakha*) | Phase 7 |
| Prompt engineering + reason-code mapping | Phase 7 |

### ML Infrastructure / Serving
| Skill | Phase |
|---|---|
| Modal (functions, GPU, endpoints, secrets) | Phase 4 |
| GPU training (mixed precision, checkpointing) | Phase 4 |
| Inference optimization (batching, p50/p95) | Phase 4 |
| Google Colab (experiments) | Phase 3 |
| Hugging Face Hub (cards, adapters, artifacts) | Phase 4 |

### Data Engineering & Benchmarking
| Skill | Phase |
|---|---|
| Dataset adapters / ETL | Phase 3 |
| Manifest design (Parquet, pandas/pyarrow) | Phase 3 |
| Data licensing & consent governance | Phase 3 |
| Benchmark engineering (frozen splits, gates) | Phase 3 |
| Domain metrics (MPTR, MAE-by-subgroup, EER, TAR@FAR, ACER/APCER/BPCER) | Phase 3/8 |
| Skin-tone (ITA) estimation | Phase 3 |

### Data / Auth Platform (Supabase)
| Skill | Phase |
|---|---|
| PostgreSQL (schema, indexing) | MVP+ |
| Row-Level Security policies | MVP+ |
| Supabase Auth + Storage | MVP+ |
| Self-hosting Supabase | MVP+ |

### DevOps / Infra / Operations
| Skill | Phase |
|---|---|
| Git + monorepo branching | Phase 0 |
| GitHub Actions CI/CD | Phase 0+ |
| n8n automation | Phase 9 |
| Release management + model versioning | Phase 9 |
| Secrets management | MVP+ |

### Cross-cutting (non-negotiable)
- Privacy engineering & compliance (no-store defaults, minor-data, retention transparency)
- Responsible AI (bias mitigation, "estimate not legal determination", 1:1-only verification)
- Security review & threat modeling (Phase 9)
- Testing (pytest, Vitest/Jest, model-metric & adapter tests)

---

## 4. Role clustering

1. **Frontend/mobile** - Ionic React, Capacitor, PWA, TypeScript
2. **Backend/platform** - FastAPI, Supabase/Postgres, Railway, Docker, n8n
3. **ML engineer (CV)** - PyTorch CNN, calibration, ONNX/TFLite, benchmarks
4. **ML engineer (LLM/data)** - Gemma LoRA, SFT, multilingual eval, dataset governance

## 5. Minimum set to reach the first demo (§19)
TypeScript/React/Ionic · browser camera · React Query/Zod · FastAPI + Pydantic + Docker + Railway · Modal serving · basic PyTorch CNN + ONNX export. Gemma, verification, liveness, n8n, and app-store builds are deferrable.
