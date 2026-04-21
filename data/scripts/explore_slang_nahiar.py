from datasets import load_dataset
import pandas as pd

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Eksplorasi dan cleaning dataset indonesia-slang
#            dari Hugging Face (nahiar/indonesia-slang)
# ============================================================

print("=" * 50)
print("INDONESIA SLANG - nahiar")
print("=" * 50)

# Download
print("Downloading indonesia-slang...")
slang = load_dataset("nahiar/indonesia-slang")
df_slang = pd.DataFrame(slang['train'])

# Eksplorasi awal
print(f"\nJumlah baris  : {len(df_slang)}")
print(f"Kolom         : {df_slang.columns.tolist()}")
print(f"\nPreview:\n{df_slang.head(5)}")

# Simpan mentahan
df_slang.to_csv('slang_nahiar_raw.csv', index=False)
print(f"\nTersimpan -> slang_nahiar_raw.csv ({len(df_slang)} baris)")

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
df_slang_final.to_csv('slang_nahiar_clean.csv', index=False)
print("Tersimpan -> slang_nahiar_clean.csv")