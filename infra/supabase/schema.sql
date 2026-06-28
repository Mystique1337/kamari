-- Kámárí database schema — designed to live in a dedicated sub-schema `kamari`
-- inside an existing (self-hosted) Postgres/Supabase instance.
--
-- Apply:
--   psql "$DATABASE_URL" -f infra/supabase/schema.sql
-- or paste into the self-hosted Supabase SQL editor.
--
-- The gateway connects with a role scoped to this schema and enforces org-scoping in
-- code (service-role connections bypass RLS). RLS policies below are defense-in-depth
-- for any direct/anon access.

create schema if not exists kamari;
set search_path = kamari, public;

create extension if not exists pgcrypto;  -- gen_random_uuid()

-- Organizations & users -------------------------------------------------------
create table if not exists kamari.organizations (
  id           uuid primary key default gen_random_uuid(),
  name         text not null,
  created_at   timestamptz not null default now()
);

create table if not exists kamari.app_users (
  id           uuid primary key default gen_random_uuid(),
  auth_id      text unique,                    -- maps to your Supabase auth user id
  organization_id uuid references kamari.organizations(id) on delete cascade,
  email        text,
  role         text not null default 'member', -- member | admin
  created_at   timestamptz not null default now()
);

-- API keys --------------------------------------------------------------------
create table if not exists kamari.api_keys (
  id           uuid primary key default gen_random_uuid(),
  organization_id uuid not null references kamari.organizations(id) on delete cascade,
  key_hash     text not null unique,           -- sha256(pepper:key), never the raw key
  name         text not null,
  scopes       text[] not null default '{age:estimate}',
  rate_limit_per_minute int not null default 60,
  status       text not null default 'active', -- active | revoked
  created_at   timestamptz not null default now(),
  last_used_at timestamptz
);
create index if not exists api_keys_org_idx on kamari.api_keys(organization_id);

-- Model registry --------------------------------------------------------------
create table if not exists kamari.model_versions (
  id           uuid primary key default gen_random_uuid(),
  model_type   text not null,                  -- cnn_age | gemma_explain | verification | liveness
  version      text not null,
  artifact_uri text,
  hf_repo      text,
  metrics_summary jsonb,
  thresholds_json jsonb,
  status       text not null default 'staging', -- staging | production | archived
  created_at   timestamptz not null default now(),
  unique (model_type, version)
);

-- Inference + decisions (NO raw images, metadata only) ------------------------
create table if not exists kamari.inference_requests (
  id           uuid primary key default gen_random_uuid(),
  request_id   text not null unique,
  organization_id uuid references kamari.organizations(id) on delete set null,
  user_id      uuid references kamari.app_users(id) on delete set null,
  endpoint     text not null,
  model_version text,
  decision     text,
  reason_code  text,
  face_quality real,
  estimated_age real,
  p_under_18   real,
  uncertainty  real,
  image_stored boolean not null default false,
  retention_policy text not null default 'image_not_stored',
  created_at   timestamptz not null default now()
);
create index if not exists inf_org_time_idx on kamari.inference_requests(organization_id, created_at desc);

create table if not exists kamari.age_decisions (
  id           uuid primary key default gen_random_uuid(),
  request_id   text references kamari.inference_requests(request_id) on delete cascade,
  decision     text not null,
  reason_code  text not null,
  created_at   timestamptz not null default now()
);

create table if not exists kamari.verification_sessions (
  id           uuid primary key default gen_random_uuid(),
  organization_id uuid references kamari.organizations(id) on delete cascade,
  status       text not null default 'pending',
  consent_given boolean not null default false,
  created_at   timestamptz not null default now()
);

-- Benchmarks ------------------------------------------------------------------
create table if not exists kamari.benchmark_runs (
  id           uuid primary key default gen_random_uuid(),
  model_version_id uuid references kamari.model_versions(id) on delete cascade,
  benchmark_version text not null,
  status       text not null default 'pending',
  metrics_json jsonb,
  report_uri   text,
  created_at   timestamptz not null default now()
);

create table if not exists kamari.benchmark_metrics (
  id           uuid primary key default gen_random_uuid(),
  benchmark_run_id uuid references kamari.benchmark_runs(id) on delete cascade,
  metric       text not null,
  subgroup     text,
  value        double precision
);

-- Ops -------------------------------------------------------------------------
create table if not exists kamari.audit_events (
  id           uuid primary key default gen_random_uuid(),
  organization_id uuid references kamari.organizations(id) on delete set null,
  actor        text,
  action       text not null,
  detail       jsonb,
  created_at   timestamptz not null default now()
);

create table if not exists kamari.feedback (
  id           uuid primary key default gen_random_uuid(),
  request_id   text,
  rating       int,
  comment      text,
  created_at   timestamptz not null default now()
);

create table if not exists kamari.n8n_events (
  id           uuid primary key default gen_random_uuid(),
  workflow     text not null,
  payload      jsonb,
  created_at   timestamptz not null default now()
);

-- RLS (defense-in-depth; the gateway uses a privileged role and scopes in code) --
alter table kamari.inference_requests enable row level security;
alter table kamari.api_keys           enable row level security;
alter table kamari.audit_events       enable row level security;
-- Example org-scoped policy (requires a JWT claim `org_id`); adjust to your auth setup:
-- create policy org_isolation on kamari.inference_requests
--   using (organization_id::text = current_setting('request.jwt.claims', true)::jsonb->>'org_id');
