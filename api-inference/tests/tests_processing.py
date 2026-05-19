"""
Unit tests untuk fungsi-fungsi preprocessing dasar — Hari 6 (27 Apr).

Menguji:
  - lowercase()
  - remove_special_chars()
  - split_sentences()
  - normalize_slang()
  - parse_whatsapp_chat()
  - prepare_model_input()  (pipeline penuh)

Semua test TIDAK membutuhkan model Keras, tokenizer, atau file CSV nyata.
Kamus slang di-mock langsung di dalam setiap test yang membutuhkannya.
"""

from unittest.mock import patch

import pytest

from app.services.processing import (
    lowercase,
    normalize_slang,
    parse_whatsapp_chat,
    postprocess,
    prepare_model_input,
    remove_special_chars,
    split_sentences,
)


# ─────────────────────────────────────────────────────────────────────────────
#  lowercase()
# ─────────────────────────────────────────────────────────────────────────────

class TestLowercase:
    def test_semua_huruf_besar(self):
        assert lowercase("NASI GORENG") == "nasi goreng"

    def test_campuran(self):
        assert lowercase("Bang 2 Nasi Goreng YA") == "bang 2 nasi goreng ya"

    def test_sudah_lowercase(self):
        assert lowercase("nasi goreng") == "nasi goreng"

    def test_angka_tidak_berubah(self):
        assert lowercase("2 Es Teh") == "2 es teh"

    def test_string_kosong(self):
        assert lowercase("") == ""


# ─────────────────────────────────────────────────────────────────────────────
#  remove_special_chars()
# ─────────────────────────────────────────────────────────────────────────────

class TestRemoveSpecialChars:
    def test_hapus_tanda_seru(self):
        assert remove_special_chars("bang!! 2 nasi goreng") == "bang 2 nasi goreng"

    def test_hapus_titik_koma(self):
        assert remove_special_chars("total: 20000") == "total 20000"

    def test_titik_ribuan_dihapus(self):
        # "20.000" -> "20000" karena titik dibuang
        assert remove_special_chars("total 20000") == "total 20000"

    def test_hapus_tanda_tanya(self):
        assert remove_special_chars("ada nasi goreng?") == "ada nasi goreng"

    def test_spasi_ganda_dirapikan(self):
        result = remove_special_chars("nasi  goreng")
        assert "  " not in result

    def test_angka_dipertahankan(self):
        assert remove_special_chars("2 nasi goreng 10000") == "2 nasi goreng 10000"

    def test_huruf_dipertahankan(self):
        result = remove_special_chars("nasi goreng")
        assert result == "nasi goreng"

    def test_string_kosong(self):
        assert remove_special_chars("") == ""

    def test_strip_spasi_tepi(self):
        assert remove_special_chars("  nasi goreng  ") == "nasi goreng"


# ─────────────────────────────────────────────────────────────────────────────
#  split_sentences()
# ─────────────────────────────────────────────────────────────────────────────

class TestSplitSentences:
    def test_satu_kalimat(self):
        result = split_sentences("mau pesan 2 nasi goreng")
        assert result == ["mau pesan 2 nasi goreng"]

    def test_dua_kalimat_titik(self):
        result = split_sentences("mau pesan 2 nasi goreng. sama 1 es teh ya")
        assert len(result) == 2
        assert result[0] == "mau pesan 2 nasi goreng"
        assert result[1] == "sama 1 es teh ya"

    def test_dua_kalimat_newline(self):
        result = split_sentences("2 nasi goreng\n1 es teh")
        assert len(result) == 2
        assert "2 nasi goreng" in result
        assert "1 es teh" in result

    def test_kalimat_tanda_seru(self):
        result = split_sentences("ok kak! segera disiapkan")
        assert len(result) == 2

    def test_filter_kalimat_kosong(self):
        result = split_sentences("nasi goreng... ")
        # kalimat kosong hasil split harus dibuang
        assert all(s != "" for s in result)

    def test_string_kosong(self):
        result = split_sentences("")
        assert result == []


# ─────────────────────────────────────────────────────────────────────────────
#  normalize_slang()
# ─────────────────────────────────────────────────────────────────────────────

MOCK_SLANG = {
    "bg": "abang",
    "psnnn": "pesan",
    "grngg": "goreng",
    "kak": "kakak",
}


class TestNormalizeSlang:
    def test_kata_ada_di_kamus(self):
        with patch("app.services.processing.load_slang_dict", return_value=MOCK_SLANG):
            result = normalize_slang("bg mau psnnn nasi grngg")
        assert result == "abang mau pesan nasi goreng"

    def test_kata_tidak_ada_di_kamus_dipertahankan(self):
        with patch("app.services.processing.load_slang_dict", return_value=MOCK_SLANG):
            result = normalize_slang("mau nasi goreng")
        assert result == "mau nasi goreng"

    def test_kamus_kosong_kembalikan_teks_asli(self):
        with patch("app.services.processing.load_slang_dict", return_value={}):
            result = normalize_slang("bg pesan nasi")
        assert result == "bg pesan nasi"

    def test_semua_kata_dinormalisasi(self):
        with patch("app.services.processing.load_slang_dict", return_value=MOCK_SLANG):
            result = normalize_slang("bg kak")
        assert result == "abang kakak"

    def test_string_kosong(self):
        with patch("app.services.processing.load_slang_dict", return_value=MOCK_SLANG):
            result = normalize_slang("")
        assert result == ""


# ─────────────────────────────────────────────────────────────────────────────
#  parse_whatsapp_chat()
# ─────────────────────────────────────────────────────────────────────────────

class TestParseWhatsappChat:
    def test_parse_pembeli_dan_penjual(self):
        raw = (
            "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya\n"
            "[07.44, 22/4/2026] Penjual: oke kak 10rb ya"
        )
        result = parse_whatsapp_chat(raw)
        assert result["pembeli"] == "bang 2 nasi goreng ya"
        assert result["penjual"] == "oke kak 10rb ya"

    def test_timestamp_dihapus(self):
        raw = "[09.00, 1/5/2026] Pembeli: pesan es teh"
        result = parse_whatsapp_chat(raw)
        assert "09.00" not in result["pembeli"]
        assert "1/5/2026" not in result["pembeli"]

    def test_multi_pesan_pembeli_digabung(self):
        raw = (
            "[07.42, 22/4/2026] Pembeli: bang\n"
            "[07.43, 22/4/2026] Pembeli: 2 nasi goreng ya"
        )
        result = parse_whatsapp_chat(raw)
        assert result["pembeli"] == "bang 2 nasi goreng ya"

    def test_tanpa_penjual(self):
        raw = "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya"
        result = parse_whatsapp_chat(raw)
        assert result["pembeli"] == "bang 2 nasi goreng ya"
        assert result["penjual"] == ""

    def test_tanpa_format_whatsapp(self):
        # Teks tanpa format timestamp → semua kunci kosong
        result = parse_whatsapp_chat("pesan nasi goreng")
        assert result["pembeli"] == ""
        assert result["penjual"] == ""


# ─────────────────────────────────────────────────────────────────────────────
#  prepare_model_input()  — pipeline penuh
# ─────────────────────────────────────────────────────────────────────────────

RAW_CHAT = (
    "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya\n"
    "[07.44, 22/4/2026] Penjual: oke kak 10rb totalnya 20rb ya"
)

RAW_CHAT_UPPERCASE = (
    "[07.42, 22/4/2026] Pembeli: BANG 2 NASI GORENG YA\n"
    "[07.44, 22/4/2026] Penjual: OKE KAK 10RB TOTALNYA 20RB YA"
)


class TestPrepareModelInput:
    def test_output_lowercase(self):
        with patch("app.services.processing.load_slang_dict", return_value={}):
            result = prepare_model_input(RAW_CHAT_UPPERCASE)
        assert result == result.lower()

    def test_timestamp_tidak_ada_di_output(self):
        with patch("app.services.processing.load_slang_dict", return_value={}):
            result = prepare_model_input(RAW_CHAT)
        assert "07.42" not in result
        assert "22/4/2026" not in result

    def test_sep_ada_di_output(self):
        with patch("app.services.processing.load_slang_dict", return_value={}):
            result = prepare_model_input(RAW_CHAT)
        assert "[SEP]" in result

    def test_pembeli_di_kiri_penjual_di_kanan(self):
        with patch("app.services.processing.load_slang_dict", return_value={}):
            result = prepare_model_input(RAW_CHAT)
        parts = result.split("[SEP]")
        assert len(parts) == 2
        assert "nasi goreng" in parts[0]
        assert "oke" in parts[1]

    def test_tanpa_penjual_tidak_ada_sep(self):
        raw = "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya"
        with patch("app.services.processing.load_slang_dict", return_value={}):
            result = prepare_model_input(raw)
        assert "[SEP]" not in result

    def test_slang_dinormalisasi(self):
        slang = {"bg": "abang"}
        raw = "[07.42, 22/4/2026] Pembeli: bg 2 nasi goreng ya"
        with patch("app.services.processing.load_slang_dict", return_value=slang):
            result = prepare_model_input(raw)
        assert "abang" in result
        assert "bg" not in result

    def test_tidak_ada_karakter_khusus_di_output(self):
        raw = (
            "[07.42, 22/4/2026] Pembeli: bang!! 2 nasi-goreng ya?\n"
            "[07.44, 22/4/2026] Penjual: oke kak: 10rb"
        )
        with patch("app.services.processing.load_slang_dict", return_value={}):
            result = prepare_model_input(raw)
        # Tidak boleh ada karakter selain a-z, 0-9, spasi, dan [SEP]
        import re
        tanpa_sep = result.replace("[SEP]", "")
        assert not re.search(r'[^a-z0-9\s]', tanpa_sep), (
            f"Masih ada karakter khusus di output: '{result}'"
        )


# ─────────────────────────────────────────────────────────────────────────────
#  postprocess()
# ─────────────────────────────────────────────────────────────────────────────

class TestPostprocess:
    def test_total_dihitung_benar(self):
        output = {"product": "nasi goreng", "quantity": 2, "price_satuan": 10000}
        # Masukkan output ke dalam list, lalu ambil indeks [0] dari hasilnya
        result = postprocess([output], "oke kak totalnya 20rb ya")[0]
        assert result["total"] == 20000

    def test_confidence_high_jika_total_cocok(self):
        output = {"product": "nasi goreng", "quantity": 2, "price_satuan": 10000}
        result = postprocess([output], "oke kak totalnya 20rb ya")[0]
        assert result["confidence"] == "HIGH"

    def test_confidence_low_jika_total_tidak_cocok(self):
        output = {"product": "nasi goreng", "quantity": 2, "price_satuan": 10000}
        result = postprocess([output], "oke kak totalnya 15rb ya")[0]
        assert result["confidence"] == "LOW"

    def test_confidence_medium_jika_tidak_ada_total(self):
        output = {"product": "es teh", "quantity": 3, "price_satuan": 5000}
        result = postprocess([output], "oke kak es teh ya")[0]
        assert result["confidence"] == "MEDIUM"

    def test_semua_field_ada_di_output(self):
        output = {"product": "nasi goreng", "quantity": 2, "price_satuan": 10000}
        result = postprocess([output], "totalnya 20rb")[0]
        for field in ("product", "quantity", "price_satuan", "total", "confidence"):
            assert field in result
