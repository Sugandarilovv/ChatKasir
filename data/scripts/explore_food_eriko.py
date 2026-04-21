from datasets import load_dataset
import pandas as pd

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Eksplorasi dan cleaning dataset indonesian-food
#            dari Hugging Face (eriko-syah/indonesian-food)
# ============================================================

print("=" * 50)
print("INDONESIAN FOOD - eriko-syah")
print("=" * 50)

# Download
print("Downloading indonesian-food...")
food = load_dataset("eriko-syah/indonesian-food")
df_food = pd.DataFrame(food['train'])

# Eksplorasi awal
print(f"\nJumlah baris  : {len(df_food)}")
print(f"Kolom         : {df_food.columns.tolist()}")
print(f"\nPreview:\n{df_food.head(5)}")

# Simpan mentahan
df_food.to_csv('food_eriko_raw.csv', index=False)
print(f"\nTersimpan -> food_eriko_raw.csv ({len(df_food)} baris)")

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
df_food_clean.to_csv('food_eriko_clean.csv', index=False)
print("Tersimpan -> food_eriko_clean.csv")