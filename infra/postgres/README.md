# Kámárí - database (Supabase)

Kámárí uses a self-hosted **Supabase** project. Auth is **GoTrue** (the gateway verifies
Supabase-issued JWTs), and data goes through **Supabase REST (PostgREST)**. The gateway runs against
the **public** schema, which PostgREST exposes by default, so no schema reconfiguration is needed.

## Apply the schema
Paste **`schema_public.sql`** into the Supabase SQL editor and run it. It creates the three tables
the gateway uses (`organizations`, `api_keys`, `inference_requests`) in `public` and grants the
`service_role`.

```
SUPABASE_DB_SCHEMA=public
```

`schema.sql` is an optional variant that puts everything in a dedicated `kamari` schema and adds
`pgvector` for future 1:1 verification. To use it, run it in the SQL editor, set
`PGRST_DB_SCHEMAS=public,storage,graphql_public,kamari` on the PostgREST service, and set
`SUPABASE_DB_SCHEMA=kamari`.

## Connect the gateway
Set on the API service (see `apps/api/.env.example`):
```
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...     # gateway data ops via REST
SUPABASE_ANON_KEY=...
SUPABASE_JWT_SECRET=...           # used to verify GoTrue access tokens (HS256)
SUPABASE_DB_SCHEMA=public
```

## Auth model
- **Humans** (developer portal): Supabase GoTrue. The app signs in with Supabase and sends the
  access token as a bearer; the gateway verifies it with the project JWT secret.
- **Machines** (API product): hashed API keys in `api_keys` (sha256 + pepper), validated and rate
  limited per plan in `apps/api/app/security/api_keys.py` and `app/billing.py`.

## Privacy
Only request metadata is stored (decision, reason code, model version, request id, organization);
never raw images. See `inference_requests.retention_policy`.

Pricing tiers store the plan on the org owner's Supabase user metadata, so no extra table is needed.

Full setup flow: `docs/SETUP.md`.
