import pandas as pd

# =========================
# 1. Load dataset
# =========================
df_food = pd.read_csv('food_eriko_clean.csv')
df_gofood = pd.read_csv('food_gofood_clean.csv')

# =========================
# 2. Samakan nama kolom
# =========================
df_gofood = df_gofood.rename(columns={'product': 'name'})

print(f"Dataset food lama : {len(df_food)} baris")
print(f"Dataset GoFood    : {len(df_gofood)} baris")

# =========================
# 3. Gabungkan dataset
# =========================
df_combined = pd.concat([df_food, df_gofood], ignore_index=True)

# =========================
# 4. Normalisasi teks (PENTING)
# =========================
df_combined['name'] = (
    df_combined['name']
    .astype(str)              # pastikan string
    .str.lower()              # huruf kecil semua
    .str.strip()              # hapus spasi depan/belakang
    .str.replace(r'\s+', ' ', regex=True)  # hapus spasi double
)

# =========================
# 5. Hapus duplikat
# =========================
before = len(df_combined)

df_combined = df_combined.drop_duplicates(subset='name').reset_index(drop=True)

after = len(df_combined)

print(f"Sebelum deduplikasi : {before} baris")
print(f"Setelah digabung    : {after} baris")
print(f"Data duplikat hilang: {before - after} baris")

# =========================
# 6. Simpan hasil
# =========================
df_combined.to_csv('food_utama_clean.csv', index=False)

print("\nTersimpan -> food_utama_clean.csv")
print("\nContoh data:")
print(df_combined.head(10))