import pandas as pd
import re
import os

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Eksplorasi dan cleaning dataset GoFood
# ============================================================

print("=" * 50)
print("GOFOOD DATASET")
print("=" * 50)

# Load dataset
path = 'food_gofood_raw.csv'
print(f"Folder aktif : {os.getcwd()}")
print(f"File ada     : {os.path.exists(path)}")

df = pd.read_csv(path)

# Eksplorasi awal
print(f"\nJumlah baris  : {len(df)}")
print(f"Kolom         : {df.columns.tolist()}")
print(f"Produk unik   : {df['product'].nunique()}")
print(f"Nilai kosong  : {df['product'].isnull().sum()}")
print(f"\nPreview kolom product:\n{df['product'].head(10)}")

# ============================================================
# CLEANING
# ============================================================

# Ambil kolom product saja
df_gofood = df[['product']].copy()

# Lowercase + strip
df_gofood['product'] = df_gofood['product'].str.lower().str.strip()

# Hapus prefix umum: hot, ice, large, small, medium, regular, jumbo
df_gofood['product'] = df_gofood['product'].str.replace(
    r'^(hot|ice|iced|large|small|medium|regular|jumbo)\s+', '', regex=True
)

# Hapus teks dalam tanda kurung
df_gofood['product'] = df_gofood['product'].str.replace(
    r'\(.*?\)', '', regex=True
).str.strip()

# Hapus produk yang mengandung kata bahasa Inggris
kata_inggris = [
    'chicken', 'beef', 'fish', 'rice', 'fried', 'grilled',
    'sauce', 'soup', 'salad', 'cake', 'bread', 'potato',
    'mushroom', 'cheese', 'butter', 'cream', 'truffle',
    'asparagus', 'spinach', 'maple', 'chilli', 'house',
    'parmesan', 'mashed', 'roasted', 'steamed', 'baked'
]
pola = '|'.join(kata_inggris)
df_gofood = df_gofood[
    ~df_gofood['product'].str.contains(pola, case=False, regex=True)
]

# Hapus duplikat
df_gofood = df_gofood.drop_duplicates().reset_index(drop=True)

# ============================================================
# HASIL
# ============================================================

print("\n" + "=" * 50)
print("SETELAH CLEANING")
print("=" * 50)
print(f"Total produk unik: {len(df_gofood)}")
print(f"\nPreview:\n{df_gofood.head(20)}")

# Simpan
df_gofood.to_csv('food_gofood_clean.csv', index=False)
print("\nTersimpan -> food_gofood_clean.csv")