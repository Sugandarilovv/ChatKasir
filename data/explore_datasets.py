from datasets import load_dataset
import pandas as pd
import re

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Eksplorasi dan cleaning dataset indonesian-food
#            dan indonesia-slang dari Hugging Face
# ============================================================


# ============================================================
# 1. DATASET INDONESIAN FOOD
# ============================================================

print("=" * 50)
print("1. INDONESIAN FOOD")
print("=" * 50)

# Download
print("Downloading indonesian-food...")
food = load_dataset("eriko-syah/indonesian-food")
df_food = pd.DataFrame(food['train'])

# Eksplorasi awal
print(f"\nJumlah baris  : {len(df_food)}")
print(f"Kolom         : {df_food.columns.tolist()}")
print(f"\nPreview:\n{df_food.head(5)}")

# Filter kolom yang dibutuhkan
df_food_clean = df_food[['name']].copy()

# Cleaning: lowercase + strip
df_food_clean['name'] = df_food_clean['name'].str.lower().str.strip()

# Cek kualitas data
print(f"\nNilai kosong  : {df_food_clean['name'].isnull().sum()}")
print(f"Duplikat      : {df_food_clean.duplicated().sum()}")

# Tampilkan duplikat sebelum dihapus
duplikat_food = df_food_clean[df_food_clean.duplicated(keep=False)].sort_values('name')
if len(duplikat_food) > 0:
    print(f"\nDuplikat yang ditemukan:\n{duplikat_food}")

# Hapus duplikat
df_food_clean = df_food_clean.drop_duplicates().reset_index(drop=True)

print(f"\nTotal data final: {len(df_food_clean)} nama makanan")

# Simpan
df_food_clean.to_csv('indonesian_food_clean.csv', index=False)
print("Tersimpan -> indonesian_food_clean.csv")


# ============================================================
# 2. DATASET INDONESIA SLANG
# ============================================================

print("\n" + "=" * 50)
print("2. INDONESIA SLANG")
print("=" * 50)

# Download
print("Downloading indonesia-slang...")
slang = load_dataset("nahiar/indonesia-slang")
df_slang = pd.DataFrame(slang['train'])

# Eksplorasi awal
print(f"\nJumlah baris  : {len(df_slang)}")
print(f"Kolom         : {df_slang.columns.tolist()}")
print(f"\nPreview:\n{df_slang.head(5)}")

# Ambil kolom yang dibutuhkan + lowercase
df_slang_clean = df_slang[['slang', 'formal']].copy()
df_slang_clean['slang']  = df_slang_clean['slang'].str.lower().str.strip()
df_slang_clean['formal'] = df_slang_clean['formal'].str.lower().str.strip()

# Cek kualitas awal
print(f"\nNilai kosong slang  : {df_slang_clean['slang'].isnull().sum()}")
print(f"Nilai kosong formal : {df_slang_clean['formal'].isnull().sum()}")
print(f"Duplikat            : {df_slang_clean.duplicated().sum()}")

# Hapus duplikat
df_slang_clean = df_slang_clean.drop_duplicates().reset_index(drop=True)

# --- Filter 1: panjang karakter slang <= 20 ---
df_slang_clean['panjang'] = df_slang_clean['slang'].str.len()
df_slang_clean = df_slang_clean[df_slang_clean['panjang'] <= 20].copy()
df_slang_clean = df_slang_clean.drop(columns=['panjang'])

# --- Filter 2: slang tidak mengandung angka ---
df_slang_clean = df_slang_clean[
    ~df_slang_clean['slang'].str.contains(r'[0-9]', regex=True)
].copy()

# --- Filter 3: bentuk formal maksimal 3 kata ---
df_slang_clean = df_slang_clean[
    df_slang_clean['formal'].str.split().str.len() <= 3
].copy()

df_slang_final = df_slang_clean.reset_index(drop=True)

print(f"\nTotal data final: {len(df_slang_final)} entri slang")
print(f"\nPreview hasil cleaning:\n{df_slang_final.head(10)}")

# Simpan
df_slang_final.to_csv('indonesia_slang_clean.csv', index=False)
print("Tersimpan -> indonesia_slang_clean.csv")


# ============================================================
# 3. RINGKASAN AKHIR
# ============================================================

print("\n" + "=" * 50)
print("RINGKASAN")
print("=" * 50)
print(f"indonesian_food_clean : {len(df_food_clean):>6} baris")
print(f"indonesia_slang_clean : {len(df_slang_final):>6} baris")
print("Semua dataset berhasil disimpan.")