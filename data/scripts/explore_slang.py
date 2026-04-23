import pandas as pd

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Eksplorasi, filter, merge, dan cleaning dataset slang
# ============================================================

print("=" * 50)
print("1. LOAD DATASET")
print("=" * 50)

df_nahiar    = pd.read_csv('../raw/slang_nahiar_raw.csv')
df_theonlydo = pd.read_csv('../raw/slang_theonlydo_raw.csv')

print(f"nahiar    : {len(df_nahiar)} baris | kolom: {df_nahiar.columns.tolist()}")
print(f"theonlydo : {len(df_theonlydo)} baris | kolom: {df_theonlydo.columns.tolist()}")

# ============================================================
print("\n" + "=" * 50)
print("2. FILTER KOLOM")
print("=" * 50)

df_nahiar_clean    = df_nahiar[['slang', 'formal']].copy()
df_theonlydo_clean = df_theonlydo[['slang', 'formal']].copy()

print(f"nahiar    : {len(df_nahiar_clean)} baris")
print(f"theonlydo : {len(df_theonlydo_clean)} baris")

# ============================================================
print("\n" + "=" * 50)
print("3. MERGE")
print("=" * 50)

df_merged = pd.concat([df_nahiar_clean, df_theonlydo_clean], ignore_index=True)
print(f"Setelah merge   : {len(df_merged)} baris")

df_merged['slang']  = df_merged['slang'].str.lower().str.strip()
df_merged['formal'] = df_merged['formal'].str.lower().str.strip()
df_merged = df_merged.dropna(subset=['slang', 'formal'])

before = len(df_merged)
df_merged = df_merged.drop_duplicates(subset=['slang']).reset_index(drop=True)
print(f"Setelah dedup   : {len(df_merged)} baris (dibuang: {before - len(df_merged)})")
print(f"\nPreview:\n{df_merged.head(10)}")

# ============================================================
print("\n" + "=" * 50)
print("3.5 TAMBAH SLANG KONTEKS PEMESANAN")
print("=" * 50)

slang_pemesanan = [
    # Kata pesan/order
    ('pesen', 'pesan'), ('pesen dong', 'pesan dong'), ('mesen', 'memesan'),
    ('order', 'pesan'), ('ord', 'pesan'), ('book', 'pesan'),
    ('beli', 'beli'), ('mau', 'ingin memesan'), ('pengen', 'ingin'),
    ('pingin', 'ingin'), ('request', 'pesan'),

    # Satuan jumlah
    ('pcs', 'buah'), ('porsi', 'porsi'), ('biji', 'buah'), ('buah', 'buah'),
    ('gelas', 'gelas'), ('mangkok', 'mangkuk'), ('mgkok', 'mangkuk'),
    ('cangkir', 'cangkir'), ('botol', 'botol'), ('loyang', 'loyang'),
    ('kotak', 'kotak'), ('bks', 'bungkus'), ('bungkus', 'bungkus'),
    ('bgks', 'bungkus'), ('pack', 'bungkus'),

    # Satuan harga
    ('rb', 'ribu'), ('ribu', 'ribu'), ('k', 'ribu'), ('jt', 'juta'),
    ('juta', 'juta'), ('rebu', 'ribu'), ('rbu', 'ribu'),
    ('rupiah', 'rupiah'), ('rp', 'rupiah'), ('perak', 'rupiah'),

    # Konfirmasi & respons
    ('oke', 'oke'), ('ok', 'oke'), ('sip', 'oke'), ('siap', 'siap'),
    ('iya', 'iya'), ('yep', 'iya'), ('yups', 'iya'), ('yoi', 'iya'),
    ('nggak', 'tidak'), ('ngga', 'tidak'), ('gak', 'tidak'),
    ('ga', 'tidak'), ('nope', 'tidak'),

    # Sapaan transaksi
    ('kak', 'kakak'), ('ka', 'kakak'), ('min', 'admin'),
    ('bang', 'abang'), ('bg', 'abang'), ('mas', 'mas'),
    ('mbak', 'mbak'), ('bu', 'ibu'), ('pak', 'bapak'),

    # Kata tanya transaksi
    ('brp', 'berapa'), ('berapa', 'berapa'), ('brapa', 'berapa'),
    ('harga', 'harga'), ('hrg', 'harga'), ('total', 'total'),
    ('ttl', 'total'), ('bayar', 'bayar'), ('dp', 'uang muka'),
    ('lunas', 'lunas'),

    # Kata tambahan pesanan
    ('tanpa', 'tanpa'), ('pake', 'pakai'), ('pk', 'pakai'),
    ('gak pake', 'tidak pakai'), ('no', 'tidak'), ('plus', 'tambah'),
    ('sama', 'dan'), ('ama', 'dan'), ('n', 'dan'), ('tambah', 'tambah'),
    ('tambahin', 'tambahkan'), ('kurang', 'kurang'), ('pedas', 'pedas'),
    ('pedes', 'pedas'), ('manis', 'manis'), ('asin', 'asin'),
    ('gurih', 'gurih'),

    # Pengiriman & lokasi
    ('diantar', 'diantar'), ('antar', 'antar'), ('cod', 'bayar di tempat'),
    ('gosend', 'gosend'), ('ojol', 'ojek online'), ('grab', 'grab'),
    ('gojek', 'gojek'), ('pickup', 'ambil sendiri'), ('ambil', 'ambil sendiri'),
]

df_pemesanan = pd.DataFrame(slang_pemesanan, columns=['slang', 'formal'])
print(f"Slang pemesanan ditambahkan: {len(df_pemesanan)} entri")

df_merged = pd.concat([df_merged, df_pemesanan], ignore_index=True)
df_merged['slang']  = df_merged['slang'].str.lower().str.strip()
df_merged['formal'] = df_merged['formal'].str.lower().str.strip()
df_merged = df_merged.drop_duplicates(subset=['slang']).reset_index(drop=True)
print(f"Total setelah tambah slang pemesanan: {len(df_merged)} baris")

# ============================================================
print("\n" + "=" * 50)
print("4. CLEANING LANJUTAN")
print("=" * 50)

# Hapus slang yang mengandung angka
before = len(df_merged)
df_merged = df_merged[~df_merged['slang'].str.contains(r'[0-9]', regex=True)]
print(f"Setelah hapus angka           : {len(df_merged)} baris (dibuang: {before - len(df_merged)})")

# Hapus slang yang terlalu panjang (> 20 karakter)
before = len(df_merged)
df_merged = df_merged[df_merged['slang'].str.len() <= 20]
print(f"Setelah hapus slang panjang   : {len(df_merged)} baris (dibuang: {before - len(df_merged)})")

# Hapus formal yang terlalu panjang (> 3 kata)
before = len(df_merged)
df_merged = df_merged[df_merged['formal'].str.split().str.len() <= 3]
print(f"Setelah hapus formal panjang  : {len(df_merged)} baris (dibuang: {before - len(df_merged)})")

# Hapus karakter spesial di kolom slang
before = len(df_merged)
df_merged = df_merged.copy()
df_merged['slang'] = df_merged['slang'].str.replace(r'[^a-z\s]', '', regex=True).str.strip()
df_merged = df_merged[df_merged['slang'] != '']
df_merged = df_merged.drop_duplicates(subset=['slang']).reset_index(drop=True)
print(f"Setelah hapus karakter spesial: {len(df_merged)} baris (dibuang: {before - len(df_merged)})")

# Filter konteks relevan pemesanan makanan
kata_relevan = [
    'pesan', 'order', 'beli', 'minta', 'ambil', 'memesan', 'membeli', 'meminta', 'ingin', 'mau',
    'buah', 'porsi', 'bungkus', 'mangkuk', 'gelas', 'botol', 'kotak', 'cangkir', 'piring', 'loyang',
    'ribu', 'ratus', 'juta', 'rupiah', 'harga', 'bayar', 'total', 'uang', 'lunas', 'transfer', 'tunai', 'cash',
    'oke', 'iya', 'tidak', 'bisa', 'siap', 'setuju', 'batal', 'cancel',
    'kakak', 'abang', 'admin', 'ibu', 'bapak', 'mas', 'mbak',
    'makan', 'minum', 'makanan', 'minuman', 'lauk', 'pedas', 'manis', 'asin', 'panas', 'dingin', 'hangat',
    'antar', 'kirim', 'ambil', 'ojek', 'grab',
    'pakai', 'tambah', 'kurang', 'tanpa', 'sudah', 'habis', 'ada', 'tunggu', 'ready', 'sebentar',
]
pola_relevan = '(?:' + '|'.join(kata_relevan) + ')'
before = len(df_merged)
df_merged = df_merged[df_merged['formal'].str.contains(pola_relevan, regex=True, case=False)]
df_merged = df_merged.sort_values('slang').reset_index(drop=True)
print(f"Setelah filter konteks relevan: {len(df_merged)} baris (dibuang: {before - len(df_merged)})")

print(f"\nTotal data final : {len(df_merged)} entri slang")
print(f"\nPreview:\n{df_merged.head(20)}")

df_merged.to_csv('../final/slang_utama.csv', index=False)
print(f"\nTersimpan -> ../final/slang_utama.csv ({len(df_merged)} baris)")