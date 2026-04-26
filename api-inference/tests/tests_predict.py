"""
Pytest tests untuk POST /predict dan GET /health — ChatKasir API-2.

Semua test menggunakan mock ModelLoader agar tidak membutuhkan model Keras
atau tokenizer sungguhan saat CI/CD.
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Patch ModelLoader dan load_slang_dict sebelum import app
# agar tidak ada loading model/file saat test collection
with (
    patch("app.services.model_loader.ModelLoader._load_model"),
    patch("app.services.preprocessing.load_slang_dict", return_value={}),
):
    from app.main import app

client = TestClient(app, raise_server_exceptions=False)

VALID_HEADERS = {"X-API-Key": "changeme"}

RAW_CHAT_SIMPLE = (
    "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya\n"
    "[07.44, 22/4/2026] Penjual: oke kak 1 nasi goreng 10rb totalnya 20rb ya"
)

RAW_CHAT_NO_TOTAL = (
    "[08.00, 22/4/2026] Pembeli: pesan 3 es teh\n"
    "[08.01, 22/4/2026] Penjual: oke es teh 5rb ya"
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_model_predict():
    """
    Ganti singleton model dengan mock yang mengembalikan output deterministik:
    product='nasi goreng', quantity=2, price_satuan=10000.
    """
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={
            "product": "nasi goreng",
            "quantity": 2,
            "price_satuan": 10000,
        },
    ), patch(
        "app.services.model_loader.ModelLoader.is_loaded",
        return_value=True,
    ), patch(
        "app.services.model_loader.ModelLoader._model",
        MagicMock(),
    ), patch(
        "app.services.model_loader.ModelLoader._tokenizer",
        MagicMock(),
    ):
        yield


# ── GET /health ───────────────────────────────────────────────────────────────

def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in ("ok", "degraded")
    assert isinstance(body["model_loaded"], bool)
    assert "version" in body


# ── POST /predict — autentikasi ───────────────────────────────────────────────

def test_predict_missing_api_key():
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE})
    assert response.status_code == 401


def test_predict_invalid_api_key():
    response = client.post(
        "/predict",
        json={"raw_text": RAW_CHAT_SIMPLE},
        headers={"X-API-Key": "salah"},
    )
    assert response.status_code == 401


# ── POST /predict — sukses ────────────────────────────────────────────────────

def test_predict_success_structure():
    """Response harus memiliki semua field yang dibutuhkan Alfan (dashboard)."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    body = response.json()

    assert "results" in body
    assert "clean_text" in body
    assert isinstance(body["results"], list)
    assert len(body["results"]) >= 1

    item = body["results"][0]
    assert "product" in item
    assert "quantity" in item
    assert "price_satuan" in item
    assert "total" in item
    assert "confidence" in item


def test_predict_total_calculated_correctly():
    """total harus = quantity × price_satuan."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    item = response.json()["results"][0]
    assert item["total"] == item["quantity"] * item["price_satuan"]


def test_predict_high_confidence_when_total_matches():
    """
    Chat sederhana dengan totalnya 20rb dan mock quantity=2, price=10000 →
    total_prediksi=20000 cocok → confidence=HIGH.
    """
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    item = response.json()["results"][0]
    assert item["confidence"] == "HIGH"


def test_predict_medium_confidence_when_no_total_in_chat():
    """Chat tanpa menyebutkan total → confidence=MEDIUM."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={"product": "es teh", "quantity": 3, "price_satuan": 5000},
    ):
        response = client.post(
            "/predict",
            json={"raw_text": RAW_CHAT_NO_TOTAL},
            headers=VALID_HEADERS,
        )
    assert response.status_code == 200
    item = response.json()["results"][0]
    assert item["confidence"] == "MEDIUM"


def test_predict_clean_text_removes_timestamp():
    """clean_text tidak boleh mengandung format timestamp WhatsApp."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    clean = response.json()["clean_text"]
    assert "[07.42" not in clean
    assert "22/4/2026" not in clean
    assert "[SEP]" in clean


# ── POST /predict — validasi input ───────────────────────────────────────────

def test_predict_missing_raw_text():
    response = client.post("/predict", json={}, headers=VALID_HEADERS)
    assert response.status_code == 422


def test_predict_too_short_raw_text():
    response = client.post("/predict", json={"raw_text": "hi"}, headers=VALID_HEADERS)
    assert response.status_code == 422


# ── POST /predict — error model ───────────────────────────────────────────────

def test_predict_model_not_loaded_returns_503():
    from app.core.errors import ModelNotLoadedError

    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        side_effect=ModelNotLoadedError(),
    ):
        response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 503


def test_predict_inference_failure_returns_500():
    from app.core.errors import InferenceFailedError

    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        side_effect=InferenceFailedError("test error"),
    ):
        response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 500
