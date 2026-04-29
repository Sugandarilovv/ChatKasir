import pandas as pd
import re

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Assessing dataset sintetis weighted
#            Validasi variasi format harga & jumlah
#            OUTPUT: 3 CSV gabungan (semua dataset digabung)
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

pola_gabungan = r'\d+rb|\d+k\b|\d+ ribu|\d+\.\d{3}|rp\d+rb|rp \d+\.\d{3}'

# Akumulator untuk 3 CSV gabungan
all_harga    = []
all_jumlah   = []
all_ringkasan = []

for target_rows in [10000, 50000, 100000]:
    filename = f'../script-based/synthetic_orders_weighted_{target_rows}.csv'
    try:
        df = pd.read_csv(filename)

        print(f"\n{'='*60}")
        print(f"ASSESSING: synthetic_orders_weighted_{target_rows}.csv")
        print(f"{'='*60}")

        # ============================================================
        # INFO DASAR
        # ============================================================
        print(f"\nTotal baris     : {len(df)}")
        print(f"Kolom           : {df.columns.tolist()}")
        print(f"Nilai kosong    :\n{df.isnull().sum()}")

        # ============================================================
        # VALIDASI FORMAT HARGA DI input_text
        # ============================================================
        print(f"\n--- VALIDASI FORMAT HARGA ---")
        for nama, pola in pola_harga.items():
            jumlah = df['input_text'].str.contains(pola, regex=True).sum()
            persen = jumlah / len(df) * 100
            print(f"  {nama:40s}: {jumlah:6} baris ({persen:.1f}%)")
            all_harga.append({
                'dataset'      : f'synthetic_orders_weighted_{target_rows}.csv',
                'target_rows'  : target_rows,
                'format_harga' : nama,
                'jumlah_baris' : int(jumlah),
                'persentase'   : round(persen, 1)
            })

        tidak_ada_harga = ~df['input_text'].str.contains(pola_gabungan, regex=True)
        print(f"\n  Baris tanpa format harga apapun: {tidak_ada_harga.sum()}")
        print(f"  Baris dengan price_satuan = -1 : {(df['price_satuan'] == -1).sum()}")
        print(f"  (Selisih seharusnya 0 atau kecil)")

        # ============================================================
        # VALIDASI FORMAT JUMLAH DI input_text
        # ============================================================
        print(f"\n--- VALIDASI FORMAT JUMLAH ---")
        for nama, pola in pola_jumlah.items():
            jumlah = df['input_text'].str.contains(pola, regex=True).sum()
            persen = jumlah / len(df) * 100
            print(f"  {nama:45s}: {jumlah:6} baris ({persen:.1f}%)")
            all_jumlah.append({
                'dataset'       : f'synthetic_orders_weighted_{target_rows}.csv',
                'target_rows'   : target_rows,
                'format_jumlah' : nama,
                'jumlah_baris'  : int(jumlah),
                'persentase'    : round(persen, 1)
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
        # AKUMULASI RINGKASAN
        # ============================================================
        all_ringkasan.append({
            'dataset'               : f'synthetic_orders_weighted_{target_rows}.csv',
            'target_rows'           : target_rows,
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
        })

    except FileNotFoundError:
        print(f"\nFile {filename} belum ada, skip.")

# ============================================================
# SIMPAN 3 CSV GABUNGAN
# ============================================================
if all_harga:
    pd.DataFrame(all_harga).to_csv('../script-based/assessing_harga_gabungan.csv', index=False)
    print("\nTersimpan -> assessing_harga_gabungan.csv")

if all_jumlah:
    pd.DataFrame(all_jumlah).to_csv('../script-based/assessing_jumlah_gabungan.csv', index=False)
    print("Tersimpan -> assessing_jumlah_gabungan.csv")

if all_ringkasan:
    pd.DataFrame(all_ringkasan).to_csv('../script-based/assessing_ringkasan_gabungan.csv', index=False)
    print("Tersimpan -> assessing_ringkasan_gabungan.csv")

print("\nSelesai! Semua hasil assessing sudah digabung.")