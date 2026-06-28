# Kámárí

African-focused **age-gating and face-verification** system, built web-first and shipped as web app, PWA, Android, and iOS from one codebase.

**Core split:** a small calibrated **CNN** makes the age-gate decision; **Gemma** explains it (multilingual, policy, strict JSON); **FastAPI** orchestrates; **Ionic React + Capacitor** is the client; **Postgres + pgvector**, **Modal**, **Railway**, **n8n**, and **Hugging Face** provide data, compute, hosting, automation, and public artifacts.

See `kamari_web_first_master_plan (2).md` for the full build plan.

## Deliverables
1. Kámárí Dataset + Benchmark (Kámárí-Safe Open v0)
2. Kámárí Small CNN age-gating model
3. Kámárí Gemma fine-tuned explanation/policy model
4. Kámárí API + Web/PWA/Android/iOS app

## Planned monorepo layout
```
apps/{api, kamari_app}   services/{modal_age, modal_gemma, verification, liveness}
data/   training/{cnn, gemma}   benchmarks/   infra/   docs/
```

## Privacy posture (default)
No raw face images or embeddings stored by default · metadata + audit logs only · retention visible in API and UI · **1:1 verification only, never 1:N face search** · every age result is an estimate, not a legal determination.

## Setup
- **[`docs/SETUP.md`](docs/SETUP.md)** — tier-by-tier setup: app, local gateway, self-hosted Postgres + pgvector, Railway, Modal, native.

## Repo tooling
- **Skills matrix:** [`docs/skills_matrix.md`](docs/skills_matrix.md) — full skill inventory + installed Claude Code plugins + project skills.
- **Claude Code plugins:** enabled in `.claude/settings.json`.
- **Project skills:** `.claude/skills/kamari-*` encode each workstream's conventions.

## Contributing conventions
- Commit **feature by feature**; commits authored as `chidi.ashinze@gmail.com`.
- Update relevant READMEs after any major addition.
- Branches: `main` (prod) · `staging` · `feature/*` · `model/*`.

## Status
- ✅ Data pipeline — single Colab notebook (`notebooks/kamari_data_pipeline_v3_new_fast.ipynb`): gather → auto label-quality gate → preprocess → EDA → HF. *Run on Colab.*
- ✅ App MVP — `apps/kamari_app` (Ionic React + Capacitor + PWA), African design system, full Welcome→Consent→Camera→Result flow on a mock-to-live API seam.
- ✅ API gateway — `apps/api` (FastAPI): policy engine, fastapi-users JWT auth over Postgres+pgvector, Modal clients, mock-to-live.
- ✅ **CNN trained** — `tf_efficientnetv2_s`, 30 epochs, **MAE 6.03** (held-out). ONNX for CPU serving.
- ⏳ **Gemma 4 (E4B) fine-tune** — in progress on Modal H200.

### Trained artifacts (Hugging Face, namespace `Shinzmann`)
| Artifact | Repo |
|---|---|
| CNN age model (ONNX + weights + reports) | [`Shinzmann/cnn-age-v0`](https://huggingface.co/Shinzmann/cnn-age-v0) |
| Gemma 4 explanation LoRA | [`Shinzmann/gemma-explain-lora-v0`](https://huggingface.co/Shinzmann/gemma-explain-lora-v0) |
| Training faces (private) | `Shinzmann/kamari-faces-v0` |
| Dataset registry / provenance | `Shinzmann/dataset-registry-v0` |
| Benchmark (Kámárí-Safe Open v0) | `Shinzmann/kamari-safe-open-v0` |
| Gemma SFT set | `Shinzmann/gemma-sft-v0` |

### Where things run
| Workstream | Runs on |
|---|---|
| Data gather/clean/EDA/upload | Google Colab → Hugging Face |
| CNN + Gemma **training** | Modal (H200) |
| **CNN serving** | **CPU** (ONNX, ~14 ms) |
| **Gemma serving** | **GPU** (4B; CPU/q4-GGUF optional) |
| App + API gateway | Local / Railway |
