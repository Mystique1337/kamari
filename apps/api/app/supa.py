"""Supabase client (service role) for REST data ops against the kamari schema.

Returns None when Supabase isn't configured, so the gateway runs standalone.
Requires the `kamari` schema to be exposed in PostgREST (db-schemas).
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
