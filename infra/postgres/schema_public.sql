-- Kámárí — minimal schema in the PUBLIC schema (already exposed to PostgREST).
-- Use this when you don't want to reconfigure PostgREST's db-schemas list.
-- Paste into the self-hosted Supabase SQL editor and Run.
--
-- The gateway only touches three tables: organizations, api_keys, inference_requests.
-- Set apps/api/.env: SUPABASE_DB_SCHEMA=public

create extension if not exists pgcrypto;  -- gen_random_uuid()

-- Organizations (one per authenticated owner) --------------------------------
create table if not exists public.organizations (
  id            uuid primary key default gen_random_uuid(),
  name          text not null,
  owner_auth_id text unique,            -- Supabase auth.users id (GoTrue sub)
  created_at    timestamptz not null default now()
);

-- API keys -------------------------------------------------------------------
create table if not exists public.api_keys (
  id            uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  key_hash      text not null unique,           -- sha256(pepper:key), never the raw key
  name          text not null,
  scopes        text[] not null default '{age:estimate}',
  rate_limit_per_minute int not null default 60,
  status        text not null default 'active', -- active | revoked
  created_at    timestamptz not null default now(),
  last_used_at  timestamptz
);
create index if not exists api_keys_org_idx on public.api_keys(organization_id);

-- Inference log (metadata only — NO raw images) ------------------------------
create table if not exists public.inference_requests (
  id            uuid primary key default gen_random_uuid(),
  request_id    text not null unique,
  organization_id uuid references public.organizations(id) on delete set null,
  user_id       uuid,
  endpoint      text not null,
  model_version text,
  decision      text,
  reason_code   text,
  face_quality  real,
  estimated_age real,
  p_under_18    real,
  uncertainty   real,
  image_stored  boolean not null default false,
  retention_policy text not null default 'image_not_stored',
  created_at    timestamptz not null default now()
);
create index if not exists inf_org_time_idx on public.inference_requests(organization_id, created_at desc);

-- Grants — service_role (gateway) full access; public schema is already exposed.
grant all on public.organizations, public.api_keys, public.inference_requests to service_role;
