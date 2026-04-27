import pandas as pd

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Assessing & cleaning final food_utama.csv
# ============================================================

df = pd.read_csv('../final/food_utama.csv')

print("=" * 50)
print("ASSESSING food_utama.csv")
print("=" * 50)

# Info dasar
print(f"\nJumlah baris  : {len(df)}")
print(f"Kolom         : {df.columns.tolist()}")
print(f"\nPreview:\n{df.head(10)}")

# Cek null
print(f"\nNilai kosong  : {df['name'].isnull().sum()}")

# Cek duplikat
print(f"Duplikat      : {df.duplicated().sum()}")

# Cek panjang nama
df['panjang_kata'] = df['name'].str.split().str.len()
print(f"\nDistribusi panjang nama (kata):")
print(df['panjang_kata'].value_counts().sort_index())

# Cek nama terpendek (1 kata)
print(f"\nNama dengan 1 kata (sample 10):")
print(df[df['panjang_kata'] == 1]['name'].head(10).tolist())

# Cek nama terpanjang
print(f"\nNama terpanjang (5 kata ke atas):")
print(df[df['panjang_kata'] >= 5]['name'].head(10).tolist())

# Cek masih ada angka
print(f"\nMasih ada angka: {df['name'].str.contains(r'[0-9]', regex=True).sum()} baris")

# Cek masih ada karakter spesial
print(f"Masih ada karakter spesial: {df['name'].str.contains(r'[^a-z\s]', regex=True).sum()} baris")

# Cek huruf kapital
print(f"Masih ada huruf kapital: {df['name'].str.contains(r'[A-Z]', regex=True).sum()} baris")

# Cek spasi berlebih
print(f"Ada spasi berlebih: {df['name'].str.contains(r'\s{2,}', regex=True).sum()} baris")

# ============================================================
# CLEANING
# ============================================================

print("\n" + "=" * 50)
print("CLEANING food_utama.csv")
print("=" * 50)

# Fix spasi berlebih
before = len(df)
df['name'] = df['name'].str.replace(r'\s{2,}', ' ', regex=True).str.strip()

# Hapus duplikat yang mungkin muncul setelah fix spasi
df = df.drop_duplicates().reset_index(drop=True)

print(f"Sebelum : {before} baris")
print(f"Setelah : {len(df)} baris")
print(f"Dibuang : {before - len(df)} baris")

# Hapus kolom bantu
df = df.drop(columns=['panjang_kata'])

# Verifikasi final
print(f"\nVerifikasi final:")
print(f"Nilai kosong     : {df['name'].isnull().sum()}")
print(f"Duplikat         : {df.duplicated().sum()}")
print(f"Spasi berlebih   : {df['name'].str.contains(r'chr(92)s{2,}', regex=True).sum()}")
print(f"Total baris final: {len(df)}")
print(f"\nPreview:\n{df.head(10)}")

# Simpan
df.to_csv('../final/food_utama.csv', index=False)
print("\nTersimpan -> food_utama.csv")