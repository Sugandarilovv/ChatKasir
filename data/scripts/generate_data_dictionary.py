import pandas as pd
import csv
import os

os.makedirs('../data-dictionary', exist_ok=True)
print('✅ Folder ../data-dictionary siap')

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Generate Data Dictionary dari 3 dataset final
#            OUTPUT: 3 file CSV data dictionary
# ============================================================

df_food  = pd.read_csv('../final/food_utama.csv')
df_slang = pd.read_csv('../final/slang_utama.csv')
df_sint  = pd.read_csv('../final/synthetic_orders_1000food_100000.csv')

# ============================================================
# HELPER FUNCTION
# ============================================================

def get_dtype_label(dtype):
    if dtype == 'object':
        return 'string'
    elif dtype == 'int64':
        return 'integer'
    elif dtype == 'float64':
        return 'float'
    else:
        return str(dtype)

def get_sample_values(series, n=3):
    samples = series.dropna().unique()[:n]
    return ' | '.join([str(s) for s in samples])

def get_null_count(series):
    return series.isnull().sum()

def get_unique_count(series):
    return series.nunique()

# ============================================================
# DATA DICTIONARY 1 — food_utama.csv
# ============================================================

food_meta = {
    'name': {
        'deskripsi' : 'Nama makanan atau minuman dalam bahasa Indonesia huruf kecil semua',
        'catatan'   : 'Gabungan dari eriko-syah/indonesian-food (HuggingFace) dan ariqsyahalam/indonesia-food-delivery-gofood-product-list (Kaggle). Panjang nama 1-5 kata.',
    }
}

rows_food = []
for col in df_food.columns:
    rows_food.append({
        'nama_kolom'    : col,
        'tipe_data'     : get_dtype_label(str(df_food[col].dtype)),
        'jumlah_baris'  : len(df_food),
        'nilai_kosong'  : get_null_count(df_food[col]),
        'nilai_unik'    : get_unique_count(df_food[col]),
        'contoh_nilai'  : get_sample_values(df_food[col]),
        'deskripsi'     : food_meta[col]['deskripsi'],
        'catatan'       : food_meta[col]['catatan'],
    })

df_dd_food = pd.DataFrame(rows_food)
df_dd_food.to_csv('../data-dictionary/data_dictionary_food.csv', index=False, quoting=csv.QUOTE_ALL)
print(f'✅ Tersimpan -> data_dictionary_food.csv ({len(df_dd_food)} kolom)')
print(df_dd_food.to_string(index=False))

# ============================================================
# DATA DICTIONARY 2 — slang_utama.csv
# ============================================================

slang_meta = {
    'slang': {
        'deskripsi' : 'Kata slang atau singkatan yang umum digunakan dalam chat WhatsApp',
        'catatan'   : 'Gabungan dari nahiar/indonesia-slang dan theonlydo/indonesia-slang (HuggingFace). Semua huruf kecil. Panjang 1-20 karakter.',
    },
    'formal': {
        'deskripsi' : 'Bentuk baku atau formal dari kata slang yang bersesuaian',
        'catatan'   : 'Digunakan oleh AI-2 (Denny) sebagai kamus normalisasi teks sebelum diproses model. Semua huruf kecil.',
    }
}

rows_slang = []
for col in df_slang.columns:
    rows_slang.append({
        'nama_kolom'    : col,
        'tipe_data'     : get_dtype_label(str(df_slang[col].dtype)),
        'jumlah_baris'  : len(df_slang),
        'nilai_kosong'  : get_null_count(df_slang[col]),
        'nilai_unik'    : get_unique_count(df_slang[col]),
        'contoh_nilai'  : get_sample_values(df_slang[col]),
        'deskripsi'     : slang_meta[col]['deskripsi'],
        'catatan'       : slang_meta[col]['catatan'],
    })

df_dd_slang = pd.DataFrame(rows_slang)
df_dd_slang.to_csv('../data-dictionary/data_dictionary_slang.csv', index=False, quoting=csv.QUOTE_ALL)
print(f'\n✅ Tersimpan -> data_dictionary_slang.csv ({len(df_dd_slang)} kolom)')
print(df_dd_slang.to_string(index=False))

# ============================================================
# DATA DICTIONARY 3 — synthetic_orders_1000food_100000.csv
# ============================================================

sint_meta = {
    'input_text': {
        'deskripsi' : 'Teks percakapan pesanan antara pembeli dan penjual dipisahkan token [SEP]',
        'catatan'   : 'Format: <teks_pembeli> [SEP] <teks_penjual>. Baris tanpa [SEP] adalah pattern 1 tanpa konfirmasi penjual (2.491 baris / 2.5%).',
    },
    'product': {
        'deskripsi' : 'Nama produk makanan yang dipesan dalam bentuk baku huruf kecil',
        'catatan'   : 'Target ekstraksi entitas oleh model NLP. Diambil dari food_utama.csv. 1.000 produk unik di dataset ini.',
    },
    'quantity': {
        'deskripsi' : 'Jumlah produk yang dipesan dalam satuan angka bulat',
        'catatan'   : f'Nilai berkisar {df_sint["quantity"].min()}-{df_sint["quantity"].max()}. Distribusi merata (~10% per nilai). Target ekstraksi entitas oleh model NLP.',
    },
    'price_satuan': {
        'deskripsi' : 'Harga satuan produk dalam rupiah. Nilai -1 berarti harga tidak disebutkan secara eksplisit dalam teks',
        'catatan'   : f'Nilai -1 disengaja untuk melatih model menangani kasus tanpa harga ({(df_sint["price_satuan"]==-1).sum():,} baris / {(df_sint["price_satuan"]==-1).sum()/len(df_sint)*100:.1f}%). Harga valid berkisar Rp {df_sint[df_sint["price_satuan"]>0]["price_satuan"].min():,}-Rp {df_sint["price_satuan"].max():,}.',
    },
    'pattern': {
        'deskripsi' : 'Pola kalimat yang digunakan saat generate data sintetis',
        'catatan'   : 'Pattern 1: satu produk tanpa/dengan konfirmasi penjual. Pattern 2: multi produk menghasilkan beberapa baris per percakapan. Pattern 3: input mengandung slang dan typo berat namun label tetap baku.',
    },
}

rows_sint = []
for col in df_sint.columns:
    rows_sint.append({
        'nama_kolom'    : col,
        'tipe_data'     : get_dtype_label(str(df_sint[col].dtype)),
        'jumlah_baris'  : len(df_sint),
        'nilai_kosong'  : get_null_count(df_sint[col]),
        'nilai_unik'    : get_unique_count(df_sint[col]),
        'contoh_nilai'  : get_sample_values(df_sint[col]),
        'deskripsi'     : sint_meta[col]['deskripsi'],
        'catatan'       : sint_meta[col]['catatan'],
    })

df_dd_sint = pd.DataFrame(rows_sint)
df_dd_sint.to_csv('../data-dictionary/data_dictionary_synthetic.csv', index=False, quoting=csv.QUOTE_ALL)
print(f'\n✅ Tersimpan -> data_dictionary_synthetic.csv ({len(df_dd_sint)} kolom)')
print(df_dd_sint.to_string(index=False))

print('\n✅ Selesai! Semua Data Dictionary tersimpan di folder ../data-dictionary/')
