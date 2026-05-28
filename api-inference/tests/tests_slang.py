"""
Unit tests untuk validasi pengelolaan kamus slang dan normalisasinya — ChatKasir API-2 (Versi Final V2).

Menguji secara mendalam:
  - load_slang_dict()    : Memuat CSV, pembersihan huruf kecil, penanganan duplikat, dan toleransi file absen.
  - reload_slang_dict()  : Fungsi penyegaran cache otomatis (hot-swap).
  - get_slang_stats()    : Akurasi kalkulasi statistik kamus.
  - prepare_model_input(): Integrasi transformasi slang dalam pipa pembersihan teks utama.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.processing import (
    get_slang_stats,
    load_slang_dict,
    prepare_model_input,
    reload_slang_dict,
)

#  Helper: Pembuat Berkas CSV Tiruan untuk Isolasi Pengujian
def _write_csv(path: Path, rows: list[tuple[str, str]], with_header: bool = True) -> Path:
    """Membantu menulis berkas CSV slang sementara agar pengujian tidak merusak data asli."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if with_header:
            writer.writerow(["slang", "baku"])
        writer.writerows(rows)
    return path

#  1. PENGUJIAN: load_slang_dict()
class TestLoadSlangDict:
    """Memastikan fungsi pemuat kamus bekerja cerdas dalam segala kondisi data."""

    def setup_method(self):
        # Selalu bersihkan lru_cache sebelum tes dimulai agar tidak terjadi kebocoran data antar skenario
        load_slang_dict.cache_clear()

    def test_load_single_word_entries(self, tmp_path):
        """Memastikan kata singkatan biasa berhasil dimuat dengan sempurna."""
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

    def test_key_value_disimpan_lowercase_dan_strip(self, tmp_path):
        """Memastikan data otomatis dibersihkan dari spasi liar dan huruf kapital pengganggu."""
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("  BG  ", "  ABANG  "),
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            result = load_slang_dict()
        assert "bg" in result
        assert result["bg"] == "abang"

    def test_file_tidak_ada_kembalikan_dict_kosong(self, tmp_path):
        """Jaring Pengaman: Jika file belum terdownload, sistem tidak boleh crash, melainkan return dict kosong."""
        path_palsu = str(tmp_path / "tidak_ada_file_ini.csv")
        with patch("app.core.config.settings.SLANG_DICT_PATH", path_palsu):
            result = load_slang_dict()
        assert result == {}

    def test_baris_nilai_kosong_atau_kurang_kolom_otomatis_dilewati(self, tmp_path):
        """Memastikan baris data yang cacat/rusak dilewati secara aman oleh parser."""
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("", "abang"),    # Slang kosong
            ("bg", ""),       # Baku kosong
            ("kk", "kakak"),  # Valid
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            result = load_slang_dict()
        assert "kk" in result
        assert len(result) == 1

    def test_duplikat_key_nilai_terakhir_yang_menang(self, tmp_path):
        """Memastikan jika ada aturan ganda, baris paling bawah yang memegang kendali."""
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("bg", "abang"),
            ("bg", "abangku"),
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            result = load_slang_dict()
        assert result["bg"] == "abangku"

#  2. PENGUJIAN: reload_slang_dict()
class TestReloadSlangDict:
    """Memastikan fitur hot-swap/hot-reload berjalan lancar tanpa perlu restart server API."""

    def setup_method(self):
        load_slang_dict.cache_clear()

    def test_reload_berhasil_memperbarui_memori_runtime(self, tmp_path):
        csv_file = tmp_path / "slang.csv"
        _write_csv(csv_file, [("bg", "abang")])

        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            hasil_awal = load_slang_dict()
            assert "kk" not in hasil_awal

            # Simulasi Admin memperbarui file CSV di tengah jalan
            _write_csv(csv_file, [("bg", "abang"), ("kk", "kakak")])
            hasil_baru = reload_slang_dict()

        assert hasil_baru.get("kk") == "kakak"
        assert len(hasil_baru) == 2

#  3. PENGUJIAN: get_slang_stats()
class TestGetSlangStats:
    """Memastikan dasbor monitoring mendapatkan data ringkasan struktur kamus secara presisi."""

    def setup_method(self):
        load_slang_dict.cache_clear()

    def test_stats_kalkulasi_secara_akurat(self, tmp_path):
        csv_file = _write_csv(tmp_path / "slang.csv", [
            ("bg", "abang"),
            ("kk", "kakak"),
        ])
        with patch("app.core.config.settings.SLANG_DICT_PATH", str(csv_file)):
            stats = get_slang_stats()

        assert stats["total"] == 2
        assert stats["loaded"] is True
        assert "path" in stats

#  4. INTEGRASI: Transformasi Slang Lewat prepare_model_input()
class TestSlangIntegrationPipeline:
    """Memastikan kata slang berhasil diluruskan saat mengalir di pipa pembersih utama."""

    def test_normalisasi_slang_pembeli_dan_penjual(self):
        mock_kamus = {"nasgor": "nasi goreng", "bgt": "banget"}
        raw_chat = "[07.42] Pembeli: pesan nasgor\n[07.44] Penjual: siap mantap bgt"
        
        with patch("app.services.processing.load_slang_dict", return_value=mock_kamus):
            result = prepare_model_input(raw_chat)
            
        # Memastikan seluruh slang mendarat dalam bentuk kata baku siap saji
        assert "nasgor" not in result
        assert "bgt" not in result
        assert "nasi goreng" in result
        assert "mantap banget" in result

#  5. JALUR INTEGRASI KAMUS FISIK ASLI (AUTOMATED PROTECTION)
# Menghitung jalur absolut agar aman dibaca dari folder pengetesan mana pun
SLANG_REAL_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/final/slang_utama.csv")
)

@pytest.mark.skipif(
    not os.path.exists(SLANG_REAL_CSV_PATH),
    reason="Kamus slang_utama.csv belum diunduh lokal, melewati tes integrasi fisik."
)
class TestKamusSlangFisikAsli:
    """Pengunci Keamanan: Memastikan file asli dari tim data scientist tidak rusak/kosong."""

    def setup_method(self):
        load_slang_dict.cache_clear()

    def test_validasi_kelayakan_file_produksi_nyata(self):
        with patch("app.core.config.settings.SLANG_DICT_PATH", SLANG_REAL_CSV_PATH):
            kamus_nyata = load_slang_dict()
        
        assert isinstance(kamus_nyata, dict)
        assert len(kamus_nyata) > 0, "Bahaya! Berkas slang_utama.csv terdeteksi kosong!"