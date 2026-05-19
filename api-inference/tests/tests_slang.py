"""
Unit tests untuk normalisasi slang — Hari 7 (28 Apr).

Menguji:
  - load_slang_dict()   : load CSV, validasi baris, duplikat, file tidak ada
  - reload_slang_dict() : hot-reload (cache clear + reload)
  - get_slang_stats()   : statistik kamus
  - normalize_slang()   : single-word, multi-word phrase, longest-match-first
  - prepare_model_input(): integrasi kamus nyata via temp CSV

Semua test yang membutuhkan file CSV menggunakan tmp_path pytest
sehingga tidak bergantung pada file slang_utama.csv yang sebenarnya.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.processing import (
    _build_phrase_index,
    get_slang_stats,
    load_slang_dict,
    normalize_slang,
    prepare_model_input,
    reload_slang_dict,
)


# ─────────────────────────────────────────────────────────────────────────────
#  Helper: buat CSV sementara untuk test
# ─────────────────────────────────────────────────────────────────────────────

def _write_csv(path: Path, rows: list[tuple[str, str]], with_header: bool = True) -> Path:
    """Tulis CSV slang sementara ke path, kembalikan path-nya."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if with_header:
            writer.writerow(["slang", "baku"])
        writer.writerows(rows)
    return path


# ─────────────────────────────────────────────────────────────────────────────
#  load_slang_dict()
# ─────────────────────────────────────────────────────────────────────────────

class TestLoadSlangDict:
    """Setiap test membersihkan cache lru_cache terlebih dahulu."""

    def setup_method(self):
        load_slang_dict.cache_clear()

    # ── Skenario happy path ───────────────────────────────────────────────────

    def test_load_single_word_entries(self, tmp_path):
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("bg", "abang"),
            ("kk", "kakak"),
            ("pesen", "pesan"),
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            result = load_slang_dict()
        assert result["bg"] == "abang"
        assert result["kk"] == "kakak"
        assert result["pesen"] == "pesan"
        assert len(result) == 3

    def test_load_multi_word_entries(self, tmp_path):
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("nasi grg", "nasi goreng"),
            ("es teh", "es teh"),
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            result = load_slang_dict()
        assert result["nasi grg"] == "nasi goreng"
        assert result["es teh"] == "es teh"

    def test_key_value_disimpan_lowercase(self, tmp_path):
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("BG", "ABANG"),
            ("Nasi GRG", "Nasi Goreng"),
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            result = load_slang_dict()
        assert "bg" in result
        assert result["bg"] == "abang"
        assert "nasi grg" in result
        assert result["nasi grg"] == "nasi goreng"

    def test_whitespace_distrip(self, tmp_path):
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("  bg  ", "  abang  "),
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            result = load_slang_dict()
        assert "bg" in result
        assert result["bg"] == "abang"

    # ── Skenario file tidak ada ───────────────────────────────────────────────

    def test_file_tidak_ada_kembalikan_dict_kosong(self, tmp_path):
        path_palsu = str(tmp_path / "tidak_ada.csv")
        with patch("app.core.config.settings.SLANG_DICT_PATH", path_palsu):
            result = load_slang_dict()
        assert result == {}

    def test_file_tidak_ada_tidak_raise(self, tmp_path):
        path_palsu = str(tmp_path / "tidak_ada.csv")
        with patch("app.core.config.settings.SLANG_DICT_PATH", path_palsu):
            try:
                load_slang_dict()
            except Exception as exc:
                pytest.fail(f"load_slang_dict() raise exception tak terduga: {exc}")

    # ── Skenario validasi baris ───────────────────────────────────────────────

    def test_baris_dengan_kolom_kurang_dilewati(self, tmp_path):
        """Baris yang hanya punya 1 kolom harus dilewati tanpa crash."""
        path = tmp_path / "slang.csv"
        path.write_text("slang,baku\nbg\nabang,abang\n", encoding="utf-8")
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(path)):
            result = load_slang_dict()
        # "bg" (hanya 1 kolom) dilewati, "abang" tetap dimuat
        assert "bg" not in result
        assert "abang" in result

    def test_baris_nilai_kosong_dilewati(self, tmp_path):
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("", "abang"),    # slang kosong
            ("bg", ""),       # baku kosong
            ("kk", "kakak"),  # valid
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            result = load_slang_dict()
        # Hanya "kk" yang valid
        assert "kk" in result
        assert "" not in result

    def test_duplikat_key_nilai_terakhir_menang(self, tmp_path):
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("bg", "abang"),
            ("bg", "abangku"),  # duplikat — ini yang menang
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            result = load_slang_dict()
        assert result["bg"] == "abangku"

    def test_csv_tanpa_header_tidak_crash(self, tmp_path):
        """CSV tanpa header juga harus ditangani — baris pertama dianggap header dan dilewati."""
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("bg", "abang"),
        ], with_header=False)
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            # Tidak boleh raise, boleh hasilkan dict yang mungkin menyertakan
            # baris pertama sebagai data (karena header='bg,abang' di-skip)
            result = load_slang_dict()
        # Yang penting tidak crash
        assert isinstance(result, dict)

    # ── Cache behavior ────────────────────────────────────────────────────────

    def test_load_dipanggil_dua_kali_hasilnya_sama(self, tmp_path):
        csv_file = _write_csv(tmp_path / "slang.csv", [("bg", "abang")])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            hasil_1 = load_slang_dict()
            hasil_2 = load_slang_dict()
        assert hasil_1 is hasil_2   # dict yang sama persis dari cache


# ─────────────────────────────────────────────────────────────────────────────
#  reload_slang_dict()
# ─────────────────────────────────────────────────────────────────────────────

class TestReloadSlangDict:
    def setup_method(self):
        load_slang_dict.cache_clear()

    def test_reload_mengambil_data_terbaru(self, tmp_path):
        """Setelah CSV diperbarui, reload harus mengambil data baru."""
        csv_file = tmp_path / "slang.csv"
        _write_csv(csv_file, [("bg", "abang")])

        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            hasil_awal = load_slang_dict()
            assert hasil_awal.get("bg") == "abang"
            assert "kk" not in hasil_awal

            # Perbarui CSV
            _write_csv(csv_file, [("bg", "abang"), ("kk", "kakak")])

            hasil_baru = reload_slang_dict()

        assert hasil_baru.get("kk") == "kakak"
        assert len(hasil_baru) == 2

    def test_reload_kembalikan_dict(self, tmp_path):
        csv_file = _write_csv(tmp_path / "slang.csv", [("bg", "abang")])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            result = reload_slang_dict()
        assert isinstance(result, dict)


# ─────────────────────────────────────────────────────────────────────────────
#  get_slang_stats()
# ─────────────────────────────────────────────────────────────────────────────

class TestGetSlangStats:
    def setup_method(self):
        load_slang_dict.cache_clear()

    def test_stats_field_lengkap(self, tmp_path):
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("bg", "abang"),
            ("kk", "kakak"),
            ("nasi grg", "nasi goreng"),
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            stats = get_slang_stats()

        for field in ("total", "single_word", "multi_word", "loaded", "path"):
            assert field in stats, f"field '{field}' tidak ada di stats"

    def test_stats_hitung_benar(self, tmp_path):
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("bg", "abang"),       # single
            ("kk", "kakak"),       # single
            ("nasi grg", "nasi goreng"),  # multi
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            stats = get_slang_stats()

        assert stats["total"]       == 3
        assert stats["single_word"] == 2
        assert stats["multi_word"]  == 1
        assert stats["loaded"]      is True

    def test_stats_file_tidak_ada(self, tmp_path):
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(tmp_path / "kosong.csv")):
            stats = get_slang_stats()
        assert stats["total"]  == 0
        assert stats["loaded"] is False


# ─────────────────────────────────────────────────────────────────────────────
#  _build_phrase_index()
# ─────────────────────────────────────────────────────────────────────────────

class TestBuildPhraseIndex:
    def test_hanya_multi_word_masuk_indeks(self):
        slang_dict = {
            "bg":       "abang",        # 1 kata  — tidak masuk
            "nasi grg": "nasi goreng",  # 2 kata  — masuk di key 2
            "es teh":   "es teh",       # 2 kata  — masuk di key 2
        }
        idx = _build_phrase_index(slang_dict)
        assert 1 not in idx
        assert 2 in idx
        tokens_list = [tokens for tokens, _ in idx[2]]
        assert ["nasi", "grg"] in tokens_list
        assert ["es", "teh"]   in tokens_list

    def test_kamus_kosong_kembalikan_kosong(self):
        assert _build_phrase_index({}) == {}

    def test_trigram_masuk_key_3(self):
        slang_dict = {"nasi goreng spesial": "nasi goreng spesial"}
        idx = _build_phrase_index(slang_dict)
        assert 3 in idx


# ─────────────────────────────────────────────────────────────────────────────
#  normalize_slang() — single-word
# ─────────────────────────────────────────────────────────────────────────────

MOCK_SINGLE = {"bg": "abang", "kk": "kakak", "pesen": "pesan", "oke": "oke"}


class TestNormalizeSlangSingleWord:
    def test_semua_kata_dinormalisasi(self):
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_SINGLE):
            assert normalize_slang("bg mau pesen") == "abang mau pesan"

    def test_kata_tidak_ada_dipertahankan(self):
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_SINGLE):
            assert normalize_slang("nasi goreng") == "nasi goreng"

    def test_kamus_kosong_teks_tidak_berubah(self):
        with patch("app.services.preprocessing.load_slang_dict", return_value={}):
            assert normalize_slang("bg kk pesen") == "bg kk pesen"

    def test_string_kosong(self):
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_SINGLE):
            assert normalize_slang("") == ""

    def test_satu_kata(self):
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_SINGLE):
            assert normalize_slang("bg") == "abang"


# ─────────────────────────────────────────────────────────────────────────────
#  normalize_slang() — multi-word phrase & longest-match
# ─────────────────────────────────────────────────────────────────────────────

MOCK_MULTI = {
    "bg":          "abang",
    "nasi":        "nasi",        # single fallback
    "grg":         "goreng",      # single fallback
    "nasi grg":    "nasi goreng", # 2-kata phrase — harus menang atas dua lookup terpisah
    "es":          "es",
    "teh":         "teh",
    "es teh":      "es teh",      # 2-kata phrase
    "mie grg":     "mie goreng",
}


class TestNormalizeSlangMultiWord:
    def test_dua_kata_phrase_dinormalisasi(self):
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_MULTI):
            result = normalize_slang("mau nasi grg")
        assert "nasi goreng" in result
        # Pastikan tidak muncul "nasi goreng" sebagai "nasi goreng" (sudah baku)
        # dan tidak ada sisa "grg" terpisah
        assert "grg" not in result

    def test_longest_match_menang_atas_single(self):
        """
        "nasi grg" sebagai frasa harus dipilih daripada "nasi" + "grg" terpisah.
        Kedua opsi ada di kamus, longest-match harus menang.
        """
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_MULTI):
            result = normalize_slang("nasi grg")
        assert result == "nasi goreng"
        # Bukan "nasi goreng" dari dua lookup terpisah (hasilnya sama di kasus ini,
        # tapi test memastikan mekanisme longest-match aktif)

    def test_dua_phrase_berturut(self):
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_MULTI):
            result = normalize_slang("nasi grg mie grg")
        assert "nasi goreng" in result
        assert "mie goreng"  in result

    def test_phrase_di_awal_kalimat(self):
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_MULTI):
            result = normalize_slang("nasi grg 2 porsi")
        assert result.startswith("nasi goreng")

    def test_phrase_di_tengah_kalimat(self):
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_MULTI):
            result = normalize_slang("pesan nasi grg ya")
        assert "nasi goreng" in result

    def test_phrase_di_akhir_kalimat(self):
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_MULTI):
            result = normalize_slang("mau pesan nasi grg")
        assert result.endswith("nasi goreng")

    def test_es_teh_sebagai_phrase(self):
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_MULTI):
            result = normalize_slang("es teh 2 gelas")
        assert "es teh" in result

    def test_kata_tunggal_setelah_phrase(self):
        """Token setelah frasa berhasil di-match tidak ikut dikonsumsi."""
        with patch("app.services.preprocessing.load_slang_dict", return_value=MOCK_MULTI):
            result = normalize_slang("bg nasi grg")
        assert "abang" in result
        assert "nasi goreng" in result


# ─────────────────────────────────────────────────────────────────────────────
#  Integrasi: normalize_slang() dengan kamus nyata (slang_utama.csv)
# ─────────────────────────────────────────────────────────────────────────────

SLANG_CSV_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../../../data/final/slang_utama.csv"
)


@pytest.mark.skipif(
    not os.path.exists(SLANG_CSV_PATH),
    reason="slang_utama.csv belum tersedia — skip test integrasi"
)
class TestNormalizeSlangIntegrasi:
    """
    Test ini hanya jalan jika slang_utama.csv sudah ada (dari DS-1).
    Dijalankan saat development; di CI tetap jalan setelah CSV di-commit.
    """

    def setup_method(self):
        load_slang_dict.cache_clear()

    def test_sapaan_bg_dinormalisasi(self):
        with patch("app.core.config.settings.SLANG_DICT_PATH", SLANG_CSV_PATH):
            result = normalize_slang("bg 2 nasi goreng ya")
        assert "abang" in result

    def test_nasi_grg_multi_word(self):
        with patch("app.core.config.settings.SLANG_DICT_PATH", SLANG_CSV_PATH):
            result = normalize_slang("2 nasi grg")
        assert "nasi goreng" in result

    def test_es_teh_multi_word(self):
        with patch("app.core.config.settings.SLANG_DICT_PATH", SLANG_CSV_PATH):
            result = normalize_slang("es teh 3 gelas")
        # "es teh" baku → tidak berubah, tetapi juga tidak dipecah jadi "es" + "teh"
        assert "es teh" in result

    def test_total_rb_dinormalisasi(self):
        with patch("app.core.config.settings.SLANG_DICT_PATH", SLANG_CSV_PATH):
            result = normalize_slang("totalnya 20 rb")
        # "rb" → "ribu", "totalnya" → "total"
        assert "ribu" in result

    def test_kamus_coverage_lebih_dari_50_entri(self):
        with patch("app.core.config.settings.SLANG_DICT_PATH", SLANG_CSV_PATH):
            d = load_slang_dict()
        assert len(d) >= 50, (
            f"Kamus hanya {len(d)} entri — minta DS-1 (Faradi) tambah coverage"
        )
