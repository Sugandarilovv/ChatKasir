import pandas as pd

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Analisis hasil generate dataset sintetis v3
#            — Diselaraskan dengan struktur output generate_data.py
# ============================================================

# Kolom output generate_data.py:
#   input_text   : "{pembeli} [SEP] {penjual}"
#   product      : nama produk (pola 1-3) atau "produk1 & produk2" (pola 4)
#   quantity     : qty (int/str untuk pola 1-3) atau "qty1 & qty2" (pola 4)
#   price_satuan : harga int (pola 1-3) atau -1 (pola 4 & tanpa harga)
#   pattern      : 1 | 2 | 3 | 4
#                  catatan: baris tanpa harga memakai pattern 1/2/3
#                  (generate_order_tanpa_harga → pattern=random.choice([1,2,3]))

FOOD_PATH = '../final/food_utama.csv'
FILENAME  = 'chatkasir_synthetic.csv'

# ============================================================
# LOAD FOOD LIST (referensi jumlah produk target)
# ============================================================
try:
    food_list = (
        pd.read_csv(FOOD_PATH)['name']
        .dropna()
        .str.lower()
        .str.strip()
        .tolist()
    )
except FileNotFoundError:
    print(f"[WARNING] {FOOD_PATH} tidak ditemukan — kolom 'total_produk_food_list' akan diisi 0.")
    food_list = []

# ============================================================
# LOAD DATASET HASIL GENERATE
# ============================================================
try:
    df = pd.read_csv(FILENAME)
except FileNotFoundError:
    print(f"[ERROR] File {FILENAME} belum ada, pastikan sudah di-generate.")
    exit()

# ============================================================
# VALIDASI KOLOM
# Kolom wajib sesuai generate_data.py
# ============================================================
KOLOM_WAJIB = ['input_text', 'product', 'quantity', 'price_satuan', 'pattern']
kolom_hilang = [k for k in KOLOM_WAJIB if k not in df.columns]
if kolom_hilang:
    print(f"[ERROR] Kolom berikut tidak ditemukan di dataset: {kolom_hilang}")
    exit()

# ============================================================
# PISAHKAN POLA 4 (MAJEMUK) vs POLA 1/2/3 (SINGLE)
# ============================================================
df_single  = df[df['pattern'] != 4].copy()
df_majemuk = df[df['pattern'] == 4].copy()

# ============================================================
# HITUNG PRODUK UNIK EFEKTIF
# Pola 4 menyimpan "produk1 & produk2" → flatten dulu
# ============================================================
produk_majemuk_flat = set()
for val in df_majemuk['product'].dropna():
    for p in str(val).split(' & '):
        produk_majemuk_flat.add(p.strip())

produk_unik_single   = set(df_single['product'].dropna().unique())
produk_unik_efektif  = produk_unik_single | produk_majemuk_flat
n_produk_unik        = len(produk_unik_efektif)

# ============================================================
# DISTRIBUSI PATTERN
# Catatan: baris tanpa harga (price_satuan == -1) tersebar di
# pattern 1/2/3 (sesuai generate_order_tanpa_harga) dan pola 4.
# Pola 4 selalu price_satuan == -1.
# ============================================================
n_pattern = df['pattern'].value_counts().sort_index()

# Baris tanpa harga: price_satuan == -1
df_tanpa_harga    = df[df['price_satuan'] == -1]
n_tanpa_harga     = len(df_tanpa_harga)

# Baris tanpa harga bukan pola 4 (pola 1/2/3 yang tidak punya harga)
n_tanpa_harga_non4 = len(df_tanpa_harga[df_tanpa_harga['pattern'] != 4])

# ============================================================
# DISTRIBUSI QTY
# qty bisa: angka (int) atau string ejaan ("satu", "seporsi", dst.)
# Pola 4: "qty1 & qty2"
# ============================================================
qty_single  = df_single['quantity'].astype(str)
qty_numeric = pd.to_numeric(qty_single, errors='coerce')
n_qty_angka  = qty_numeric.notna().sum()
n_qty_string = qty_numeric.isna().sum()

# ============================================================
# TOP 100 PRODUK (hanya dari baris single / pola 1-3)
# ============================================================
top100 = (
    df_single['product']
    .value_counts()
    .head(100)
    .reset_index()
)
top100.columns = ['product', 'jumlah_muncul']

# ============================================================
# RINGKASAN ANALISIS
# ============================================================
analisis = {
    'dataset'                   : FILENAME,
    'total_baris'               : len(df),

    # --- Distribusi pattern ---
    'pattern_1'                 : int(n_pattern.get(1, 0)),
    'pattern_2'                 : int(n_pattern.get(2, 0)),
    'pattern_3_slang'           : int(n_pattern.get(3, 0)),
    'pattern_4_majemuk'         : int(n_pattern.get(4, 0)),

    # --- Harga ---
    'baris_tanpa_harga_total'   : n_tanpa_harga,          # pola 4 + pola 1/2/3 tanpa harga
    'baris_tanpa_harga_non_p4'  : n_tanpa_harga_non4,     # hanya pola 1/2/3 tanpa harga
    'baris_dengan_harga'        : len(df) - n_tanpa_harga,

    # --- Qty ---
    'qty_format_angka'          : int(n_qty_angka),
    'qty_format_string_ejaan'   : int(n_qty_string),

    # --- Produk unik ---
    'produk_unik_efektif'       : n_produk_unik,
    'total_produk_food_list'    : len(food_list),
    'produk_belum_ter_generate' : max(0, len(food_list) - n_produk_unik),
}

df_hasil = pd.DataFrame([analisis])

# ============================================================
# SIMPAN OUTPUT
# ============================================================
top100.to_csv('analisis_top100_chatkasir.csv', index=False)
print("Tersimpan -> analisis_top100_chatkasir.csv")

df_hasil.to_csv('analisis_ringkasan.csv', index=False)
print("Tersimpan -> analisis_ringkasan.csv")

# ============================================================
# PREVIEW
# ============================================================
print("\n" + "=" * 60)
print("RINGKASAN DATASET")
print("=" * 60)
for k, v in analisis.items():
    print(f"  {k:<35}: {v}")

print("\n" + "=" * 60)
print("TOP 10 PRODUK TERBANYAK (Single / Pola 1-3)")
print("=" * 60)
print(top100.head(10).to_string(index=False))

print("\n" + "=" * 60)
print("DISTRIBUSI PATTERN")
print("=" * 60)
print(df['pattern'].value_counts().sort_index().to_string())