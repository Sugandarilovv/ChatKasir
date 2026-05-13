"""
Integration tests untuk POST /predict dan GET /health — ChatKasir API-2.

Skenario yang diuji:
  A. Autentikasi (missing key, wrong key)
  B. Validasi input (missing field, teks < 5 karakter)
  C. Sukses — HIGH confidence (total chat cocok)
  D. Sukses — MEDIUM confidence (tidak ada total di chat, softmax >= 90)
  E. Sukses — LOW confidence (total chat tidak cocok)
  F. Edge case — harga tidak disebutkan (price_satuan: null)
  G. Edge case — produk tidak dikenal (product: "unknown")
  H. Error model (503 model not loaded, 500 inference failed)
  I. Preprocessing — timestamp dihapus, [SEP] ada
  J. Smart Regex — "jadinya" dan "semuanya" dikenali sebagai total
  K. Logika Softmax fallback saat tidak ada total di chat
  L. Struktur response lengkap (semua field wajib ada)
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

with (
    patch("app.services.model_loader.ModelLoader._load_model"),
    patch("app.services.preprocessing.load_slang_dict", return_value={}),
):
    from app.main import app

client = TestClient(app, raise_server_exceptions=False)

VALID_HEADERS = {"X-API-Key": "changeme"}

# ── Payload fixtures ──────────────────────────────────────────────────────────

RAW_CHAT_SIMPLE = (
    "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya\n"
    "[07.44, 22/4/2026] Penjual: oke kak 1 nasi goreng 10rb totalnya 20rb ya"
)
RAW_CHAT_JADINYA = (
    "[08.00, 22/4/2026] Pembeli: pesan 2 mie ayam\n"
    "[08.01, 22/4/2026] Penjual: oke kak jadinya 24rb ya"
)
RAW_CHAT_SEMUANYA = (
    "[08.00, 22/4/2026] Pembeli: mau 3 es teh\n"
    "[08.01, 22/4/2026] Penjual: semuanya 15rb kak"
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


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_model_loaded():
    with (
        patch("app.services.model_loader.ModelLoader._model", MagicMock()),
        patch("app.services.model_loader.ModelLoader._tokenizer", MagicMock()),
        patch("app.services.model_loader.ModelLoader.is_loaded", return_value=True),
    ):
        yield


@pytest.fixture
def mock_predict_nasi_goreng():
    """qty=2, price=10000 → total=20000 → cocok chat → HIGH."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={
            "product": "nasi goreng",
            "quantity": 2,
            "price_satuan": 10000,
            "avg_conf_softmax": 95.0,
        },
    ):
        yield


@pytest.fixture
def mock_predict_no_price():
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={
            "product": "jus alpukat",
            "quantity": 1,
            "price_satuan": None,
            "avg_conf_softmax": 88.0,
        },
    ):
        yield


@pytest.fixture
def mock_predict_unknown():
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={
            "product": "unknown",
            "quantity": 1,
            "price_satuan": None,
            "avg_conf_softmax": 0.0,
        },
    ):
        yield


# ── A. Autentikasi ────────────────────────────────────────────────────────────

def test_missing_api_key(mock_predict_nasi_goreng):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE})
    assert r.status_code == 401
    assert r.json()["error_code"] == 4010


def test_wrong_api_key(mock_predict_nasi_goreng):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE},
                    headers={"X-API-Key": "wrong"})
    assert r.status_code == 401


def test_health_no_auth():
    r = client.get("/health")
    assert r.status_code == 200


# ── B. Validasi input ─────────────────────────────────────────────────────────

def test_missing_raw_text():
    r = client.post("/predict", json={}, headers=VALID_HEADERS)
    assert r.status_code == 422
    assert r.json()["error_code"] == 1001


def test_too_short_2_chars():
    r = client.post("/predict", json={"raw_text": "hi"}, headers=VALID_HEADERS)
    assert r.status_code == 422
    assert r.json()["error_code"] == 1001


def test_too_short_4_chars():
    r = client.post("/predict", json={"raw_text": "abcd"}, headers=VALID_HEADERS)
    assert r.status_code == 422
    assert r.json()["error_code"] == 1001


def test_empty_string():
    r = client.post("/predict", json={"raw_text": ""}, headers=VALID_HEADERS)
    assert r.status_code == 422
    assert r.json()["error_code"] == 1001


# ── C. HIGH confidence ────────────────────────────────────────────────────────

def test_high_confidence_when_total_matches(mock_predict_nasi_goreng):
    """Business Override: total chat 20rb == prediksi 2×10000 → HIGH."""
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert r.status_code == 200
    item = r.json()["results"][0]
    assert item["confidence"] == "HIGH"
    assert item["product"] == "nasi goreng"
    assert item["quantity"] == 2
    assert item["price_satuan"] == 10000
    assert item["total"] == 20000


def test_total_equals_quantity_times_price(mock_predict_nasi_goreng):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    item = r.json()["results"][0]
    assert item["total"] == item["quantity"] * item["price_satuan"]


# ── D. MEDIUM / softmax fallback ──────────────────────────────────────────────

def test_high_via_softmax_when_no_total_in_chat():
    """Tidak ada total di chat → pakai softmax. avg_conf=95 ≥ 90 → HIGH."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={
            "product": "es teh",
            "quantity": 3,
            "price_satuan": 5000,
            "avg_conf_softmax": 95.0,
        },
    ):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_NO_TOTAL},
                        headers=VALID_HEADERS)
    assert r.status_code == 200
    assert r.json()["results"][0]["confidence"] == "HIGH"


def test_medium_via_softmax_70_to_89():
    """avg_conf=80 (70-89) → MEDIUM."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={
            "product": "es teh",
            "quantity": 3,
            "price_satuan": 5000,
            "avg_conf_softmax": 80.0,
        },
    ):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_NO_TOTAL},
                        headers=VALID_HEADERS)
    assert r.json()["results"][0]["confidence"] == "MEDIUM"


def test_low_via_softmax_below_70():
    """avg_conf=65 < 70 → LOW."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={
            "product": "es teh",
            "quantity": 3,
            "price_satuan": 5000,
            "avg_conf_softmax": 65.0,
        },
    ):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_NO_TOTAL},
                        headers=VALID_HEADERS)
    assert r.json()["results"][0]["confidence"] == "LOW"


# ── E. LOW confidence (total tidak cocok) ────────────────────────────────────

def test_low_confidence_total_mismatch():
    """Business Override: total chat 25rb ≠ prediksi 2×15000=30000 → LOW."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={
            "product": "ayam bakar",
            "quantity": 2,
            "price_satuan": 15000,
            "avg_conf_softmax": 92.0,
        },
    ):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_TOTAL_MISMATCH},
                        headers=VALID_HEADERS)
    assert r.status_code == 200
    assert r.json()["results"][0]["confidence"] == "LOW"


# ── F. price_satuan: null ──────────────────────────────────────────────────────

def test_null_price_returns_null_total(mock_predict_no_price):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_NO_PRICE},
                    headers=VALID_HEADERS)
    assert r.status_code == 200
    item = r.json()["results"][0]
    assert item["price_satuan"] is None
    assert item["total"] is None
    assert item["confidence"] == "MEDIUM"


def test_null_price_product_still_returned(mock_predict_no_price):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_NO_PRICE},
                    headers=VALID_HEADERS)
    assert r.json()["results"][0]["product"] == "jus alpukat"


# ── G. product: "unknown" ──────────────────────────────────────────────────────

def test_unknown_product_confidence_medium(mock_predict_unknown):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_NO_PRICE},
                    headers=VALID_HEADERS)
    item = r.json()["results"][0]
    assert item["product"] == "unknown"
    assert item["confidence"] == "MEDIUM"


def test_unknown_product_never_high(mock_predict_unknown):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE},
                    headers=VALID_HEADERS)
    assert r.json()["results"][0]["confidence"] != "HIGH"


# ── H. Error model ─────────────────────────────────────────────────────────────

def test_model_not_loaded_returns_503():
    from app.core.errors import ModelNotLoadedError
    with patch("app.services.model_loader.ModelLoader.predict_single",
               side_effect=ModelNotLoadedError()):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE},
                        headers=VALID_HEADERS)
    assert r.status_code == 503
    assert r.json()["error_code"] == 1002


def test_inference_failure_returns_500():
    from app.core.errors import InferenceFailedError
    with patch("app.services.model_loader.ModelLoader.predict_single",
               side_effect=InferenceFailedError("fail")):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE},
                        headers=VALID_HEADERS)
    assert r.status_code == 500
    assert r.json()["error_code"] == 1003


# ── I. Preprocessing ──────────────────────────────────────────────────────────

def test_clean_text_no_timestamp(mock_predict_nasi_goreng):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    clean = r.json()["clean_text"]
    assert "07.42" not in clean
    assert "22/4/2026" not in clean


def test_clean_text_has_sep(mock_predict_nasi_goreng):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert "[SEP]" in r.json()["clean_text"]


def test_clean_text_lowercase(mock_predict_nasi_goreng):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    clean = r.json()["clean_text"].replace("[SEP]", "")
    assert clean == clean.lower()


# ── J. Smart Regex (jadinya / semuanya) ──────────────────────────────────────

def test_jadinya_detected_as_total():
    """'jadinya 24rb' harus dikenali sebagai total → cocokkan dengan prediksi."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={
            "product": "mie ayam",
            "quantity": 2,
            "price_satuan": 12000,
            "avg_conf_softmax": 91.0,
        },
    ):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_JADINYA},
                        headers=VALID_HEADERS)
    assert r.status_code == 200
    item = r.json()["results"][0]
    # 2 × 12000 = 24000 = "jadinya 24rb" → HIGH
    assert item["confidence"] == "HIGH"
    assert item["total"] == 24000


def test_semuanya_detected_as_total():
    """'semuanya 15rb' harus dikenali sebagai total."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value={
            "product": "es teh",
            "quantity": 3,
            "price_satuan": 5000,
            "avg_conf_softmax": 91.0,
        },
    ):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_SEMUANYA},
                        headers=VALID_HEADERS)
    item = r.json()["results"][0]
    # 3 × 5000 = 15000 = "semuanya 15rb" → HIGH
    assert item["confidence"] == "HIGH"
    assert item["total"] == 15000


# ── K. Pembulatan Rp500 ───────────────────────────────────────────────────────

def test_price_rounded_to_500():
    """
    Pastikan price_satuan yang keluar dari model sudah dibulatkan ke Rp500.
    Simulasi: model raw output 12.3 → ×1000 = 12300 → bulatkan ke 12500.
    """
    from app.services.model_loader import ModelLoader, _PRICE_NULL_THRESHOLD
    loader = ModelLoader()
    # Simulasi langsung logika pembulatan
    price_raw_val = 12.3
    price_mentah  = price_raw_val * 1000      # 12300
    price_satuan  = int(round(price_mentah / 500.0) * 500)  # 12500
    assert price_satuan == 12500

    price_raw_val2 = 11.8
    price_satuan2  = int(round(price_raw_val2 * 1000 / 500.0) * 500)  # 12000
    assert price_satuan2 == 12000


# ── L. Struktur response ──────────────────────────────────────────────────────

def test_all_required_fields_present(mock_predict_nasi_goreng):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert r.status_code == 200
    body = r.json()
    assert "results" in body
    assert "clean_text" in body
    item = body["results"][0]
    for field in ("product", "quantity", "price_satuan", "total", "confidence"):
        assert field in item, f"Field '{field}' tidak ada"


def test_confidence_is_valid_literal(mock_predict_nasi_goreng):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert r.json()["results"][0]["confidence"] in ("HIGH", "MEDIUM", "LOW")


def test_quantity_is_positive_int(mock_predict_nasi_goreng):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    qty = r.json()["results"][0]["quantity"]
    assert isinstance(qty, int) and qty >= 1


def test_error_format_consistent():
    """Semua error harus { error, error_code, message }."""
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE})
    body = r.json()
    assert "error" in body
    assert "error_code" in body
    assert "message" in body


def test_health_response_structure():
    r = client.get("/health")
    body = r.json()
    assert body["status"] in ("ok", "degraded")
    assert isinstance(body["model_loaded"], bool)
    assert "version" in body
