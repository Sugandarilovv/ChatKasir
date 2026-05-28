"""
Unit tests khusus untuk modul pipa Preprocessing & Postprocessing — ChatKasir API-2 (Versi Final V2).
Semua pengujian menggunakan teknik patching kamus slang tiruan tanpa bergantung pada disk asli.
"""

from unittest.mock import patch
import pytest

from app.services.processing import (
    prepare_model_input,
    postprocess,
    validate_input_length
)

# Kamus Slang tiruan untuk pengujian visualisasi lookup
MOCK_SLANG = {
    "nasgor": "nasi goreng",
    "mie grg": "mie goreng",
    "esteh": "es teh"
}

#  1. TESTING PIPELINE: prepare_model_input()
class TestPrepareModelInput:

    def test_universal_regex_timestamp_stripping(self):
        """Memastikan segala format timestamp WhatsApp dibersihkan tanpa sisa."""
        raw_chats = [
            "[28/05, 05:26] Rifan: order nasi goreng",
            "26/05/2026, 1:45 pm - Pelanggan_1: order nasi goreng",
            "26 Mei 2026 19.30 - +62 899-1111: order nasi goreng",
            "[27/05/2026, 09.15.22 AM] +628123: order nasi goreng"
        ]
        
        with patch("app.services.processing.load_slang_dict", return_value={}):
            for chat in raw_chats:
                result = prepare_model_input(chat)
                assert "05:26" not in result
                assert "2026" not in result
                assert "pm" not in result
                assert "order nasi goreng" in result

    def test_noise_sapaan_words_removal(self):
        """Memastikan kata sapaan pengisi (noise tokens) dipangkas bersih."""
        raw_chat = "[28/05, 05:26] Pembeli: halo admin mas bro bang pesan nasi goreng ya kak"
        with patch("app.services.processing.load_slang_dict", return_value={}):
            result = prepare_model_input(raw_chat)
        
        # Kata sapaan pengisi harus hilang dari korpus input model
        for kata_bising in ["halo", "admin", "mas", "bro", "bang", "kak", "ya"]:
            assert kata_bising not in result.split()
        assert "pesan nasi goreng" in result

    def test_domain_separation_with_sep_token(self):
        """Memastikan chat multi-baris pembeli-penjual dipisahkan oleh token [SEP]."""
        raw_chat = (
            "[28/05, 05:26] Rifan: pesan 2 nasgor\n"
            "[28/05, 06:01] Alfan: siap harganya 20k"
        )
        with patch("app.services.processing.load_slang_dict", return_value=MOCK_SLANG):
            result = prepare_model_input(raw_chat)
            
        assert "[SEP]" in result
        parts = result.split(" [SEP] ")
        assert len(parts) == 2
        assert "2 nasi goreng" in parts[0]
        assert "harga 20000" in parts[1]

    def test_currency_and_multiplier_normalization(self):
        """Memastikan singkatan nominal komersial ditranslasikan ke digit murni."""
        raw_chat = "Ayam bakar Rp 35k katering besar harganya 1.5jt"
        with patch("app.services.processing.load_slang_dict", return_value={}):
            result = prepare_model_input(raw_chat)
            
        assert "rp" not in result
        assert "35000" in result
        assert "1500000" in result

#  2. TESTING POST-PIPELINE: postprocess()
class TestPostprocess:

    def test_subtotal_calculation_and_key_mapping_contract(self):
        """Memastikan key mematuhi kontrak product_name & subtotal terhitung akurat."""
        output_ai = [{"product": "Ayam Bakar Madu", "quantity": 2, "price_satuan": 15000, "avg_conf_softmax": 95.0}]
        teks_bersih = "pesan ayam bakar madu 2 porsi [SEP] harga 15000 total tagihan 30000"
        
        result = postprocess(output_ai, teks_bersih)[0]
        
        assert "product_name" in result
        assert "subtotal" in result
        assert result["product_name"] == "Ayam Bakar Madu"
        assert result["subtotal"] == 30000
        assert result["confidence"] == "HIGH"

    def test_confidence_flag_resolution(self):
        """Memastikan bendera logika penentuan confidence bekerja secara akurat."""
        output_ai = [{"product": "Es Jeruk", "quantity": 2, "price_satuan": 5000, "avg_conf_softmax": 95.0}]
        
        # Kasus A: Total Nota Cocok -> HIGH
        res_high = postprocess(output_ai, "es jeruk 2 [SEP] harga 5000 totalnya 10000")[0]
        assert res_high["confidence"] == "HIGH"
        
        # Kasus B: Total Nota Meleset/Salah -> LOW
        res_low = postprocess(output_ai, "es jeruk 2 [SEP] harga 5000 total harganya 15000")[0]
        assert res_low["confidence"] == "LOW"
        
        # Kasus C: Tidak ada total di chat -> MEDIUM (Jika harga tidak disebutkan)
        output_no_price = [{"product": "Es Jeruk", "quantity": 2, "price_satuan": None, "avg_conf_softmax": 95.0}]
        res_medium = postprocess(output_no_price, "es jeruk 2 porsi cek harganya")[0]
        assert res_medium["confidence"] == "MEDIUM"

#  3. TESTING VALIDATION: validate_input_length()
class TestValidateInputLength:

    def test_valid_input_passes(self):
        # Teks aman di atas atau sama dengan 5 karakter tidak boleh melempar eksepsi
        validate_input_length("order mi")

    def test_invalid_input_throws_custom_error(self):
        from app.core.errors import InvalidInputError
        with pytest.raises(InvalidInputError):
            validate_input_length("p")