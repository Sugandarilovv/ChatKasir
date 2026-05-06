import pandas as pd
import re

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Assessing dataset sintetis
#            synthetic_orders_1000food_100000.csv
#            Validasi variasi format harga & jumlah
#            OUTPUT: 1 CSV gabungan (harga, jumlah, ringkasan)
# ============================================================

pola_harga = {
    'rb (contoh: 15rb)'            : r'\d+rb',
    'k (contoh: 15k)'              : r'\d+k\b',
    'ribu (contoh: 15 ribu)'       : r'\d+ ribu',
    '.000 (contoh: 15.000)'        : r'\d+\.\d{3}',
    'rp...rb (contoh: rp15rb)'     : r'rp\d+rb',
    'rp ...000 (contoh: rp 15.000)': r'rp \d+\.\d{3}',
}

pola_jumlah = {
    'angka saja (contoh: 3)'         : r'\b[1-9]\b',
    'angka + porsi (contoh: 3 porsi)': r'\d+ porsi',
    'angka + pcs (contoh: 3 pcs)'    : r'\d+ pcs',
    'angka + buah (contoh: 3 buah)'  : r'\d+ buah',
    'angka + bungkus'                : r'\d+ bungkus',
}

pola_gabungan = (
    r'\d+rb'        # 15rb
    r'|\d+k\b'      # 15k
    r'|\d+ ribu'    # 15 ribu
    r'|\d+ rbu'     # 24 rbu
    r'|\d+ rb\b'    # 3 rb
    r'|\d+ rbuan'   # 30 rbuan
    r'|\d+ rebu'    # 10 rebu
    r'|\d+\.\d{3}'  # 15.000
    r'|rp\d+rb'     # rp15rb
    r'|rp \d+\.\d{3}' # rp 15.000
)

FILENAME     = '../script-based/synthetic_orders_1000food_100000.csv'
DATASET_NAME = 'synthetic_orders_1000food_100000.csv'
OUTPUT_CSV   = '../script-based/assessing_1000food_100000.csv'

rows = []  # satu akumulator untuk semua section

try:
    df = pd.read_csv(FILENAME)

    print(f"\n{'='*60}")
    print(f"ASSESSING: {DATASET_NAME}")
    print(f"{'='*60}")

    # ============================================================
    # INFO DASAR
    # ============================================================
    print(f"\nTotal baris     : {len(df)}")
    print(f"Kolom           : {df.columns.tolist()}")
    print(f"Nilai kosong    :\n{df.isnull().sum()}")

    # ============================================================
    # VALIDASI FORMAT HARGA
    # ============================================================
    print(f"\n--- VALIDASI FORMAT HARGA ---")
    for nama, pola in pola_harga.items():
        jumlah = df['input_text'].str.contains(pola, regex=True).sum()
        persen = jumlah / len(df) * 100
        print(f"  {nama:40s}: {jumlah:6} baris ({persen:.1f}%)")
        rows.append({
            'section'  : 'harga',
            'dataset'  : DATASET_NAME,
            'label'    : nama,
            'jumlah'   : int(jumlah),
            'persen'   : round(persen, 1),
            'keterangan': ''
        })

    tidak_ada_harga = ~df['input_text'].str.contains(pola_gabungan, regex=True)
    print(f"\n  Baris tanpa format harga apapun: {tidak_ada_harga.sum()}")
    print(f"  Baris dengan price_satuan = -1 : {(df['price_satuan'] == -1).sum()}")

    # ============================================================
    # VALIDASI FORMAT JUMLAH
    # ============================================================
    print(f"\n--- VALIDASI FORMAT JUMLAH ---")
    for nama, pola in pola_jumlah.items():
        jumlah = df['input_text'].str.contains(pola, regex=True).sum()
        persen = jumlah / len(df) * 100
        print(f"  {nama:45s}: {jumlah:6} baris ({persen:.1f}%)")
        rows.append({
            'section'   : 'jumlah',
            'dataset'   : DATASET_NAME,
            'label'     : nama,
            'jumlah'    : int(jumlah),
            'persen'    : round(persen, 1),
            'keterangan': ''
        })

    # ============================================================
    # VALIDASI KOLOM quantity
    # ============================================================
    print(f"\n--- VALIDASI KOLOM quantity ---")
    print(f"  Tipe data         : {df['quantity'].dtype}")
    print(f"  Nilai min         : {df['quantity'].min()}")
    print(f"  Nilai max         : {df['quantity'].max()}")
    print(f"  Distribusi qty    :\n{df['quantity'].value_counts().sort_index().head(10)}")

    # ============================================================
    # VALIDASI KOLOM price_satuan
    # ============================================================
    print(f"\n--- VALIDASI KOLOM price_satuan ---")
    print(f"  Tipe data              : {df['price_satuan'].dtype}")
    print(f"  Baris price = -1       : {(df['price_satuan'] == -1).sum()}")
    print(f"  Baris price > 0        : {(df['price_satuan'] > 0).sum()}")
    print(f"  Baris price = 0        : {(df['price_satuan'] == 0).sum()}")
    print(f"  Nilai min (selain -1)  : {df[df['price_satuan'] > 0]['price_satuan'].min()}")
    print(f"  Nilai max              : {df['price_satuan'].max()}")

    # ============================================================
    # VALIDASI [SEP]
    # ============================================================
    print(f"\n--- VALIDASI [SEP] ---")
    ada_sep   = df['input_text'].str.contains(r'\[SEP\]', regex=True).sum()
    tidak_sep = (~df['input_text'].str.contains(r'\[SEP\]', regex=True)).sum()
    print(f"  Ada [SEP]    : {ada_sep} baris ({ada_sep/len(df)*100:.1f}%)")
    print(f"  Tanpa [SEP]  : {tidak_sep} baris ({tidak_sep/len(df)*100:.1f}%)")

    # ============================================================
    # PREVIEW SAMPLE
    # ============================================================
    print(f"\n--- PREVIEW 5 BARIS ACAK ---")
    print(df.sample(5, random_state=42)[['input_text', 'product', 'quantity', 'price_satuan', 'pattern']].to_string(index=False))

    # ============================================================
    # RINGKASAN
    # ============================================================
    ringkasan = {
        'total_baris'           : len(df),
        'price_minus1'          : int((df['price_satuan'] == -1).sum()),
        'price_valid'           : int((df['price_satuan'] > 0).sum()),
        'price_min'             : df[df['price_satuan'] > 0]['price_satuan'].min(),
        'price_max'             : df['price_satuan'].max(),
        'qty_min'               : int(df['quantity'].min()),
        'qty_max'               : int(df['quantity'].max()),
        'ada_sep'               : int(ada_sep),
        'tanpa_sep'             : int(tidak_sep),
        'baris_tanpa_harga_teks': int(tidak_ada_harga.sum()),
    }
    for label, nilai in ringkasan.items():
        rows.append({
            'section'   : 'ringkasan',
            'dataset'   : DATASET_NAME,
            'label'     : label,
            'jumlah'    : nilai,
            'persen'    : '',
            'keterangan': ''
        })

except FileNotFoundError:
    print(f"\nFile {FILENAME} tidak ditemukan, pastikan path sudah benar.")

# ============================================================
# SIMPAN 1 CSV GABUNGAN
# ============================================================
if rows:
    pd.DataFrame(rows).to_csv(OUTPUT_CSV, index=False)
    print(f"\nTersimpan -> {OUTPUT_CSV}")

print("\nSelesai!")