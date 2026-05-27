import pandas as pd

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Assessing & cleaning final slang_utama.csv
# ============================================================

df = pd.read_csv('../final/slang_utama.csv')

print("=" * 50)
print("ASSESSING slang_utama.csv")
print("=" * 50)

# Info dasar
print(f"\nJumlah baris  : {len(df)}")
print(f"Kolom         : {df.columns.tolist()}")
print(f"\nPreview:\n{df.head(10)}")

# Cek null
print(f"\nNilai kosong slang  : {df['slang'].isnull().sum()}")
print(f"Nilai kosong formal : {df['formal'].isnull().sum()}")

# Cek duplikat
print(f"Duplikat            : {df.duplicated().sum()}")
print(f"Duplikat kolom slang: {df['slang'].duplicated().sum()}")

# Cek huruf kapital
print(f"\nHuruf kapital slang  : {df['slang'].str.contains(r'[A-Z]', regex=True).sum()} baris")
print(f"Huruf kapital formal : {df['formal'].str.contains(r'[A-Z]', regex=True).sum()} baris")

# Cek spasi berlebih
print(f"\nSpasi berlebih slang  : {df['slang'].str.contains(r'\s{2,}', regex=True).sum()} baris")
print(f"Spasi berlebih formal : {df['formal'].str.contains(r'chr(92)s{2,}', regex=True).sum()} baris")

# Cek slang = formal (tidak berguna)
df['sama'] = df['slang'] == df['formal']
print(f"\nSlang sama dengan formal: {df['sama'].sum()} baris")
print(df[df['sama'] == True].head(10))

# Cek panjang slang
df['panjang_slang'] = df['slang'].str.len()
print(f"\nRata-rata panjang slang : {df['panjang_slang'].mean():.1f} karakter")
print(f"Slang terpendek         : {df['panjang_slang'].min()} karakter")
print(f"Slang terpanjang        : {df['panjang_slang'].max()} karakter")

# Sample slang terpendek
print(f"\nSlang 1 karakter:")
print(df[df['panjang_slang'] == 1][['slang', 'formal']].head(10))

# ============================================================
# CLEANING
# ============================================================

print("\n" + "=" * 50)
print("CLEANING slang_utama.csv")
print("=" * 50)

before = len(df)

# Hapus slang yang sama dengan formal
df = df[df['slang'] != df['formal']].copy()
print(f"Hapus slang = formal : {before - len(df)} baris dibuang")

# Fix spasi berlebih
df['slang']  = df['slang'].str.replace(r'\s{2,}', ' ', regex=True).str.strip()
df['formal'] = df['formal'].str.replace(r'\s{2,}', ' ', regex=True).str.strip()

# Hapus duplikat setelah cleaning
before2 = len(df)
df = df.drop_duplicates(subset=['slang']).reset_index(drop=True)
print(f"Hapus duplikat       : {before2 - len(df)} baris dibuang")

# Hapus kolom bantu
df = df.drop(columns=['sama', 'panjang_slang'])

# Verifikasi final
print(f"\nVerifikasi final:")
print(f"Nilai kosong slang  : {df['slang'].isnull().sum()}")
print(f"Nilai kosong formal : {df['formal'].isnull().sum()}")
print(f"Duplikat            : {df.duplicated().sum()}")
print(f"Slang = formal      : {(df['slang'] == df['formal']).sum()}")
print(f"Total baris final   : {len(df)}")
print(f"\nPreview:\n{df.head(10)}")

# Simpan
df.to_csv('../final/slang_utama.csv', index=False)
print("\nTersimpan -> slang_utama.csv")