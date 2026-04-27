import pandas as pd
import random

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Rule-Based Generation dengan bobot kategori populer
# ============================================================

# ============================================================
# PRODUK MANUAL PER KATEGORI (yang mungkin tidak ada di dataset)
# ============================================================
PRODUK_MANUAL = {
    'penyetan'        : [
        'ayam penyet', 'lele penyet', 'bebek penyet', 'tahu penyet',
        'tempe penyet', 'udang penyet', 'cumi penyet', 'ayam penyet sambal ijo',
        'lele penyet sambal bawang', 'bebek penyet sambal terasi',
    ],
    'nasi'            : [
        'nasi goreng', 'nasi uduk', 'nasi padang', 'nasi kuning',
        'nasi putih', 'nasi campur', 'nasi bakar', 'nasi kebuli',
        'nasi liwet', 'nasi goreng kampung', 'nasi goreng seafood',
        'nasi goreng spesial', 'nasi timbel', 'nasi pecel',
    ],
    'mie'             : [
        'mie ayam', 'mie goreng', 'mie rebus', 'bakmi goreng',
        'mie kuah', 'mie pangsit', 'mie ayam bakso', 'mie goreng seafood',
        'kwetiau goreng', 'kwetiau rebus', 'bihun goreng', 'bihun rebus',
    ],
    'bakso_soto'      : [
        'bakso', 'bakso urat', 'bakso malang', 'bakso gepeng',
        'soto ayam', 'soto betawi', 'soto lamongan', 'rawon',
        'sop buntut', 'sop ayam', 'coto makassar', 'konro',
    ],
    'gorengan_jajanan': [
        'tempe goreng', 'tahu goreng', 'pisang goreng', 'martabak',
        'martabak manis', 'martabak telur', 'risoles', 'pastel',
        'cireng', 'cilok', 'batagor', 'siomay', 'pempek',
        'kerupuk', 'tahu bulat', 'tahu crispy',
    ],
    'ayam'            : [
        'ayam goreng', 'ayam geprek', 'ayam bakar', 'fried chicken',
        'ayam crispy', 'ayam kremes', 'ayam rica rica', 'ayam kecap',
        'ayam sambal hijau', 'ayam sambal merah', 'ayam pop',
        'ayam bakar madu', 'chicken wings', 'ayam katsu',
    ],
    'seafood'         : [
        'udang goreng', 'cumi goreng', 'ikan bakar', 'ikan goreng',
        'udang saus tiram', 'cumi saus padang', 'kepiting saus',
        'ikan asam manis', 'udang tepung', 'kerang saus',
    ],
    'minuman_es'      : [
        'es teh', 'es jeruk', 'es campur', 'es buah',
        'es teh manis', 'es jeruk peras', 'es lemon tea',
        'es cincau', 'es kelapa muda', 'es cendol',
        'es dawet', 'es kopyor', 'jus alpukat', 'jus mangga',
        'jus jambu', 'jus semangka', 'jus wortel',
    ],
    'kopi_hangat'     : [
        'kopi susu', 'kopi hitam', 'americano', 'teh manis',
        'teh tarik', 'wedang jahe', 'wedang ronde', 'susu hangat',
        'coklat hangat', 'kopi tubruk', 'kopi gula aren',
        'cappuccino', 'latte', 'es kopi susu',
    ],
    'minuman_kekinian': [
        'boba', 'thai tea', 'taro', 'matcha latte',
        'brown sugar boba', 'cheese tea', 'es kopi susu gula aren',
        'kopi susu kekinian', 'green tea latte', 'strawberry tea',
        'lychee tea', 'passion fruit tea', 'mango smoothie',
    ],
}

# Bobot per kategori (semakin besar semakin sering muncul)
BOBOT_KATEGORI = {
    'penyetan'        : 50,
    'nasi'            : 80,
    'mie'             : 60,
    'bakso_soto'      : 50,
    'gorengan_jajanan': 40,
    'ayam'            : 80,
    'seafood'         : 30,
    'minuman_es'      : 60,
    'kopi_hangat'     : 50,
    'minuman_kekinian': 40,
    'lainnya'         : 0,
}

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

# ============================================================
# LOAD DATASET
# ============================================================
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

# ============================================================
# FILTER PRODUK DARI FOOD_UTAMA PER KATEGORI
# ============================================================
def filter_produk_dari_dataset(food_list):
    kata_kunci = {
        'penyetan'        : ['penyet'],
        'nasi'            : ['nasi'],
        'mie'             : ['mie', 'bakmi', 'kwetiau', 'bihun'],
        'bakso_soto'      : ['bakso', 'soto', 'rawon', 'sop', 'coto', 'konro'],
        'gorengan_jajanan': ['goreng', 'martabak', 'risoles', 'pastel', 'cireng',
                             'cilok', 'batagor', 'siomay', 'pempek'],
        'ayam'            : ['ayam', 'chicken'],
        'seafood'         : ['udang', 'cumi', 'ikan', 'kepiting', 'kerang'],
        'minuman_es'      : ['es ', 'jus'],
        'kopi_hangat'     : ['kopi', 'teh', 'wedang', 'susu'],
        'minuman_kekinian': ['boba', 'thai', 'matcha', 'taro', 'latte', 'smoothie'],
    }

    produk_per_kategori = {k: [] for k in kata_kunci}
    produk_lainnya      = []

    for produk in food_list:
        masuk_kategori = False
        for kategori, keywords in kata_kunci.items():
            if any(kw in produk for kw in keywords):
                produk_per_kategori[kategori].append(produk)
                masuk_kategori = True
                break
        if not masuk_kategori:
            produk_lainnya.append(produk)

    return produk_per_kategori, produk_lainnya

# ============================================================
# GABUNGKAN PRODUK MANUAL + DARI DATASET
# ============================================================
def gabungkan_produk(produk_per_kategori, produk_lainnya):
    gabungan = {}
    for kategori, produk_dataset in produk_per_kategori.items():
        produk_manual  = PRODUK_MANUAL.get(kategori, [])
        gabungan[kategori] = list(set(produk_dataset + produk_manual))
    gabungan['lainnya'] = produk_lainnya
    return gabungan

# ============================================================
# BUAT WEIGHTED FOOD LIST
# ============================================================
def buat_weighted_list(gabungan_produk):
    weighted_list = []
    for kategori, produk_list in gabungan_produk.items():
        bobot = BOBOT_KATEGORI.get(kategori, 0)
        if bobot > 0:
            weighted_list.extend(produk_list * bobot)
    return weighted_list

# ============================================================
# FORMAT HARGA
# ============================================================
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

# ============================================================
# APPLY SLANG
# ============================================================
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

# ============================================================
# GENERATE SATU BARIS
# ============================================================
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
    penjual    = random.choice(TEMPLATES_TANPA_HARGA_PENJUAL)
    input_text = f"{pembeli} [SEP] {penjual}" if penjual else pembeli
    return {
        "input_text"   : input_text,
        "product"      : produk,
        "quantity"     : qty,
        "price_satuan" : -1,
        "pattern"      : pattern,
    }

# ============================================================
# MAIN GENERATE
# ============================================================
def generate_dataset(weighted_list, formal_to_slang, target_rows,
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
            random.choice(weighted_list), random.randint(1, 10),
            random.choice(harga_range), pattern=1
        ))

    print("  Generating Pola 2...")
    for _ in range(n_pola2):
        rows.append(generate_order_dengan_harga(
            random.choice(weighted_list), random.randint(1, 10),
            random.choice(harga_range), pattern=2
        ))

    print("  Generating Pola 3...")
    for _ in range(n_pola3):
        row = generate_order_dengan_harga(
            random.choice(weighted_list), random.randint(1, 10),
            random.choice(harga_range), pattern=3
        )
        row["input_text"] = apply_slang(row["input_text"], formal_to_slang)
        rows.append(row)

    print("  Generating baris tanpa harga...")
    for _ in range(n_no_harga):
        rows.append(generate_order_tanpa_harga(
            random.choice(weighted_list), random.randint(1, 10),
            random.choice([1, 2, 3])
        ))

    random.shuffle(rows)
    return rows

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    RANDOM_SEED    = 42
    RATIO_POLA_1       = 0.3325   
    RATIO_POLA_2       = 0.3325
    RATIO_POLA_3       = 0.165
    RATIO_NO_HARGA     = 0.175

    random.seed(RANDOM_SEED)

    print("Loading datasets...")
    food_list, slang_dict, formal_to_slang = load_datasets()
    print(f"Food list   : {len(food_list)} produk")
    print(f"Slang dict  : {len(slang_dict)} entri")

    print("\nMemfilter dan menggabungkan produk per kategori...")
    produk_per_kategori, produk_lainnya = filter_produk_dari_dataset(food_list)
    gabungan = gabungkan_produk(produk_per_kategori, produk_lainnya)

    print("\nJumlah produk per kategori:")
    for kategori, produk in gabungan.items():
        print(f"  {kategori:20s}: {len(produk)} produk")

    weighted_list = buat_weighted_list(gabungan)
    print(f"\nTotal weighted list: {len(weighted_list)} entri")

    for target_rows in [10000, 50000, 100000]:
        print(f"\n{'='*50}")
        print(f"Generating {target_rows} baris...")
        print(f"{'='*50}")

        rows = generate_dataset(
            weighted_list, formal_to_slang, target_rows,
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

        filename = f'synthetic_orders_weighted_{target_rows}.csv'
        df.to_csv(filename, index=False)
        print(f"Tersimpan -> {filename}")