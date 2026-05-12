"""
Integration tests untuk POST /predict dan GET /health — ChatKasir API-2.

Skenario yang diuji:
  A. Autentikasi (missing key, wrong key)
  B. Validasi input (missing field, teks < 5 karakter, teks kosong setelah preprocessing)
  C. Sukses — 1 produk dengan total cocok (HIGH)
  D. Sukses — tanpa total di chat (MEDIUM)
  E. Sukses — total di chat tidak cocok (LOW)
  F. Edge case — harga tidak disebutkan (price_satuan: null)
  G. Edge case — produk tidak dikenal (product: "unknown")
  H. Error model (503 model not loaded, 500 inference failed)
  I. Preprocessing — timestamp dihapus, [SEP] ada, slang dinormalisasi
  J. Struktur response lengkap (semua field wajib ada)

Semua test menggunakan mock ModelLoader agar tidak membutuhkan model Keras.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Patch sebelum import app agar tidak ada loading model/file saat test collection
with (
    patch("app.services.model_loader.ModelLoader._load_model"),
    patch("app.services.preprocessing.load_slang_dict", return_value={}),
):
    from app.main import app

client = TestClient(app, raise_server_exceptions=False)

VALID_HEADERS = {"X-API-Key": "changeme"}

# ── Fixture data ──────────────────────────────────────────────────────────────

RAW_CHAT_SIMPLE = (
    "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya\n"
    "[07.44, 22/4/2026] Penjual: oke kak 1 nasi goreng 10rb totalnya 20rb ya"
)
RAW_CHAT_NO_TOTAL = (
    "[08.00, 22/4/2026] Pembeli: pesan 3 es teh\n"
    "[08.01, 22/4/2026] Penjual: oke es teh 5rb ya"
)
RAW_CHAT_TOTAL_MISMATCH = (
    "[09.00, 22/4/2026] Pembeli: mau 2 ayam bakar\n"
    "[09.01, 22/4/2026] Penjual: ayam bakar 15rb totalnya 25rb ya"
)
RAW_CHAT_NO_PRICE = (
    "[10.00, 22/4/2026] Pembeli: pesan 1 jus alpukat\n"
    "[10.01, 22/4/2026] Penjual: oke, nanti saya cek harganya"
)
RAW_CHAT_SLANG = (
    "[07.42, 22/4/2026] Pembeli: bg psnnn nasgorrrr 2 yak\n"
    "[07.44, 22/4/2026] Penjual: oke kak, 1 nasi goreng 10rb total 20rb"
)
RAW_CHAT_MULTI_LINE = (
    "[07.40, 22/4/2026] Pembeli: bang mau pesan\n"
    "[07.41, 22/4/2026] Pembeli: 2 nasi goreng sama 1 es teh\n"
    "[07.43, 22/4/2026] Penjual: nasi goreng 10rb es teh 5rb totalnya 25rb ya"
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_model_loaded():
    """Pastikan model dianggap loaded di semua test."""
    with (
        patch("app.services.model_loader.ModelLoader._model", MagicMock()),
        patch("app.services.model_loader.ModelLoader._tokenizer", MagicMock()),
        patch("app.services.model_loader.ModelLoader.is_loaded", return_value=True),
    ):
        yield


@pytest.fixture
def mock_predict_nasi_goreng():
    """Mock predict_single: nasi goreng, qty=2, price=10000."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={"product": "nasi goreng", "quantity": 2, "price_satuan": 10000},
    ):
        yield


@pytest.fixture
def mock_predict_no_price():
    """Mock predict_single: produk dikenal tapi harga = null."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={"product": "jus alpukat", "quantity": 1, "price_satuan": None},
    ):
        yield


@pytest.fixture
def mock_predict_unknown_product():
    """Mock predict_single: NER gagal, produk tidak dikenal."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={"product": "unknown", "quantity": 1, "price_satuan": None},
    ):
        yield


# ── A. Autentikasi ────────────────────────────────────────────────────────────

def test_predict_missing_api_key(mock_predict_nasi_goreng):
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE})
    assert response.status_code == 401
    body = response.json()
    assert body["error"] is True
    assert body["error_code"] == 4010


def test_predict_wrong_api_key(mock_predict_nasi_goreng):
    response = client.post(
        "/predict",
        json={"raw_text": RAW_CHAT_SIMPLE},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_health_no_auth_required():
    """GET /health tidak butuh API key."""
    response = client.get("/health")
    assert response.status_code == 200


# ── B. Validasi input ─────────────────────────────────────────────────────────

def test_predict_missing_raw_text():
    response = client.post("/predict", json={}, headers=VALID_HEADERS)
    assert response.status_code == 422
    body = response.json()
    assert body["error"] is True
    assert body["error_code"] == 1001   # INVALID_INPUT


def test_predict_too_short_2_chars():
    """Teks 2 karakter → INVALID_INPUT."""
    response = client.post("/predict", json={"raw_text": "hi"}, headers=VALID_HEADERS)
    assert response.status_code == 422
    body = response.json()
    assert body["error"] is True
    assert body["error_code"] == 1001


def test_predict_too_short_4_chars():
    """Teks 4 karakter → INVALID_INPUT (batas minimal = 5)."""
    response = client.post("/predict", json={"raw_text": "abcd"}, headers=VALID_HEADERS)
    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == 1001


def test_predict_exactly_5_chars_accepted(mock_predict_nasi_goreng):
    """
    Teks tepat 5 karakter → tidak ditolak karena PANJANG (error_code 1001).
    Boleh gagal karena alasan lain (misal teks tidak mengandung format WhatsApp).
    """
    response = client.post("/predict", json={"raw_text": "12345"}, headers=VALID_HEADERS)
    # Kalau 422, pastikan bukan karena length check (error_code 1001 dari length)
    if response.status_code == 422:
        body = response.json()
        # error 1001 boleh, tapi pesannya harus bukan soal panjang karakter
        assert "terlalu pendek" not in body.get("message", "").lower(), (
            "Input 5 karakter tidak boleh ditolak karena terlalu pendek"
        )


def test_predict_empty_string():
    response = client.post("/predict", json={"raw_text": ""}, headers=VALID_HEADERS)
    assert response.status_code == 422
    assert response.json()["error_code"] == 1001


# ── C. Sukses — HIGH confidence ───────────────────────────────────────────────

def test_predict_success_high_confidence(mock_predict_nasi_goreng):
    """Chat dengan total 20rb, qty=2, price=10000 → total cocok → HIGH."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    item = response.json()["results"][0]
    assert item["confidence"] == "HIGH"
    assert item["product"] == "nasi goreng"
    assert item["quantity"] == 2
    assert item["price_satuan"] == 10000
    assert item["total"] == 20000


def test_predict_total_calculated_correctly(mock_predict_nasi_goreng):
    """total harus selalu = quantity × price_satuan."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    item = response.json()["results"][0]
    assert item["total"] == item["quantity"] * item["price_satuan"]


# ── D. Sukses — MEDIUM confidence (tanpa total) ───────────────────────────────

def test_predict_medium_confidence_no_total():
    """Chat tanpa total → MEDIUM."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={"product": "es teh", "quantity": 3, "price_satuan": 5000},
    ):
        response = client.post("/predict", json={"raw_text": RAW_CHAT_NO_TOTAL}, headers=VALID_HEADERS)
    assert response.status_code == 200
    assert response.json()["results"][0]["confidence"] == "MEDIUM"


# ── E. Sukses — LOW confidence (total tidak cocok) ───────────────────────────

def test_predict_low_confidence_total_mismatch():
    """Prediksi qty=2 × price=15000=30000, tapi chat bilang 25rb → LOW."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={"product": "ayam bakar", "quantity": 2, "price_satuan": 15000},
    ):
        response = client.post(
            "/predict",
            json={"raw_text": RAW_CHAT_TOTAL_MISMATCH},
            headers=VALID_HEADERS,
        )
    assert response.status_code == 200
    assert response.json()["results"][0]["confidence"] == "LOW"


# ── F. Edge case — harga tidak disebutkan ─────────────────────────────────────

def test_predict_null_price_when_price_not_mentioned(mock_predict_no_price):
    """Ketika price_satuan = null → total = null, confidence = MEDIUM."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_NO_PRICE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    item = response.json()["results"][0]
    assert item["price_satuan"] is None
    assert item["total"] is None
    assert item["confidence"] == "MEDIUM"


def test_predict_null_price_product_still_returned(mock_predict_no_price):
    """Meskipun harga null, nama produk tetap harus ada di response."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_NO_PRICE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    item = response.json()["results"][0]
    assert item["product"] is not None
    assert len(item["product"]) > 0


# ── G. Edge case — produk tidak dikenal ───────────────────────────────────────

def test_predict_unknown_product_fallback(mock_predict_unknown_product):
    """Ketika NER gagal → product='unknown', confidence='MEDIUM'."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_NO_PRICE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    item = response.json()["results"][0]
    assert item["product"] == "unknown"
    assert item["confidence"] == "MEDIUM"


def test_predict_unknown_product_never_high_confidence(mock_predict_unknown_product):
    """Produk unknown tidak boleh mendapat confidence HIGH meskipun total cocok."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    assert response.json()["results"][0]["confidence"] != "HIGH"


# ── H. Error model ─────────────────────────────────────────────────────────────

def test_predict_model_not_loaded_returns_503():
    from app.core.errors import ModelNotLoadedError
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        side_effect=ModelNotLoadedError(),
    ):
        response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 503
    body = response.json()
    assert body["error"] is True
    assert body["error_code"] == 1002


def test_predict_inference_failure_returns_500():
    from app.core.errors import InferenceFailedError
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        side_effect=InferenceFailedError("test error"),
    ):
        response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 500
    body = response.json()
    assert body["error"] is True
    assert body["error_code"] == 1003


# ── I. Preprocessing ──────────────────────────────────────────────────────────

def test_predict_clean_text_removes_timestamp(mock_predict_nasi_goreng):
    """clean_text tidak boleh mengandung format timestamp WhatsApp."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    clean = response.json()["clean_text"]
    assert "07.42" not in clean
    assert "22/4/2026" not in clean


def test_predict_clean_text_has_sep_separator(mock_predict_nasi_goreng):
    """clean_text harus mengandung [SEP] antara pesan pembeli dan penjual."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    assert "[SEP]" in response.json()["clean_text"]


def test_predict_clean_text_no_brackets_from_timestamp(mock_predict_nasi_goreng):
    """Tanda kurung siku dari timestamp harus bersih."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    # Setelah preprocessing, tidak boleh ada sisa bracket timestamp
    clean = response.json()["clean_text"]
    # "[SEP]" boleh ada, tapi "[07.42, ...]" tidak boleh
    clean_without_sep = clean.replace("[SEP]", "")
    assert "[" not in clean_without_sep


def test_predict_clean_text_lowercase(mock_predict_nasi_goreng):
    """clean_text harus lowercase."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    clean = response.json()["clean_text"].replace("[SEP]", "")
    assert clean == clean.lower()


# ── J. Struktur response lengkap ──────────────────────────────────────────────

def test_predict_response_has_all_required_fields(mock_predict_nasi_goreng):
    """Response harus punya semua field yang dibutuhkan FS-2 (Reihan) dan Alfan."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert "results" in body
    assert "clean_text" in body
    assert isinstance(body["results"], list)
    assert len(body["results"]) >= 1

    item = body["results"][0]
    for field in ("product", "quantity", "price_satuan", "total", "confidence"):
        assert field in item, f"Field '{field}' tidak ada di response"


def test_predict_confidence_is_valid_literal(mock_predict_nasi_goreng):
    """confidence harus salah satu dari HIGH, MEDIUM, LOW."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert response.json()["results"][0]["confidence"] in ("HIGH", "MEDIUM", "LOW")


def test_predict_quantity_is_positive_int(mock_predict_nasi_goreng):
    """quantity harus int ≥ 1."""
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    qty = response.json()["results"][0]["quantity"]
    assert isinstance(qty, int)
    assert qty >= 1


def test_health_response_structure():
    """GET /health harus mengembalikan status, model_loaded, version."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "model_loaded" in body
    assert "version" in body
    assert body["status"] in ("ok", "degraded")
    assert isinstance(body["model_loaded"], bool)


def test_error_response_format_consistent():
    """Semua error harus menggunakan format { error, error_code, message }."""
    # Test dengan request tanpa API key
    response = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE})
    body = response.json()
    assert "error" in body
    assert "error_code" in body
    assert "message" in body
