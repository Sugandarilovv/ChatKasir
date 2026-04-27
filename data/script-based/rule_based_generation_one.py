import pandas as pd
import random

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# ============================================================

SAPAAN  = ['bang', 'kak', 'kk', 'bg', 'mas', 'mbak', 'min', 'bu', 'pak', '']
PENUTUP = ['ya', 'dong', 'kak', 'ya kak', 'dong kak', 'nih', '']

TEMPLATES_PEMBELI = [
    "{sapaan} {qty} {produk} {penutup}",
    "{sapaan} mau pesen {qty} {produk} {penutup}",
    "kak mau order {qty} {produk} {penutup}",
    "minta {qty} {produk} {penutup}",
    "{qty} {produk} {penutup}",
    "pesan {qty} {produk} {penutup}",
    "beli {qty} {produk} {penutup}",
    "{sapaan} bisa pesan {qty} {produk} {penutup}",
    "mau {qty} {produk} {penutup}",
    "boleh pesan {qty} {produk} {penutup}",
]

TEMPLATES_PENJUAL = [
    "oke kak {produk} harganya {harga} totalnya {total}",
    "siap kak {produk} {harga} per porsi total {total} ya",
    "{produk} {harga} ya kak jadi {total}",
    "baik kak {produk} {harga} satuan totalnya {total}",
    "noted kak {produk} {harga} per porsi totalnya {total}",
    "oke {produk} harga {harga} total {total} ya kak",
    "siap {produk} {harga} totalnya {total} kak",
]

TEMPLATES_TANPA_HARGA_PEMBELI = [
    "{sapaan} {qty} {produk} {penutup}",
    "kak mau pesen {qty} {produk} {penutup}",
    "minta {qty} {produk} {penutup}",
    "{qty} {produk} {penutup}",
    "pesan {qty} {produk} {penutup}",
]

TEMPLATES_TANPA_HARGA_PENJUAL = [
    "oke siap kak",
    "noted kak ditunggu ya",
    "oke kak pesanannya masuk ya",
    "siap kak",
    "baik kak",
    "oke noted",
    "",
]

def load_datasets():
    df_food  = pd.read_csv('../final/food_utama.csv')
    df_slang = pd.read_csv('../final/slang_utama.csv')
    food_list  = df_food['name'].dropna().str.lower().str.strip().tolist()
    slang_dict = dict(zip(
        df_slang['slang'].str.lower().str.strip(),
        df_slang['formal'].str.lower().str.strip()
    ))
    formal_to_slang = {}
    for slang, formal in slang_dict.items():
        if formal not in formal_to_slang:
            formal_to_slang[formal] = []
        formal_to_slang[formal].append(slang)
    return food_list, slang_dict, formal_to_slang

def format_price_text(price: int) -> str:
    formats = [
        f"{price // 1000}rb",
        f"{price // 1000}k",
        f"{price // 1000} ribu",
        f"{price // 1000}.000",
        f"rp{price // 1000}rb",
        f"rp {price // 1000}.000",
    ]
    return random.choice(formats)

def apply_slang(text: str, formal_to_slang: dict) -> str:
    words  = text.split()
    result = []
    for word in words:
        word_lower = word.lower()
        if word_lower in formal_to_slang and random.random() < 0.4:
            result.append(random.choice(formal_to_slang[word_lower]))
        else:
            result.append(word)
    return " ".join(result)

def generate_order_dengan_harga(produk, qty, price, pattern):
    sapaan  = random.choice(SAPAAN)
    penutup = random.choice(PENUTUP)
    harga   = format_price_text(price)
    total   = format_price_text(price * qty)
    pembeli = random.choice(TEMPLATES_PEMBELI).format(
        sapaan=sapaan, qty=qty, produk=produk, penutup=penutup
    ).strip()
    penjual = random.choice(TEMPLATES_PENJUAL).format(
        produk=produk, harga=harga, total=total
    ).strip()
    return {
        "input_text"   : f"{pembeli} [SEP] {penjual}",
        "product"      : produk,
        "quantity"     : qty,
        "price_satuan" : price,
        "pattern"      : pattern,
    }

def generate_order_tanpa_harga(produk, qty, pattern):
    sapaan  = random.choice(SAPAAN)
    penutup = random.choice(PENUTUP)
    pembeli = random.choice(TEMPLATES_TANPA_HARGA_PEMBELI).format(
        sapaan=sapaan, qty=qty, produk=produk, penutup=penutup
    ).strip()
    penjual = random.choice(TEMPLATES_TANPA_HARGA_PENJUAL)
    input_text = f"{pembeli} [SEP] {penjual}" if penjual else pembeli
    return {
        "input_text"   : input_text,
        "product"      : produk,
        "quantity"     : qty,
        "price_satuan" : -1,
        "pattern"      : pattern,
    }

def generate_dataset(food_list, formal_to_slang, target_rows,
                     ratio_pola_1, ratio_pola_2, ratio_pola_3, ratio_no_harga):
    rows        = []
    n_pola1     = int(target_rows * ratio_pola_1)
    n_pola2     = int(target_rows * ratio_pola_2)
    n_pola3     = int(target_rows * ratio_pola_3)
    n_no_harga  = int(target_rows * ratio_no_harga)
    harga_range = list(range(3000, 75001, 1000))

    print("  Generating Pola 1...")
    for _ in range(n_pola1):
        rows.append(generate_order_dengan_harga(
            random.choice(food_list), random.randint(1, 10),
            random.choice(harga_range), pattern=1
        ))

    print("  Generating Pola 2...")
    for _ in range(n_pola2):
        rows.append(generate_order_dengan_harga(
            random.choice(food_list), random.randint(1, 10),
            random.choice(harga_range), pattern=2
        ))

    print("  Generating Pola 3...")
    for _ in range(n_pola3):
        row = generate_order_dengan_harga(
            random.choice(food_list), random.randint(1, 10),
            random.choice(harga_range), pattern=3
        )
        row["input_text"] = apply_slang(row["input_text"], formal_to_slang)
        rows.append(row)

    print("  Generating baris tanpa harga...")
    for _ in range(n_no_harga):
        rows.append(generate_order_tanpa_harga(
            random.choice(food_list), random.randint(1, 10),
            random.choice([1, 2, 3])
        ))

    random.shuffle(rows)
    return rows

if __name__ == "__main__":
    RANDOM_SEED    = 42
    RATIO_POLA_1   = 0.40
    RATIO_POLA_2   = 0.40
    RATIO_POLA_3   = 0.20
    RATIO_NO_HARGA = 0.175

    random.seed(RANDOM_SEED)

    print("Loading datasets...")
    food_list, slang_dict, formal_to_slang = load_datasets()
    print(f"Food list   : {len(food_list)} produk")
    print(f"Slang dict  : {len(slang_dict)} entri")

    for target_rows in [10000, 50000, 100000]:
        print(f"\n{'='*50}")
        print(f"Generating {target_rows} baris...")
        print(f"{'='*50}")

        rows = generate_dataset(
            food_list, formal_to_slang, target_rows,
            RATIO_POLA_1, RATIO_POLA_2, RATIO_POLA_3, RATIO_NO_HARGA
        )
        df = pd.DataFrame(rows)

        print(f"\n=== HASIL {target_rows} ===")
        print(f"Total baris              : {len(df)}")
        print(f"Distribusi pattern       :\n{df['pattern'].value_counts()}")
        print(f"Baris tanpa harga        : {(df['price_satuan'] == -1).sum()}")
        print(f"Produk unik ter-generate : {df['product'].nunique()} dari {len(food_list)}")
        print(f"Produk belum ter-generate: {len(food_list) - df['product'].nunique()}")
        print(f"\nTop 10 produk terbanyak muncul:")
        print(df['product'].value_counts().head(10))
        print(f"\nPreview:\n{df.head(5)}")

        filename = f'synthetic_orders_{target_rows}.csv'
        df.to_csv(filename, index=False)
        print(f"Tersimpan -> {filename}")