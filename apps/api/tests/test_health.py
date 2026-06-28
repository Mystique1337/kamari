"""Smoke tests for the gateway over the mock ML path (no Modal needed)."""
import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_models():
    r = client.get("/v1/models")
    assert r.status_code == 200
    assert any(m["type"] == "cnn_age" for m in r.json()["models"])


def test_estimate_mock_returns_contract():
    # 1x1 JPEG-ish bytes are fine — the mock CNN ignores pixels.
    files = {"image": ("selfie.jpg", io.BytesIO(b"\xff\xd8\xff\xd9"), "image/jpeg")}
    r = client.post("/v1/age/estimate", files=files, data={"language": "en", "country": "NG"})
    assert r.status_code == 200
    body = r.json()
    for key in ["request_id", "model_version", "estimated_age", "decision",
                "reason_code", "message", "retention"]:
        assert key in body
    assert body["retention"] == "image_not_stored"
    assert body["decision"] in {"allow", "block", "secondary_check", "recapture"}
