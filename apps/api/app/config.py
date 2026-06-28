"""Gateway settings (env-driven). See infra/railway for deployment env."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ML endpoints (Modal). Empty -> gateway uses a built-in mock so it runs standalone.
    modal_age_endpoint: str = ""
    modal_gemma_endpoint: str = ""

    # Supabase / Postgres (logging/audit). Optional in dev.
    # Self-hosted + sub-schema: connect directly via DATABASE_URL to the `kamari` schema.
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    database_url: str = ""
    supabase_db_schema: str = "kamari"

    # Security
    api_key_pepper: str = "dev-pepper-change-me"
    require_api_key: bool = False  # set True in production

    # Human auth - Supabase GoTrue. The gateway VERIFIES Supabase-issued JWTs (HS256)
    # using the project's JWT secret; users live in Supabase auth.users.
    supabase_anon_key: str = ""
    supabase_jwt_secret: str = ""        # GOTRUE_JWT_SECRET / project JWT secret
    supabase_jwt_aud: str = "authenticated"

    # Policy thresholds (mirrors training/cnn thresholds_v0.json defaults)
    block_p_under_18: float = 0.70
    challenge_threshold: int = 21
    legal_threshold: int = 18
    uncertainty_threshold: float = 0.28
    min_quality: float = 0.40

    retention_default: str = "image_not_stored"
    use_gemma_message: bool = True

    # n8n email (live "Dynamic Email Template Sender" workflow). The gateway POSTs
    # {template:{to,subject,body,isHtml}, variables:{...}} with the header-auth secret.
    n8n_email_webhook_url: str = ""
    n8n_email_header_name: str = "EMAIL_SECRET"  # n8n Header Auth credential name
    n8n_email_header_secret: str = ""
    email_from_name: str = "Kamari"

    # Public app URL (Railway) - used to build links inside emails.
    app_public_url: str = "https://kamari.app"


@lru_cache
def get_settings() -> Settings:
    return Settings()
