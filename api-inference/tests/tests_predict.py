"""Pytest tests for POST /predict and GET /health."""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ── App setup ─────────────────────────────────────────────────────────────────
# Patch ModelLoader before importing the app so no real TF model is loaded.
with patch("app.services.model_loader.ModelLoader._load_model"):
    from app.main import app

client = TestClient(app, raise_server_exceptions=False)

VALID_HEADERS = {"X-API-Key": "changeme"}


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_model():
    """Replace the singleton model with a simple mock for every test."""
    mock = MagicMock()
    mock.predict.return_value = __import__("numpy").array([[0.9, 0.1]])
    with patch("app.services.model_loader.ModelLoader._model", mock):
        yield mock


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in ("ok", "degraded")
    assert isinstance(body["model_loaded"], bool)


# ── /predict ──────────────────────────────────────────────────────────────────

def test_predict_success():
    payload = {"inputs": [[0.1, 0.2, 0.3]]}
    response = client.post("/predict", json=payload, headers=VALID_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert "predictions" in body
    assert isinstance(body["predictions"], list)


def test_predict_missing_api_key():
    payload = {"inputs": [[0.1, 0.2, 0.3]]}
    response = client.post("/predict", json=payload)
    assert response.status_code == 401


def test_predict_invalid_api_key():
    payload = {"inputs": [[0.1, 0.2, 0.3]]}
    response = client.post("/predict", json=payload, headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_predict_empty_inputs():
    payload = {"inputs": []}
    response = client.post("/predict", json=payload, headers=VALID_HEADERS)
    assert response.status_code == 422


def test_predict_missing_inputs():
    response = client.post("/predict", json={}, headers=VALID_HEADERS)
    assert response.status_code == 422
