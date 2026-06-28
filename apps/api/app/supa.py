"""Supabase client (service role) for REST data ops.

Targets the schema in SUPABASE_DB_SCHEMA (default `public`, which PostgREST exposes out of
the box). Returns None when Supabase isn't configured, so the gateway runs standalone.
"""
from functools import lru_cache

from .config import get_settings


@lru_cache
def get_client():
    s = get_settings()
    if not (s.supabase_url and s.supabase_service_role_key):
        return None
    from supabase import create_client
    return create_client(s.supabase_url.rstrip("/"), s.supabase_service_role_key)
