from __future__ import annotations

import csv
import logging
import os
import re
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)

SlangDict = Dict[str, str]

# ── BLOK PERTAMA: PREPROCESSING TINGKAT LANJUT ────────────────────────────────

@lru_cache(maxsize=1)
def load_slang_dict() -> SlangDict:
    """Muat kamus slang dari disk lokal."""
    slang_dict: SlangDict = {}
    path = settings.SLANG_DICT_PATH

    if not os.path.exists(path):
        logger.warning("[Slang] Kamus tidak ditemukan di '%s'.", path)
        return slang_dict

    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header

            for lineno, row in enumerate(reader, start=2):
                if len(row) < 2: continue
                slang_raw = row[0].strip().lower()
                baku_raw  = row[1].strip().lower()
                if not slang_raw or not baku_raw: continue
                slang_dict[slang_raw] = baku_raw
    except Exception as exc:
        logger.exception("[Slang] Gagal membaca kamus slang: %s", exc)
        return {}

    return slang_dict

def reload_slang_dict() -> SlangDict:
    load_slang_dict.cache_clear()
    return load_slang_dict()

def get_slang_stats() -> dict:
    slang_dict = load_slang_dict()
    single_word = sum(1 for k in slang_dict if " " not in k)
    return {
        "total":       len(slang_dict),
        "single_word": single_word,
        "multi_word":  len(slang_dict) - single_word,
        "loaded":      len(slang_dict) > 0,
        "path":        settings.SLANG_DICT_PATH,
    }

# Implementasi Pembersih Universal Regex & Sekat Domain [SEP]
def prepare_model_input(raw_text: str) -> str:
    """
    Mengubah raw chat WhatsApp menjadi string bersih siap konsumsi model AI.
    Mendukung segala ragam timestamp kotor lintas OS handphone.
    """
    slang_dict = load_slang_dict()
    if not isinstance(raw_text, str): return ""
    
    baris_chat = raw_text.split('\n')
    baris_bersih = []

    for baris in baris_chat:
        if not baris.strip(): continue
        
        # 1. Sapu bersih segala pola penanda waktu (dengan/tanpa tahun, pm/am, kurung siku)
        baris = re.sub(r'^\[?\d{1,2}[/\-\.]\d{1,2}([/\-\.]\d{2,4})?,?\s+\d{1,2}[:\.]\d{2}([:\.]\d{2})?(\s*[aApP][mM])?\]?\s*(-\s*)?', '', baris)
        baris = re.sub(r'^\[?\d{1,2}\s+[A-Za-z]+(\s+\d{2,4})?,?\s+\d{1,2}[:\.]\d{2}([:\.]\d{2})?(\s*[aApP][mM])?\]?\s*(-\s*)?', '', baris)
        
        # 2. Potong nama pengirim chat secara dinamis (fleksibel tanpa hardcode kata Pembeli/Penjual)
        if ':' in baris:
            bagian_kiri = baris.split(':', 1)[0]
            if len(bagian_kiri) < 50: 
                baris = baris.split(':', 1)[1]
                
        baris_bersih.append(baris.strip())

    # 3. Satukan domain percakapan menggunakan token separator utama
    text = " [SEP] ".join(baris_bersih)
    text = text.replace("[SEP] [SEP]", "[SEP]").lower()
    text = text.replace("&", " dan ")

    # 4. Reduksi kata sapaan pengisi (Noise reduction)
    sapaan_pattern = r'\b(bg|abang|bang|mas|kak|mbak|kk|min|teteh|teh|aa|om|tante|bude|pakde|paklik|pak|bapak|bu|ibu|gan|sis|bro|cuy|bos|juragan|admin|halo|halo admin|hallo|pagi|siang|sore|malam|subuh|assalamualaikum|wr|wb|p|ping|ass|dan|dn|budi|deni|andi|ani|siti|dewi|rudi|joko|reza|putri)\b'
    text = re.sub(sapaan_pattern, ' ', text)

    # 5. Normalisasi mata uang dan pelurusan eksponen ribuan/jutaan murni
    text = re.sub(r'\brp\s*(\d+)', r'\1', text)
    text = re.sub(r'(?<=\d)\.(?=\d{3}\b)', '', text)
    text = re.sub(r'\b(\d+)\s*(k|rb|ribu)\b', r'\g<1>000', text)
    text = re.sub(r'\b(\d+)\s*(jt|juta)\b', r'\g<1>000000', text)

   # 6. Terapkan Kamus Slang HANYA jika kata tersebut ada persis di kamus
    kata_kata = []
    if slang_dict:
        for k in text.split():
            kata_baku = slang_dict.get(k)
            if kata_baku:
                # Cegah over-correction: Jika 1 kata slang diubah jadi lebih dari 2 kata baku (indikasi anomali/halusinasi kamus)
                if len(kata_baku.split()) > 2 and len(k.split()) == 1:
                    kata_kata.append(k) # Abaikan kamus, pertahankan kata asli
                else:
                    kata_kata.append(kata_baku)
            else:
                kata_kata.append(k)
        text = " ".join(kata_kata)

    # 7. Bersihkan sisa simbol baca pengganggu inferensi sekuensial
    text = re.sub(r'[^a-z0-9\s\[\]]', ' ', text)
    text = re.sub(r'(\b\w+)(nya)\b', r'\1', text)
    text = text.replace("[sep]", "[SEP]")
    text = re.sub(r'\b(dong|donk|dnk|ya+|ko+k)\b', '', text)
    
    return re.sub(r'\s+', ' ', text).strip()


# ── BLOK KEDUA: POSTPROCESSING TINGKAT LANJUT ────────────────────────────────

def _extract_total_from_chat(teks_bersih: str) -> Optional[int]:
    """Ekstrak nilai total klaim nota kasir dari teks biner."""
    match = re.search(
        r'(?:total|jadi|semua|tagihan|bayar)(?:nya)?\s*(\d+)',
        teks_bersih,
        re.IGNORECASE,
    )
    return int(match.group(1)) if match else None


# Mentranslasikan output mentah AI menjadi Key Kontrak Baru
def postprocess(list_pesanan: List[dict], teks_bersih: str) -> List[dict]:
    """
    Menghitung subtotal per item makanan dan menentukan status verifikasi confidence AI.
    Dilengkapi dengan Fallback Regex jika AI gagal mendeteksi nama produk.
    """
    total_chat = _extract_total_from_chat(teks_bersih)
    grand_total_prediksi = sum(
        (item["quantity"] * item["price_satuan"])
        for item in list_pesanan
        if item.get("price_satuan") is not None
    )

    hasil_akhir = []

    for item in list_pesanan:
        quantity = item["quantity"]
        price_satuan = item.get("price_satuan")
        product_name = item.get("product_name", "unknown")
        avg_conf = item.get("avg_conf_softmax", 0.0)

        # FITUR FALLBACK PENYELAMAT PRODUK
        if product_name == "unknown":
            qty_str = str(quantity)
            chat_pembeli = teks_bersih.split('[SEP]')[0]
            
            # Gunakan \b (word boundary) agar angka "1" tidak mencuri dari dalam "10"
            match = re.search(rf'(.*?)\s+\b{qty_str}\b', chat_pembeli, re.IGNORECASE)
            
            if match:
                tebakan = match.group(1).strip()
                # Bersihkan ragam kata kerja di awal agar murni nama produk
                tebakan = re.sub(r'^(pesan|order|mau|beli|minta|tolong|bikinin|bikin)\s+', '', tebakan, flags=re.IGNORECASE).strip()
                
                if tebakan:
                    product_name = tebakan.title()

        # Hitung kalkulasi matematika subtotal murni
        subtotal_item = (quantity * price_satuan) if price_satuan is not None else None

        # Penentuan status keandalan verifikasi
        if price_satuan is None or product_name == "unknown":
            confidence = "MEDIUM"
        elif total_chat is not None:
            confidence = "HIGH" if grand_total_prediksi == total_chat else "LOW"
        else:
            if avg_conf >= 90.0: confidence = "HIGH"
            elif avg_conf >= 70.0: confidence = "MEDIUM"
            else: confidence = "LOW"

        hasil_akhir.append({
            "product_name": product_name,
            "quantity":     quantity,
            "price_satuan": price_satuan,
            "subtotal":     subtotal_item,
            "confidence":   confidence,
        })

    return hasil_akhir

# ── VALIDASI ──────────────────────────────────────────────────────────────────

def validate_input_length(raw_text: str) -> None:
    if len(raw_text.strip()) < 5:
        from app.core.errors import InvalidInputError
        raise InvalidInputError(
            f"Input terlalu pendek ({len(raw_text.strip())} karakter). Minimal 5 karakter."
        )