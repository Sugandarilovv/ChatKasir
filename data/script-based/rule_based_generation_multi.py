"""
Rule-Based Generation Script - ChatKasir (FIXED VERSION)
Perbaikan:
- CSV aman (pakai separator ';' + quoting)
- JSON lebih compact
- Optional kolom tambahan untuk ML (orders_str)
"""

import pandas as pd
import numpy as np
import random
import json
import os
import csv

# ──────────────────────────────────────────────
# KONFIGURASI
# ──────────────────────────────────────────────
FILE_FOOD  = "../final/food_utama.csv"
FILE_SLANG = "../final/slang_utama.csv"
FOOD_COL   = "name"
SLANG_COL  = "slang"
FORMAL_COL = "formal"

OUTPUT_FILE  = "synthetic_orders_multi.csv"
TARGET_ROWS  = 1000
RANDOM_SEED  = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ──────────────────────────────────────────────
# LOAD DATASET
# ──────────────────────────────────────────────
def load_datasets():
    print("[INFO] Memuat dataset...")

    if not os.path.exists(FILE_FOOD):
        raise FileNotFoundError(f"File tidak ditemukan: {FILE_FOOD}")
    if not os.path.exists(FILE_SLANG):
        raise FileNotFoundError(f"File tidak ditemukan: {FILE_SLANG}")

    df_food  = pd.read_csv(FILE_FOOD)
    df_slang = pd.read_csv(FILE_SLANG)

    food_list = (
        df_food[FOOD_COL]
        .dropna()
        .drop_duplicates()
        .str.strip()
        .str.lower()
        .tolist()
    )

    slang_dict = dict(
        zip(
            df_slang[SLANG_COL].str.strip().str.lower(),
            df_slang[FORMAL_COL].str.strip().str.lower()
        )
    )

    print(f"[INFO] Jumlah makanan : {len(food_list)}")
    print(f"[INFO] Jumlah slang  : {len(slang_dict)}")
    return food_list, slang_dict


# ──────────────────────────────────────────────
# QUANTITY
# ──────────────────────────────────────────────
QUANTITY_WORDS = {
    None: [None],
    1:  ["1", "satu", "seporsi"],
    2:  ["2", "dua", "2 porsi"],
    3:  ["3", "tiga"],
    4:  ["4"],
    5:  ["5"],
}

QTY_KEYS    = [None, 1, 2, 3, 4, 5]
QTY_WEIGHTS = [0.2, 0.4, 0.2, 0.1, 0.05, 0.05]

def pick_qty():
    qty_int  = random.choices(QTY_KEYS, weights=QTY_WEIGHTS, k=1)[0]
    qty_text = random.choice(QUANTITY_WORDS[qty_int])
    actual   = 1 if qty_int is None else qty_int
    return actual, qty_text


# ──────────────────────────────────────────────
# FORMAT HARGA (disederhanakan biar stabil)
# ──────────────────────────────────────────────
def format_price_text(price: int) -> str:
    return random.choice([
        f"{price}",
        f"Rp{price}",
        f"rp {price}"
    ])


# ──────────────────────────────────────────────
# TEMPLATE
# ──────────────────────────────────────────────
TEMPLATES = [
    "mau {qty} {product} {price}",
    "pesen {product} {qty} {price}",
    "beli {qty} {product} {price}",
    "{product} {price}",
]

CONNECTORS = [" dan ", " sama ", " + "]

def build_text(items):
    parts = []
    for it in items:
        price = format_price_text(it["price_int"])
        if it["qty_text"]:
            parts.append(f"{it['qty_text']} {it['product']} {price}")
        else:
            parts.append(f"{it['product']} {price}")
    return random.choice(["", "wkwk ", "kak "]) + random.choice(CONNECTORS).join(parts)


# ──────────────────────────────────────────────
# GENERATE ORDER
# ──────────────────────────────────────────────
def generate_order(food_list):
    num_products = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
    products = random.sample(food_list, k=min(num_products, len(food_list)))

    items = []
    for product in products:
        qty_int, qty_text = pick_qty()
        price_int = random.choice(range(2000, 50001, 500))
        items.append({
            "product": product,
            "qty_int": qty_int,
            "qty_text": qty_text,
            "price_int": price_int
        })

    text = build_text(items)

    orders_detail = [
        {
            "product": it["product"],
            "quantity": it["qty_int"],
            "price": it["price_int"],
            "total_price": it["qty_int"] * it["price_int"]
        }
        for it in items
    ]

    return {
        "text": text,
        "orders": json.dumps(orders_detail, ensure_ascii=False, separators=(',', ':')),  # compact JSON
        "orders_str": "|".join([f"{it['product']}:{it['qty_int']}:{it['price_int']}" for it in items]),  # ML friendly
        "num_items": num_products,
        "grand_total": sum(o["total_price"] for o in orders_detail)
    }


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    print("=" * 50)
    print("ChatKasir Synthetic Data Generator (Fixed)")
    print("=" * 50)

    food_list, _ = load_datasets()

    print(f"[INFO] Generate {TARGET_ROWS} data...")
    records = [generate_order(food_list) for _ in range(TARGET_ROWS)]

    df = pd.DataFrame(records)

    # 🔥 SAVE CSV AMAN
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        sep=";",                  # penting!
        encoding="utf-8-sig",
        quoting=csv.QUOTE_ALL    # penting!
    )

    df.to_excel(
    "synthetic_orders_multi.xlsx",
    index=False
    )

    print(f"[OK] File saved: {OUTPUT_FILE}")
    print(df.head())


if __name__ == "__main__":
    main()