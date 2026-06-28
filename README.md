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
- ✅ Phase 0 — monorepo scaffold, skills tooling, planning docs.
- ✅ Data pipeline — registry + manifest schema + Colab notebooks (`notebooks/01–04`, single HF upload step). *Run on Colab.*
- ✅ App MVP — `apps/kamari_app` (Ionic React + Capacitor + PWA), African design system, full Welcome→Consent→Camera→Result flow on a mock-to-live API seam.
- ⏳ Next — Modal CNN + Gemma train/serve scripts; FastAPI gateway; wire live endpoints.

### Where things run
| Workstream | Runs on |
|---|---|
| Data gather/clean/EDA/upload | Google Colab → Hugging Face |
| CNN + Gemma training/serving | Modal (GPU) |
| App + API gateway | Local / Railway |
