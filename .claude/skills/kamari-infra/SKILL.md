---
name: kamari-infra
description: Provision and wire Kámárí infrastructure — Supabase (Postgres/Auth/RLS/Storage), Modal (GPU serving/training), Railway (API host), n8n (automation), Hugging Face (artifacts), and GitHub Actions CI/CD. Use for infra/ and .github/ work.
---

# Kámárí Infrastructure

Separation of concerns is the whole point: **Railway orchestrates, Modal computes, Supabase remembers, n8n notifies, HF publishes.**

## Supabase (§12) — self-hosted
Tables: app_users, organizations, api_keys, model_versions, inference_requests, age_decisions, verification_sessions, benchmark_runs, benchmark_metrics, audit_events, feedback, n8n_events. Files in `infra/supabase/{schema.sql, rls_policies.sql, storage_policies.sql, seed.sql}`.
- **RLS mandatory:** users see only their org; API keys limited to scopes; admin tables admin-only; benchmark metadata public only if explicitly marked; **raw images never accessible by default**.
- Storage: reports, model/dataset/benchmark cards only. Never raw minor images in public buckets.

## Modal (§13)
Services: modal_age_{train,infer}, modal_gemma_{train_lora,infer}, modal_benchmark_runner. Pin artifact versions; configure secrets; measure cold-start + p50/p95; FastAPI handles fallback errors.

## Railway (§14)
Hosts FastAPI gateway only (no GPU). Services: kamari-api-staging, kamari-api-prod. Env vars per kamari-api skill. `infra/railway/{railway.json, Dockerfile}`.

## n8n (§15) — operations only, never ML decisions
Workflows: signup→welcome email; API-key request→admin approve/reject→email; benchmark complete→report email; release-candidate fail→alert; weekly usage report; high-error-rate incident; dataset-licence-review task. Commit workflow exports to `infra/n8n/workflow_exports/`; separate staging/prod; configure webhook secrets.

## Hugging Face (§17)
Repos: kamari/cnn-age-v0, kamari/gemma-explain-lora-v0, kamari/kamari-safe-open-v0, kamari/dataset-registry-v0. Cards + adapters + benchmark metadata only. **Never upload raw face images** unless licence+consent+redistribution explicitly allow.

## GitHub CI/CD (§16)
Branches: main (prod) · staging · feature/* · model/*. Workflows in `.github/workflows/`: api-ci (lint/type/test/docker), app-ci (install/lint/type/test/build web+PWA), model-tests (adapters, manifest schema, metric fns), benchmark-nightly (scheduled Modal call → Supabase). Release tags: api-v*, app-v*, cnn-v*, gemma-v*, benchmark-v*.
