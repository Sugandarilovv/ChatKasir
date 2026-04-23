"""
Rule-Based Generation Script - ChatKasir
DS-1: Muhammad Faradi Eka Damara

Deskripsi:
    Script ini menghasilkan data sintetis variasi teks pesanan pelanggan UMKM
    berbahasa Indonesia yang informal (gaul, typo, singkatan), beserta label
    entitas: nama produk, jumlah, dan harga.

Input:
    - FILE_FOOD    : path ke dataset nama makanan Indonesia (kolom nama makanan)
    - FILE_SLANG   : path ke dataset kamus slang Indonesia (kolom slang & baku)

Output:
    - synthetic_orders.csv : dataset hasil generate (~1000 baris)

Kolom output:
    text        : teks pesanan mentah (informal)
    product     : nama produk yang dipesan
    quantity    : jumlah pesanan (integer)
    price       : harga satuan (integer, dalam rupiah)
    total_price : total harga = quantity * price
"""

import pandas as pd
import numpy as np
import random
import re
import os
from datetime import datetime

# ──────────────────────────────────────────────
# KONFIGURASI — sesuaikan nama file kamu di sini
# ──────────────────────────────────────────────
FILE_FOOD  = "../final/food_utama.csv"      # <-- ganti dengan nama file dataset food kamu
FILE_SLANG = "../final/slang_utama.csv"      # <-- ganti dengan nama file dataset slang kamu
FOOD_COL   = "name"                     # <-- ganti dengan nama kolom nama makanan
SLANG_COL  = "slang"                    # <-- ganti dengan nama kolom kata slang
FORMAL_COL = "formal"                   # <-- ganti dengan nama kolom kata formal/baku

OUTPUT_FILE    = "synthetic_orders_one.csv"
TARGET_ROWS    = 1000
RANDOM_SEED    = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ──────────────────────────────────────────────
# 1. LOAD DATASET
# ──────────────────────────────────────────────
def load_datasets():
    print("[INFO] Memuat dataset...")

    if not os.path.exists(FILE_FOOD):
        raise FileNotFoundError(f"File tidak ditemukan: {FILE_FOOD}")
    if not os.path.exists(FILE_SLANG):
        raise FileNotFoundError(f"File tidak ditemukan: {FILE_SLANG}")

    df_food  = pd.read_csv(FILE_FOOD)
    df_slang = pd.read_csv(FILE_SLANG)

    # Ambil daftar nama makanan, hilangkan null & duplikat
    food_list = (
        df_food[FOOD_COL]
        .dropna()
        .drop_duplicates()
        .str.strip()
        .str.lower()
        .tolist()
    )

    # Buat kamus slang → formal
    slang_dict = dict(
        zip(
            df_slang[SLANG_COL].str.strip().str.lower(),
            df_slang[FORMAL_COL].str.strip().str.lower()
        )
    )

    print(f"[INFO] Jumlah nama makanan: {len(food_list)}")
    print(f"[INFO] Jumlah entri kamus slang: {len(slang_dict)}")
    return food_list, slang_dict


# ──────────────────────────────────────────────
# 2. KOMPONEN VARIASI TEKS
# ──────────────────────────────────────────────

# Variasi cara menyebut jumlah
QUANTITY_WORDS = {
    1: ["1", "satu", "1 biji", "1 porsi", "seporsi", "1 aja", "satu dong"],
    2: ["2", "dua", "2 porsi", "dua porsi", "2 biji"],
    3: ["3", "tiga", "3 porsi", "tiga porsi"],
    4: ["4", "empat", "4 porsi"],
    5: ["5", "lima", "5 porsi", "lima porsi"],
    10: ["10", "sepuluh", "10 porsi"],
}

# Variasi cara menyebut harga
def format_price_text(price: int) -> str:
    templates = [
        f"{price}",
        f"Rp{price}",
        f"Rp. {price}",
        f"rp {price}",
        f"{price} rb" if price >= 1000 else f"{price}",
        f"{price//1000}k" if price >= 1000 else f"{price}",
        f"{price//1000} ribu" if price >= 1000 else f"{price}",
        f"harganya {price}",
        f"harga {price//1000}k" if price >= 1000 else f"harga {price}",
    ]
    return random.choice(templates)

# Pola kalimat pesanan
TEMPLATES = [
    "mau pesen {qty} {product} dong",
    "kak minta {qty} {product} ya harga {price}",
    "beli {qty} {product} {price}",
    "pesen {qty} {product} kak, total {total}",
    "order {product} {qty} pcs harga {price}",
    "nitip {product} ya {qty} aja harga {price}",
    "{qty} {product} berapa kak?",
    "mau {qty} {product}, {price} kan?",
    "pesan {product} {qty} {price}",
    "bisa gak order {qty} {product} harga {price}",
    "kak {qty} {product} {price} ya",
    "{product} {qty} ya kak, harga {price}",
    "tolong pesanin {qty} {product} dong {price}",
    "mau dongg {qty} {product} harga {price}",
    "order {qty} {product} total {total}",
    "halo kak mau beli {qty} {product} harganya {price}",
    "{qty} {product} aja kak harga {price}",
    "beli {product} dulu {qty} {price}",
    "pesan {product} sebanyak {qty} harga {price}",
    "kak ada {product}? mau {qty} {price}",
]

# Variasi typo umum
def apply_typo(text: str) -> str:
    typo_map = {
        "pesan": ["pesen", "psean", "peesn"],
        "beli":  ["belli", "bly", "beli"],
        "harga": ["hrga", "harga", "hrg"],
        "ribu":  ["rbu", "rib", "ribu"],
        "porsi": ["porsi", "porcy", "porxi"],
        "dong":  ["dng", "donk", "dong"],
        "kakak": ["kak", "kaka", "kk"],
    }
    for word, variants in typo_map.items():
        if word in text and random.random() < 0.25:
            text = text.replace(word, random.choice(variants), 1)
    return text

# Sisipkan kata slang acak
def apply_slang(text: str, slang_dict: dict) -> str:
    slang_insertions = [
        "btw ", "fyi ", "ygy ", "wkwk ", "hehe ", "nih ", "loh ", "sih ",
    ]
    if random.random() < 0.3:
        text = random.choice(slang_insertions) + text
    return text

# Variasi kapitalisasi
def apply_capitalization(text: str) -> str:
    choice = random.random()
    if choice < 0.33:
        return text.lower()
    elif choice < 0.66:
        return text.capitalize()
    else:
        return text.upper()


# ──────────────────────────────────────────────
# 3. GENERATOR UTAMA
# ──────────────────────────────────────────────
def generate_order(food_list: list, slang_dict: dict) -> dict:
    # Pilih produk
    product = random.choice(food_list)

    # Pilih jumlah
    qty_int = random.choice(list(QUANTITY_WORDS.keys()))
    qty_text = random.choice(QUANTITY_WORDS[qty_int])

    # Tentukan harga satuan (kelipatan 500, antara 2.000 – 50.000)
    price_int = random.choice(range(2000, 50001, 500))
    total_int = qty_int * price_int
    price_text = format_price_text(price_int)
    total_text = format_price_text(total_int)

    # Pilih template
    template = random.choice(TEMPLATES)
    text = template.format(
        product=product,
        qty=qty_text,
        price=price_text,
        total=total_text,
    )

    # Terapkan variasi
    text = apply_typo(text)
    text = apply_slang(text, slang_dict)
    text = apply_capitalization(text)

    return {
        "text":        text,
        "product":     product,
        "quantity":    qty_int,
        "price":       price_int,
        "total_price": total_int,
    }


# ──────────────────────────────────────────────
# 4. MAIN — GENERATE & SIMPAN
# ──────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  ChatKasir - Rule-Based Generation Script")
    print(f"  Target: {TARGET_ROWS} baris | Seed: {RANDOM_SEED}")
    print("=" * 50)

    food_list, slang_dict = load_datasets()

    print(f"\n[INFO] Mulai generate {TARGET_ROWS} data sintetis...")
    records = [generate_order(food_list, slang_dict) for _ in range(TARGET_ROWS)]

    df_out = pd.DataFrame(records)

    # Cek duplikat teks
    n_dup = df_out["text"].duplicated().sum()
    print(f"[INFO] Duplikat teks ditemukan: {n_dup} baris (wajar jika kecil)")

    # Simpan ke CSV
    df_out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    df_out.to_excel("synthetic_orders_one.xlsx", index=False)
    print(f"\n[OK] File disimpan: {OUTPUT_FILE}")
    print(f"[OK] Total baris  : {len(df_out)}")
    print(f"\nPreview 5 baris pertama:")
    print(df_out.head().to_string(index=False))
    print("\n[DONE] Script selesai dijalankan.")


if __name__ == "__main__":
    main()