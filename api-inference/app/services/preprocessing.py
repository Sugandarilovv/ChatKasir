"""
Preprocessing & Postprocessing pipeline — tanggung jawab AI-2 (Denny).

Blok Pertama  : preprocessing (sebelum teks masuk model)
  - Hapus timestamp WhatsApp dengan regex
  - Pisahkan pesan pembeli dan penjual
  - Lowercase seluruh teks
  - Hapus karakter khusus (tanda baca, emoji, simbol)
  - Split kalimat (untuk pesan panjang multi-kalimat)
  - Normalisasi slang menggunakan kamus dari DS-1 (Faradi)
    · Single-word lookup  : "bg"        → "abang"
    · Multi-word phrase   : "nasi grg"  → "nasi goreng"
    · Longest-match-first : "es teh" diprioritaskan atas "es" + "teh" terpisah
  - Gabungkan dengan separator [SEP]

Blok Kedua    : postprocessing (setelah model menghasilkan output)
  - Hitung total  = quantity × price_satuan
  - Tentukan confidence berdasarkan total yang disebutkan di chat

Changelog:
  Hari 6 (27 Apr): lowercase, remove_special_chars, split_sentences, pipeline dasar
  Hari 7 (28 Apr): load CSV DS-1, multi-word phrase matching, reload hot-swap, validasi
"""

from __future__ import annotations

import csv
import logging
import os
import re
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)

# Type alias: dict[slang] = baku
SlangDict = Dict[str, str]


# ─────────────────────────────────────────────────────────────────────────────
#  BLOK PERTAMA: PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

# ── Load & Reload Kamus Slang ─────────────────────────────────────────────────

@lru_cache(maxsize=1)
def load_slang_dict() -> SlangDict:
    """
    Muat kamus slang dari file CSV DS-1 (Faradi) — di-cache setelah pertama load.

    Format CSV yang diharapkan (dengan header):
        slang,baku
        bg,abang
        nasi grg,nasi goreng

    Aturan:
    - Kolom kurang dari 2   → baris dilewati + warning per baris
    - Nilai kosong          → baris dilewati + warning per baris
    - Duplikat key          → entri terakhir menang (warning dicatat)
    - Semua key & value     → lowercase + strip whitespace

    Mendukung single-word ("bg") DAN multi-word phrase ("nasi grg").
    Pemisahan untuk normalisasi frasa ditangani oleh normalize_slang().

    Returns
    -------
    dict[slang_lowercase] = baku_lowercase
    Kamus kosong jika file tidak ditemukan atau gagal dibaca.
    """
    slang_dict: SlangDict = {}
    path = settings.SLANG_DICT_PATH

    if not os.path.exists(path):
        logger.warning(
            "[Slang] Kamus tidak ditemukan di '%s'. "
            "Normalisasi slang dinonaktifkan sampai file tersedia.",
            path,
        )
        return slang_dict

    bad_rows: List[Tuple[int, str]] = []   # (nomor_baris, alasan)
    duplicates: List[str] = []

    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)  # skip header row

            if header is None:
                logger.warning("[Slang] File CSV '%s' kosong.", path)
                return slang_dict

            for lineno, row in enumerate(reader, start=2):  # start=2 karena baris 1 = header
                # Validasi jumlah kolom
                if len(row) < 2:
                    bad_rows.append((lineno, f"hanya {len(row)} kolom"))
                    continue

                slang_raw = row[0].strip().lower()
                baku_raw  = row[1].strip().lower()

                # Validasi nilai tidak kosong
                if not slang_raw:
                    bad_rows.append((lineno, "kolom 'slang' kosong"))
                    continue
                if not baku_raw:
                    bad_rows.append((lineno, "kolom 'baku' kosong"))
                    continue

                # Deteksi duplikat key
                if slang_raw in slang_dict:
                    duplicates.append(
                        f"'{slang_raw}': '{slang_dict[slang_raw]}' → '{baku_raw}' (baris {lineno})"
                    )

                slang_dict[slang_raw] = baku_raw

    except Exception as exc:
        logger.exception("[Slang] Gagal membaca kamus slang: %s", exc)
        return {}

    # ── Ringkasan log setelah load ────────────────────────────────────────
    single_word = sum(1 for k in slang_dict if " " not in k)
    multi_word  = len(slang_dict) - single_word

    logger.info(
        "[Slang] Dimuat dari '%s': %d entri total "
        "(%d single-word, %d multi-word phrase).",
        path, len(slang_dict), single_word, multi_word,
    )

    if bad_rows:
        logger.warning(
            "[Slang] %d baris dilewati karena format tidak valid:\n%s",
            len(bad_rows),
            "\n".join(f"  baris {n}: {alasan}" for n, alasan in bad_rows),
        )

    if duplicates:
        logger.warning(
            "[Slang] %d duplikat key ditemukan (nilai terakhir dipakai):\n%s",
            len(duplicates),
            "\n".join(f"  {d}" for d in duplicates),
        )

    return slang_dict


def reload_slang_dict() -> SlangDict:
    """
    Paksa reload kamus slang dari disk — berguna untuk hot-swap tanpa restart.

    Cara kerja:
        Bersihkan cache lru_cache pada load_slang_dict(), lalu panggil ulang.
        Thread-safe selama tidak ada request aktif saat reload.

    Returns
    -------
    Kamus slang yang baru dimuat.
    """
    load_slang_dict.cache_clear()
    logger.info("[Slang] Cache dibersihkan — memuat ulang kamus slang...")
    return load_slang_dict()


def get_slang_stats() -> dict:
    """
    Kembalikan statistik kamus slang yang sedang di-cache.
    Berguna untuk endpoint /health atau debugging.

    Returns
    -------
    {
        "total": int,
        "single_word": int,
        "multi_word": int,
        "loaded": bool,
        "path": str,
    }
    """
    slang_dict = load_slang_dict()
    single_word = sum(1 for k in slang_dict if " " not in k)
    return {
        "total":       len(slang_dict),
        "single_word": single_word,
        "multi_word":  len(slang_dict) - single_word,
        "loaded":      len(slang_dict) > 0,
        "path":        settings.SLANG_DICT_PATH,
    }


# ── Fungsi Dasar Preprocessing ────────────────────────────────────────────────

def lowercase(text: str) -> str:
    """
    Ubah seluruh teks menjadi huruf kecil.

    Contoh:
        "Bang 2 Nasi Goreng YA" -> "bang 2 nasi goreng ya"
    """
    return text.lower()


def remove_special_chars(text: str) -> str:
    """
    Hapus semua karakter yang bukan huruf a-z, angka 0-9, atau spasi.
    Tanda baca, emoji, simbol mata uang, tanda kurung, dsb. dibuang.
    Spasi berlebih (hasil penghapusan) dirapikan menjadi satu spasi.

    Contoh:
        "bang!! 2 nasi-goreng ya"  -> "bang 2 nasigoreng ya"
        "total: 20.000"            -> "total 20000"

    Catatan:
        Dipanggil SETELAH lowercase() agar hasil konsisten.
        Tanda titik dalam "20.000" dihapus → "20000" (benar untuk pattern di postprocess).
    """
    cleaned = re.sub(r'[^a-z0-9\s]', '', text)
    return re.sub(r'\s+', ' ', cleaned).strip()


def split_sentences(text: str) -> List[str]:
    """
    Pecah teks menjadi list kalimat berdasarkan tanda baca akhir kalimat
    dan baris baru.

    Contoh:
        "mau pesan 2 nasi goreng. sama 1 es teh ya"
        -> ["mau pesan 2 nasi goreng", "sama 1 es teh ya"]

    Catatan:
        Untuk tokenisasi lanjutan (Hari-8), output list ini bisa di-join
        kembali atau diproses per kalimat sesuai pipeline AI-1 (Rifan).
    """
    parts = re.split(r'[.!?\n]+', text)
    return [s.strip() for s in parts if s.strip()]


# ── Normalisasi Slang — Multi-Word Phrase Support ─────────────────────────────

def _build_phrase_index(slang_dict: SlangDict) -> Dict[int, List[Tuple[List[str], str]]]:
    """
    Bangun indeks frasa berdasarkan jumlah kata agar normalize_slang()
    bisa mencoba longest-match-first secara efisien.

    Returns
    -------
    {
        3: [(['nasi', 'goreng', 'spesial'], 'nasi goreng spesial'), ...],
        2: [(['nasi', 'grg'], 'nasi goreng'), (['es', 'teh'], 'es teh'), ...],
    }
    Hanya entri dengan spasi (multi-word) yang masuk indeks ini.
    Single-word tetap di-lookup langsung via slang_dict[word].
    """
    index: Dict[int, List[Tuple[List[str], str]]] = {}
    for slang, baku in slang_dict.items():
        tokens = slang.split()
        if len(tokens) >= 2:
            n = len(tokens)
            if n not in index:
                index[n] = []
            index[n].append((tokens, baku))
    return index


def normalize_slang(text: str) -> str:
    """
    Normalisasi kata-kata slang, singkatan, dan typo menggunakan kamus DS-1.

    Strategi (Hari 7):
    1. Bangun indeks frasa dari kamus (multi-word terlebih dahulu).
    2. Scan token per token dengan sliding-window, coba panjang frasa terpanjang
       dulu (longest-match-first) sebelum fallback ke single-word lookup.
    3. Token yang tidak cocok dikembalikan apa adanya (sudah lowercase).

    Input WAJIB sudah melalui lowercase() agar lookup konsisten.

    Contoh:
        "bg mau pesan nasi grg" -> "abang mau pesan nasi goreng"
        "esteh" masih dikenali  -> "es teh"  (karena ada di kamus sebagai single token)
        "es teh" (dua kata)     -> "es teh"  (tetap — sudah bentuk baku)
    """
    slang_dict = load_slang_dict()
    if not slang_dict:
        return text

    tokens = text.split()
    if not tokens:
        return text

    # Bangun indeks frasa multi-kata, urutkan panjang dari besar ke kecil
    phrase_index = _build_phrase_index(slang_dict)
    max_phrase_len = max(phrase_index.keys(), default=0)

    result: List[str] = []
    i = 0

    while i < len(tokens):
        matched = False

        # Coba longest-match terlebih dahulu
        for phrase_len in range(min(max_phrase_len, len(tokens) - i), 1, -1):
            if phrase_len not in phrase_index:
                continue
            window = tokens[i : i + phrase_len]
            window_str = " ".join(window)
            if window_str in slang_dict:
                result.append(slang_dict[window_str])
                i += phrase_len
                matched = True
                break

        if not matched:
            # Fallback: single-word lookup
            result.append(slang_dict.get(tokens[i], tokens[i]))
            i += 1

    return " ".join(result)


# ── WhatsApp Parser ───────────────────────────────────────────────────────────

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
    pattern = r'\[([^\]]+)\]\s*(Pembeli|Penjual):\s*'
    lines = raw_text.strip().split('\n')
    hasil: Dict[str, str] = {"pembeli": "", "penjual": ""}

    for line in lines:
        match = re.match(pattern, line)
        if match:
            pengirim = match.group(2).lower()
            isi_pesan = re.sub(pattern, '', line).strip()
            if hasil[pengirim]:
                hasil[pengirim] += " " + isi_pesan
            else:
                hasil[pengirim] = isi_pesan

    return hasil


# ── Pipeline Utama ────────────────────────────────────────────────────────────

def prepare_model_input(raw_text: str) -> str:
    """
    Mengubah raw chat WhatsApp -> string bersih siap masuk model.

    Pipeline lengkap (urutan penting):
      1. Hapus timestamp & pisahkan per pengirim  (parse_whatsapp_chat)
      2. Lowercase                                (lowercase)
      3. Hapus karakter khusus                   (remove_special_chars)
      4. Normalisasi slang + frasa multi-kata    (normalize_slang)
      5. Gabungkan dengan separator [SEP]

    Returns
    -------
    Teks bersih, contoh:
        "abang 2 nasi goreng ya [SEP] oke kakak 1 nasi goreng total 20 ribu ya"

    Catatan untuk Hari-8 (tokenisasi):
        split_sentences() tersedia sebagai utilitas jika pipeline tokenisasi
        AI-1 membutuhkan input per kalimat, bukan per pengirim.
    """
    parsed = parse_whatsapp_chat(raw_text)

    pembeli = parsed["pembeli"]
    penjual = parsed["penjual"]

    # Step 2: Lowercase
    pembeli = lowercase(pembeli)
    penjual = lowercase(penjual)

    # Step 3: Hapus karakter khusus
    pembeli = remove_special_chars(pembeli)
    penjual = remove_special_chars(penjual)

    # Step 4: Normalisasi slang (longest-match-first multi-word + single-word)
    pembeli = normalize_slang(pembeli)
    penjual = normalize_slang(penjual)

    # Step 5: Gabungkan dengan [SEP]
    if penjual:
        return pembeli + " [SEP] " + penjual

    return pembeli


# ─────────────────────────────────────────────────────────────────────────────
#  BLOK KEDUA: POSTPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def _extract_total_from_chat(teks_bersih: str) -> Optional[int]:
    """
    Ekstrak nilai total yang disebutkan oleh penjual di dalam chat.

    Menangani variasi penulisan setelah preprocessing:
        "total 20rb", "total 20000", "total 25k", "total 20 ribu"

    Catatan:
        Karena teks_bersih sudah melalui remove_special_chars(),
        format "20.000" sudah menjadi "20000".

    Returns
    -------
    Total dalam rupiah penuh sebagai int, atau None jika tidak ditemukan.
    """
    match = re.search(
        r'total(?:nya)?\s*(\d+)\s*(rb|ribu|k)?',
        teks_bersih,
        re.IGNORECASE,
    )
    if not match:
        return None

    angka = int(match.group(1))
    satuan = match.group(2)
    if satuan and satuan.lower() in ['rb', 'ribu', 'k']:
        return angka * 1000
    return angka


def postprocess(model_output: dict, teks_bersih: str) -> dict:
    """
    Menghitung total dan confidence flag dari output model.

    Parameters
    ----------
    model_output:
        Dict dari ModelLoader.predict_single(), berisi:
        { "product": str, "quantity": int, "price_satuan": int }
        price_satuan sudah dalam RUPIAH PENUH.

    teks_bersih:
        Teks yang sudah dipreprocess (dipakai untuk mengekstrak total di chat).

    Returns
    -------
    Dict lengkap:
        { "product", "quantity", "price_satuan", "total", "confidence" }

    Confidence:
        HIGH   — total dari chat cocok dengan prediksi (langsung disimpan)
        LOW    — ada total di chat tapi tidak cocok   (minta konfirmasi)
        MEDIUM — tidak ada total di chat              (tampilkan dengan opsi edit)
    """
    quantity: int    = model_output["quantity"]
    price_satuan: int = model_output["price_satuan"]

    total_prediksi: int = quantity * price_satuan
    total_chat = _extract_total_from_chat(teks_bersih)

    if total_chat is not None and total_prediksi == total_chat:
        confidence = "HIGH"
    elif total_chat is not None:
        confidence = "LOW"
    else:
        confidence = "MEDIUM"

    return {
        **model_output,
        "total":      total_prediksi,
        "confidence": confidence,
    }
