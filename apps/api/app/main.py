"""Kámárí API gateway (FastAPI).

Orchestration only — heavy ML lives on Modal. Validates requests, runs the policy
engine, calls Modal CNN/Gemma, logs metadata (never raw images), returns the app
contract. Deployed on Railway.
"""
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .routes import age, explain, health

app = FastAPI(
    title="Kámárí API",
    version="0.1.0",
    description="African-focused, privacy-first age verification. Estimate, not a legal determination.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to the app origin(s) in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", f"req_{uuid.uuid4().hex[:12]}")
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    rid = request.headers.get("x-request-id", f"req_{uuid.uuid4().hex[:12]}")
    return JSONResponse(
        status_code=500,
        content={"request_id": rid, "error": "internal_error", "detail": "Unexpected error."},
        headers={"x-request-id": rid},
    )


app.include_router(health.router)
app.include_router(age.router)
app.include_router(explain.router)

# Human auth via Supabase GoTrue — mounts when the project JWT secret is configured.
# (The app logs in against Supabase directly and sends the access token as a Bearer.)
if get_settings().supabase_jwt_secret:
    from fastapi import Depends

    from .auth.gotrue import current_user
    from .routes import keys

    app.include_router(keys.router)

    @app.get("/v1/me", tags=["auth"])
    async def me(user: dict = Depends(current_user)):
        return user


@app.get("/")
async def root() -> dict:
    return {"name": "Kámárí API", "docs": "/docs", "health": "/v1/health"}
