import pandas as pd

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Analisis hasil generate dataset sintetis v3
# ============================================================

food_list = pd.read_csv('../final/food_utama.csv')['name'].dropna().str.lower().str.strip().tolist()

filename = 'chatkasir_synthetic.csv'
hasil_analisis = []

try:
    df = pd.read_csv(filename)

    # ============================================================
    # HITUNG PRODUK UNIK EFEKTIF
    # Pola 4 (majemuk) menyimpan "produk1 & produk2" di kolom product
    # Perlu di-flatten agar tidak dihitung sebagai entitas baru
    # ============================================================
    df_single  = df[df['pattern'] != 4]
    df_majemuk = df[df['pattern'] == 4]

    produk_majemuk_flat = set()
    for val in df_majemuk['product']:
        for p in val.split(' & '):
            produk_majemuk_flat.add(p.strip())

    produk_unik_efektif = len(set(df_single['product'].unique()) | produk_majemuk_flat)

    # Top 100 produk (hanya dari baris single / pola 1-3)
    top100 = df_single['product'].value_counts().head(100).reset_index()
    top100.columns = ['product', 'jumlah_muncul']

    analisis = {
        'dataset'                  : filename,
        'total_baris'              : len(df),
        'pattern_1'                : (df['pattern'] == 1).sum(),
        'pattern_2'                : (df['pattern'] == 2).sum(),
        'pattern_3'                : (df['pattern'] == 3).sum(),
        'pattern_4_majemuk'        : (df['pattern'] == 4).sum(),
        'baris_tanpa_harga'        : (df['price_satuan'] == -1).sum(),
        'produk_unik_efektif'      : produk_unik_efektif,
        'total_produk_food_list'   : len(food_list),
        'produk_belum_ter_generate': len(food_list) - produk_unik_efektif,
    }
    hasil_analisis.append(analisis)

    # Simpan top 100 produk (single)
    top100.to_csv('analisis_top100_chatkasir_v3.csv', index=False)
    print(f"Tersimpan -> analisis_top100_chatkasir_v3.csv")

except FileNotFoundError:
    print(f"File {filename} belum ada, pastikan sudah di-generate.")

# Simpan ringkasan
df_hasil = pd.DataFrame(hasil_analisis)
df_hasil.to_csv('analisis_ringkasan.csv', index=False)
print(f"\nTersimpan -> analisis_ringkasan.csv")
print(f"\nPreview ringkasan:")
print(df_hasil.to_string(index=False))
