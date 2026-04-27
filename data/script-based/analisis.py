import pandas as pd

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Analisis hasil generate dataset sintetis
# ============================================================

food_list = pd.read_csv('../final/food_utama.csv')['name'].dropna().str.lower().str.strip().tolist()

hasil_analisis = []

for target_rows in [10000, 50000, 100000]:
    filename = f'synthetic_orders_weighted_{target_rows}.csv'
    try:
        df = pd.read_csv(filename)

        top100 = df['product'].value_counts().head(100).reset_index()
        top100.columns = ['product', 'jumlah_muncul']

        analisis = {
            'dataset'                  : filename,
            'total_baris'              : len(df),
            'pattern_1'                : (df['pattern'] == 1).sum(),
            'pattern_2'                : (df['pattern'] == 2).sum(),
            'pattern_3'                : (df['pattern'] == 3).sum(),
            'baris_tanpa_harga'        : (df['price_satuan'] == -1).sum(),
            'produk_unik_ter_generate' : df['product'].nunique(),
            'total_produk_food_list'   : len(food_list),
            'produk_belum_ter_generate': len(food_list) - df['product'].nunique(),
        }
        hasil_analisis.append(analisis)

        # Simpan top 100 per dataset
        top100.to_csv(f'analisis_top100_{target_rows}.csv', index=False)
        print(f"Tersimpan -> analisis_top100_{target_rows}.csv")

    except FileNotFoundError:
        print(f"File {filename} belum ada, skip.")

# Simpan ringkasan semua dataset
df_hasil = pd.DataFrame(hasil_analisis)
df_hasil.to_csv('analisis_ringkasan.csv', index=False)
print(f"\nTersimpan -> analisis_ringkasan.csv")
print(f"\nPreview ringkasan:")
print(df_hasil.to_string(index=False))