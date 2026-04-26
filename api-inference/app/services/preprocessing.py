"""
Preprocessing & Postprocessing pipeline — tanggung jawab AI-2 (Denny).

Blok Pertama  : preprocessing (sebelum teks masuk model)
  - Hapus timestamp WhatsApp dengan regex
  - Pisahkan pesan pembeli dan penjual
  - Normalisasi slang menggunakan kamus dari DS-1 (Faradi)
  - Gabungkan dengan separator [SEP]

Blok Kedua    : postprocessing (setelah model menghasilkan output)
  - Hitung total  = quantity × price_satuan
  - Tentukan confidence berdasarkan total yang disebutkan di chat
"""

from __future__ import annotations

import csv
import logging
import os
import re
from functools import lru_cache
from typing import Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  BLOK PERTAMA: PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def load_slang_dict() -> Dict[str, str]:
    """
    Muat kamus slang dari file CSV DS-1 (Faradi).
    Hasil di-cache agar tidak dibaca ulang setiap request.

    Format CSV yang diharapkan: kolom pertama = slang, kolom kedua = bentuk baku.
    """
    slang_dict: Dict[str, str] = {}
    path = settings.SLANG_DICT_PATH

    if not os.path.exists(path):
        logger.warning(
            "Kamus slang tidak ditemukan di '%s'. "
            "Normalisasi slang dinonaktifkan.",
            path,
        )
        return slang_dict

    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 2:
                    slang_dict[row[0].strip().lower()] = row[1].strip().lower()
        logger.info("Kamus slang dimuat: %d entri dari '%s'", len(slang_dict), path)
    except Exception as exc:
        logger.exception("Gagal memuat kamus slang: %s", exc)

    return slang_dict


def normalize_slang(text: str) -> str:
    """
    Normalisasi kata-kata slang, singkatan, dan typo menggunakan kamus DS-1.

    Contoh:
        "bg mau psnnn nasi grngg" → "abang mau pesan nasi goreng"
    """
    slang_dict = load_slang_dict()
    if not slang_dict:
        return text

    words = text.split()
    normalized = [slang_dict.get(w.lower(), w) for w in words]
    return " ".join(normalized)


def parse_whatsapp_chat(raw_text: str) -> Dict[str, str]:
    """
    Membersihkan format timestamp WhatsApp dan memisahkan
    pesan pembeli dan penjual.

    Pola yang ditangani:
        "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya"
        "[07.44, 22/4/2026] Penjual: oke kak 10rb ya"

    Jika ada lebih dari satu pesan per pengirim (chat panjang),
    semua pesan digabungkan dengan spasi.

    Returns
    -------
    dict dengan kunci "pembeli" dan "penjual".
    """
    # Regex mengenali format: [timestamp] NamaPengirim: isi pesan
    pattern = r'\[([^\]]+)\]\s*(Pembeli|Penjual):\s*'
    lines = raw_text.strip().split('\n')
    hasil: Dict[str, str] = {"pembeli": "", "penjual": ""}

    for line in lines:
        match = re.match(pattern, line)
        if match:
            pengirim = match.group(2).lower()
            isi_pesan = re.sub(pattern, '', line).strip()
            # Gabungkan jika ada lebih dari satu pesan per pengirim
            if hasil[pengirim]:
                hasil[pengirim] += " " + isi_pesan
            else:
                hasil[pengirim] = isi_pesan

    return hasil


def prepare_model_input(raw_text: str) -> str:
    """
    Mengubah raw chat WhatsApp → string bersih siap masuk model.

    Langkah:
      1. Hapus timestamp dan pisahkan per pengirim
      2. Normalisasi slang pada masing-masing pesan
      3. Gabungkan dengan separator [SEP]

    Returns
    -------
    Teks bersih, contoh:
        "bang 2 nasi goreng ya [SEP] oke kak 1 nasi goreng 10rb totalnya 20rb ya"
    """
    parsed = parse_whatsapp_chat(raw_text)

    pembeli = normalize_slang(parsed["pembeli"])
    penjual = normalize_slang(parsed["penjual"])

    if penjual:
        return pembeli + " [SEP] " + penjual

    return pembeli


# ─────────────────────────────────────────────────────────────────────────────
#  BLOK KEDUA: POSTPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def _extract_total_from_chat(teks_bersih: str) -> Optional[int]:
    """
    Ekstrak nilai total yang disebutkan oleh penjual di dalam chat.

    Menangani variasi penulisan:
        "totalnya 20rb", "total 20.000", "20ribu", "total 25k"

    Returns
    -------
    Total dalam rupiah penuh sebagai int, atau None jika tidak ditemukan.
    """
    match = re.search(
        r'total(?:nya)?\s*(\d+(?:\.\d+)?)\s*(rb|ribu|k)?',
        teks_bersih,
        re.IGNORECASE,
    )
    if not match:
        return None

    angka = float(match.group(1).replace('.', ''))
    satuan = match.group(2)
    if satuan and satuan.lower() in ['rb', 'ribu', 'k']:
        return int(angka * 1000)
    return int(angka)


def postprocess(model_output: dict, teks_bersih: str) -> dict:
    """
    Menghitung total dan confidence flag dari output model.

    Parameters
    ----------
    model_output:
        Dict dari ModelLoader.predict_single(), berisi:
        { "product": str, "quantity": int, "price_satuan": int }
        price_satuan sudah dalam RUPIAH PENUH — tidak perlu konversi.

    teks_bersih:
        Teks yang sudah dipreprocess (dipakai untuk mengekstrak total di chat).

    Returns
    -------
    Dict lengkap:
        { "product", "quantity", "price_satuan", "total", "confidence" }
    """
    quantity: int = model_output["quantity"]
    price_satuan: int = model_output["price_satuan"]  # sudah dalam rupiah penuh

    # Hitung total dari prediksi model
    total_prediksi: int = quantity * price_satuan

    # Cari total yang disebutkan di chat untuk verifikasi
    total_chat = _extract_total_from_chat(teks_bersih)

    # Tentukan confidence
    if total_chat is not None and total_prediksi == total_chat:
        confidence = "HIGH"     # total cocok → prediksi dapat dipercaya
    elif total_chat is not None:
        confidence = "LOW"      # ada total di chat tapi tidak cocok → perlu konfirmasi
    else:
        confidence = "MEDIUM"   # tidak ada total di chat untuk diverifikasi

    return {
        **model_output,
        "total": total_prediksi,
        "confidence": confidence,
    }
