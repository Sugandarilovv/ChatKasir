"""
Integration tests untuk POST /predict dan GET /health — ChatKasir API-2 (Versi Sinkron V2).
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

# Blok proteksi patcher agar module main.app bisa di-import aman tanpa TensorFlow terpasang di CI
with (
    patch("app.services.model_loader.ModelLoader._load_model"),
    patch("app.services.preprocessing.load_slang_dict", return_value={}),
):
    from app.main import app

client = TestClient(app, raise_server_exceptions=False)
VALID_HEADERS = {"X-API-Key": "changeme"}

# ── Payload Fixtures (Menggunakan Simulasi Percakapan Riil V2) ────────────────

RAW_CHAT_SIMPLE = (
    "[28/05, 05:26] Rifan: order paket ayam bakar madu 10 pack\n"
    "[28/05, 06:01] Alfan: siap harganya 35k totalnya 350000 ya"
)
RAW_CHAT_JADINYA = (
    "[08.00, 22/04] Pembeli Lama: pesan 2 mie ayam\n"
    "[08.01, 22/04] Kasir: oke kak jadinya 24000 ya"
)
RAW_CHAT_SEMUANYA = (
    "26/05/2026, 1:45 pm - Pelanggan_1: mau 3 es teh\n"
    "26/05/2026, 1:47 pm - Admin: semuanya 15k kak"
)
RAW_CHAT_NO_TOTAL = (
    "[27/05/2026, 09.15.22 AM] +628123456789: pesan 3 es teh\n"
    "[27/05/2026, 09.16.00 AM] Admin: oke es teh 5ribu ya"
)
RAW_CHAT_TOTAL_MISMATCH = (
    "05/26/26, 22:10 - Pembeli Lama Banget: mau 2 ayam bakar\n"
    "05/26/26, 22:12 - Penjual: ayam bakar 15000 totalnya 25000 ya"
)
RAW_CHAT_NO_PRICE = (
    "26 Mei 2026 19.30 - +62 899-1111-2222: pesan 1 jus alpukat\n"
    "26 Mei 2026 19.32 - Admin: oke nanti saya cek harganya"
)


# ── Fixtures Moking Saraf AI ──────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_model_loaded():
    with (
        patch("app.services.model_loader.ModelLoader._model", MagicMock()),
        patch("app.services.model_loader.ModelLoader._tokenizer", MagicMock()),
        patch("app.services.model_loader.ModelLoader.is_loaded", return_value=True),
    ):
        yield


@pytest.fixture
def mock_predict_ayam_bakar():
    """qty=10, price=35000 → subtotal=350000 → cocok dengan total chat → HIGH."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value=[{
            "product": "Ayam Bakar Madu",  # Key internal model loader tetap 'product'
            "quantity": 10,
            "price_satuan": 35000,
            "avg_conf_softmax": 98.5,
        }],
    ):
        yield


@pytest.fixture
def mock_predict_no_price():
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value=[{
            "product": "jus alpukat",
            "quantity": 1,
            "price_satuan": None,
            "avg_conf_softmax": 88.0,
        }],
    ):
        yield


@pytest.fixture
def mock_predict_unknown():
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value=[{
            "product": "unknown",
            "quantity": 1,
            "price_satuan": None,
            "avg_conf_softmax": 0.0,
        }],
    ):
        yield


# ── A. Autentikasi Security ───────────────────────────────────────────────────

def test_missing_api_key(mock_predict_ayam_bakar):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE})
    assert r.status_code == 401
    assert r.json()["error_code"] == 4010


def test_wrong_api_key(mock_predict_ayam_bakar):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers={"X-API-Key": "wrong"})
    assert r.status_code == 401


def test_health_no_auth():
    r = client.get("/health")
    assert r.status_code == 200


# ── B. Validasi Karakter Input ────────────────────────────────────────────────

def test_missing_raw_text():
    r = client.post("/predict", json={}, headers=VALID_HEADERS)
    assert r.status_code == 422
    assert r.json()["error_code"] == 1001


def test_too_short_input_validation():
    r = client.post("/predict", json={"raw_text": "abcd"}, headers=VALID_HEADERS)
    assert r.status_code == 422
    assert r.json()["error_code"] == 1001


def test_empty_string_validation():
    r = client.post("/predict", json={"raw_text": "   "}, headers=VALID_HEADERS)
    assert r.status_code == 422
    assert r.json()["error_code"] == 1001


# ── C. HIGH Confidence Skenario ───────────────────────────────────────────────

def test_high_confidence_when_total_matches(mock_predict_ayam_bakar):
    """Business Logic: Nota chat 350000 == perkalian AI 10×35000 -> HIGH."""
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert r.status_code == 200
    
    body = r.json()
    assert body["status"] == "success"
    assert body["total_akumulasi"] == 350000
    
    item = body["results"][0]
    assert item["confidence"] == "HIGH"
    assert item["product_name"] == "Ayam Bakar Madu"  # 🌟 Diperbarui ke product_name
    assert item["quantity"] == 10
    assert item["price_satuan"] == 35000
    assert item["subtotal"] == 350000                 # 🌟 Diperbarui ke subtotal


def test_subtotal_calculation_accuracy(mock_predict_ayam_bakar):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    item = r.json()["results"][0]
    assert item["subtotal"] == item["quantity"] * item["price_satuan"]


# ── D. MEDIUM / Softmax Fallback ──────────────────────────────────────────────

def test_high_via_softmax_when_no_total_in_chat():
    """Tanpa total di chat, nilai key conf >= 90.0% -> HIGH."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value=[{
            "product": "es teh",
            "quantity": 3,
            "price_satuan": 5000,
            "avg_conf_softmax": 95.0,
        }],
    ):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_NO_TOTAL}, headers=VALID_HEADERS)
    assert r.status_code == 200
    assert r.json()["results"][0]["confidence"] == "HIGH"


def test_medium_via_softmax_fallback_zone():
    """Nilai key conf antara 70% s/d 89% -> MEDIUM."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value=[{
            "product": "es teh",
            "quantity": 3,
            "price_satuan": 5000,
            "avg_conf_softmax": 80.0,
        }],
    ):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_NO_TOTAL}, headers=VALID_HEADERS)
    assert r.json()["results"][0]["confidence"] == "MEDIUM"


# ── E. LOW Confidence (Total Nota Mismatch) ───────────────────────────────────

def test_low_confidence_total_mismatch():
    """Klaim chat penjual 25k != Kalkulasi AI 2×15000=30000 -> LOW."""
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value=[{
            "product": "ayam bakar",
            "quantity": 2,
            "price_satuan": 15000,
            "avg_conf_softmax": 92.0,
        }],
    ):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_TOTAL_MISMATCH}, headers=VALID_HEADERS)
    assert r.status_code == 200
    assert r.json()["results"][0]["confidence"] == "LOW"


# ── F. Edge Case: Price Satuan Null ───────────────────────────────────────────

def test_null_price_returns_null_subtotal(mock_predict_no_price):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_NO_PRICE}, headers=VALID_HEADERS)
    assert r.status_code == 200
    item = r.json()["results"][0]
    assert item["price_satuan"] is None
    assert item["subtotal"] is None
    assert item["confidence"] == "MEDIUM"


# ── G. Edge Case: Nama Produk Unknown ─────────────────────────────────────────

def test_unknown_product_handling(mock_predict_unknown):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_NO_PRICE}, headers=VALID_HEADERS)
    item = r.json()["results"][0]
    assert item["product_name"] == "unknown"
    assert item["confidence"] == "MEDIUM"


# ── H. Error Infrastructure Model Validation ──────────────────────────────────

def test_model_not_loaded_returns_503():
    from app.core.errors import ModelNotLoadedError
    with patch("app.services.model_loader.ModelLoader.predict_single", side_effect=ModelNotLoadedError()):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert r.status_code == 503
    assert r.json()["error_code"] == 1002


# ── I. Preprocessing & Pembersihan Teks Multi-OS ──────────────────────────────

def test_clean_text_universal_regex_stripping(mock_predict_ayam_bakar):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    clean = r.json()["clean_text"]
    assert "05:26" not in clean
    assert "28/05" not in clean
    assert "rifan" not in clean
    assert "[sep]" not in clean
    assert "[SEP]" in clean


# ── J. Smart Regex Exponent Multplier (Jadinya / Semuanya / Jutaan) ────────────

def test_jadinya_and_multiplier_detected():
    with patch(
        "app.services.model_loader.ModelLoader.predict_single",
        return_value=[{
            "product": "mie ayam",
            "quantity": 2,
            "price_satuan": 12000,
            "avg_conf_softmax": 91.0,
        }],
    ):
        r = client.post("/predict", json={"raw_text": RAW_CHAT_JADINYA}, headers=VALID_HEADERS)
    assert r.status_code == 200
    assert r.json()["results"][0]["confidence"] == "HIGH"
    assert r.json()["results"][0]["subtotal"] == 24000


# ── K. 🌟 [PENGGANTI PENUH LOGIKA 500]: Uji Parse Konversi Nominal Mutakhir ───

def test_exact_price_parsing_without_distortion():
    """Memastikan helper model_loader mem-parse exponen k/rb/jt secara presisi murni."""
    from app.services.model_loader import _parse_price_from_text, _parse_qty_from_text
    
    # 1. Tes Multiplier Jutaan Katering
    assert _parse_price_from_text("3.5jt") == 3500000
    assert _parse_price_from_text("13093000") == 13093000
    
    # 2. Tes Frase Kuantitas Multi-Kata
    assert _parse_qty_from_text("dua bungkus") == 2
    assert _parse_qty_from_text("lima mangkuk") == 5
    assert _parse_qty_from_text("10 pack") == 10


# ── L. Validasi Struktur Kontrak JSON Response Akhir ──────────────────────────

def test_all_required_contract_fields_present(mock_predict_ayam_bakar):
    r = client.post("/predict", json={"raw_text": RAW_CHAT_SIMPLE}, headers=VALID_HEADERS)
    assert r.status_code == 200
    body = r.json()
    
    # Verifikasi level root response
    assert "status" in body
    assert "results" in body
    assert "total_akumulasi" in body
    assert "clean_text" in body
    
    # Verifikasi level objek item internal
    item = body["results"][0]
    for field in ("product_name", "quantity", "price_satuan", "subtotal", "confidence"):
        assert field in item, f"Kontrak Field '{field}' bocor/tidak ditemukan!"


def test_health_route_degraded_status_compliance():
    """Jika model mati, /health WAJIB mengembalikan HTTP 503."""
    with patch("app.services.model_loader.ModelLoader.is_loaded", return_value=False):
        r = client.get("/health")
    assert r.status_code == 503
    assert r.json()["status"] == "degraded"