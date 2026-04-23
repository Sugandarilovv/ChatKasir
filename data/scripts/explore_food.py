import pandas as pd

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Eksplorasi, filter, dan merge dataset food
# ============================================================

print("=" * 50)
print("1. LOAD DATASET")
print("=" * 50)

df_indonesian = pd.read_csv('../raw/food_indonesian_raw.csv')
df_gofood     = pd.read_csv('../raw/food_gofood_raw.csv')

print(f"Indonesian food : {len(df_indonesian)} baris | kolom: {df_indonesian.columns.tolist()}")
print(f"GoFood          : {len(df_gofood)} baris | kolom: {df_gofood.columns.tolist()}")

# ============================================================
print("\n" + "=" * 50)
print("2. FILTER KOLOM")
print("=" * 50)

df_indonesian_clean = df_indonesian[['name']].copy()

df_gofood_clean = df_gofood[['product']].copy()
df_gofood_clean = df_gofood_clean.rename(columns={'product': 'name'})

print(f"Indonesian food : {len(df_indonesian_clean)} baris")
print(f"GoFood          : {len(df_gofood_clean)} baris")

# ============================================================
print("\n" + "=" * 50)
print("3. MERGE")
print("=" * 50)

df_merged = pd.concat([df_indonesian_clean, df_gofood_clean], ignore_index=True)
print(f"Setelah merge   : {len(df_merged)} baris")

df_merged['name'] = df_merged['name'].str.lower().str.strip()
df_merged = df_merged.dropna(subset=['name'])

before = len(df_merged)
df_merged = df_merged.drop_duplicates().reset_index(drop=True)
print(f"Setelah dedup   : {len(df_merged)} baris (dibuang: {before - len(df_merged)})")
print(f"\nPreview:\n{df_merged.head(10)}")

df_merged.to_csv('food_merged.csv', index=False)
print(f"\nTersimpan -> food_merged.csv ({len(df_merged)} baris)")

# ============================================================
print("\n" + "=" * 50)
print("4. CLEANING LANJUTAN")
print("=" * 50)

df_merged = df_merged.dropna(subset=['name']).copy()
df_merged['name'] = df_merged['name'].astype(str).str.strip()

# Hapus yang mengandung angka
before = len(df_merged)
df_merged = df_merged[~df_merged['name'].str.contains(r'[0-9]', regex=True)]
print(f"Setelah hapus angka           : {len(df_merged)} baris (dibuang: {before - len(df_merged)})")

# Hapus yang mengandung satuan berat/volume
satuan = [
    'gram', 'gr', 'kg', 'kilogram',
    'ml', 'liter', 'lt', 'cc', 'ons',
    'mg', 'pcs', 'pack', 'sachet',
    'botol', 'kaleng', 'porsi'
]
pola_satuan = '(?:' + '|'.join(satuan) + ')'
before = len(df_merged)
df_merged = df_merged[~df_merged['name'].str.contains(pola_satuan, regex=True, case=False)]
print(f"Setelah hapus satuan          : {len(df_merged)} baris (dibuang: {before - len(df_merged)})")

# Hapus yang terlalu panjang (> 5 kata)
before = len(df_merged)
df_merged = df_merged[df_merged['name'].str.split().str.len() <= 5]
print(f"Setelah hapus nama panjang    : {len(df_merged)} baris (dibuang: {before - len(df_merged)})")

# Hapus karakter spesial
before = len(df_merged)
df_merged = df_merged.copy()
df_merged['name'] = df_merged['name'].str.replace(r'[^a-z\s]', '', regex=True).str.strip()
df_merged = df_merged[df_merged['name'] != '']
df_merged = df_merged.drop_duplicates().reset_index(drop=True)
print(f"Setelah hapus karakter spesial: {len(df_merged)} baris (dibuang: {before - len(df_merged)})")

# Hapus kata tidak relevan
kata_tidak_relevan = [
    'bundle', 'paket', 'lainnya', 'other', 'dll',
    'promo', 'free', 'gratis', 'bonus', 'voucher',
    'add on', 'addon', 'tambahan', 'pilihan', 'custom',
    'signature', 'recommendation', 'favorit', 'bestseller',
    'new', 'sold out', 'habis'
]
pola_tidak_relevan = '(?:' + '|'.join(kata_tidak_relevan) + ')'
before = len(df_merged)
df_merged = df_merged[~df_merged['name'].str.contains(pola_tidak_relevan, regex=True, case=False)]
print(f"Setelah hapus tidak relevan   : {len(df_merged)} baris (dibuang: {before - len(df_merged)})")

df_merged = df_merged.sort_values('name').reset_index(drop=True)

print(f"\nTotal data final : {len(df_merged)} nama makanan")
print(f"\nPreview:\n{df_merged.head(20)}")

df_merged.to_csv('../final/food_utama.csv', index=False)
print(f"\nTersimpan -> ../final/food_utama.csv ({len(df_merged)} baris)")