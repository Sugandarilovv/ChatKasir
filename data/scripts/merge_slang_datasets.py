import pandas as pd

# ============================================================
# CHATKASIR - Data Engineering
# ============================================================

print("=" * 50)
print("MERGE DATASET SLANG")
print("=" * 50)

# =========================
# 1. Load data
# =========================
df_nahiar    = pd.read_csv('slang_nahiar_clean.csv')
df_theonlydo = pd.read_csv('slang_theonlydo_clean.csv')

print(f"slang_nahiar_clean    : {len(df_nahiar)} baris")
print(f"slang_theonlydo_clean : {len(df_theonlydo)} baris")

# =========================
# 2. Gabungkan
# =========================
df_merged = pd.concat([df_nahiar, df_theonlydo], ignore_index=True)
print(f"\nSetelah digabung      : {len(df_merged)} baris")

# =========================
# 3. Normalisasi teks (PENTING)
# =========================
df_merged['slang'] = (
    df_merged['slang']
    .astype(str)
    .str.lower()
    .str.strip()
    .str.replace(r'\s+', ' ', regex=True)
)

# =========================
# 4. Hapus duplikat
# =========================
before = len(df_merged)

df_merged = df_merged.drop_duplicates(subset=['slang']).reset_index(drop=True)

after = len(df_merged)

print(f"Setelah hapus duplikat: {after} baris")
print(f"Data terhapus         : {before - after} baris")

# =========================
# 5. Hapus data kosong (opsional tapi bagus)
# =========================
df_merged = df_merged[df_merged['slang'] != '']

# =========================
# 6. Preview
# =========================
print(f"\nPreview:\n{df_merged.head(10)}")

# =========================
# 7. Simpan
# =========================
df_merged.to_csv('slang_utama_clean.csv', index=False)

print("\nTersimpan -> slang_utama_clean.csv")