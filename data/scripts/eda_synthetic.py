import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # untuk menyimpan tanpa tampilan GUI
import os

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: EDA awal dataset sintetis weighted
# ============================================================

# Buat folder output untuk simpan grafik
os.makedirs('../eda_output', exist_ok=True)

TARGET = 10000  # ganti ke 50000 atau 100000 sesuai kebutuhan
filename = f'../script-based/synthetic_orders_weighted_{TARGET}.csv'
df = pd.read_csv(filename)

print(f"Dataset: synthetic_orders_weighted_{TARGET}.csv")
print(f"Total baris: {len(df)}")

# ============================================================
# 1. DISTRIBUSI PATTERN
# ============================================================
print("\n--- DISTRIBUSI PATTERN ---")
print(df['pattern'].value_counts())

plt.figure(figsize=(7, 4))
df['pattern'].value_counts().sort_index().plot(
    kind='bar', color=['#2E75B6', '#70AD47', '#ED7D31'], edgecolor='white'
)
plt.title(f'Distribusi Pattern — {TARGET} baris', fontsize=13)
plt.xlabel('Pattern')
plt.ylabel('Jumlah Baris')
plt.xticks([0, 1, 2], ['Pola 1\n(Normal)', 'Pola 2\n(Multi Produk)', 'Pola 3\n(Slang/Typo)'], rotation=0)
plt.tight_layout()
plt.savefig(f'../eda_output/distribusi_pattern_{TARGET}.png', dpi=150)
plt.close()
print(f"Tersimpan -> eda_output/distribusi_pattern_{TARGET}.png")

# ============================================================
# 2. DISTRIBUSI HARGA
# ============================================================
print("\n--- DISTRIBUSI HARGA ---")
df_harga = df[df['price_satuan'] > 0]['price_satuan']
print(f"Rata-rata harga : Rp {df_harga.mean():,.0f}")
print(f"Median harga    : Rp {df_harga.median():,.0f}")
print(f"Harga terendah  : Rp {df_harga.min():,.0f}")
print(f"Harga tertinggi : Rp {df_harga.max():,.0f}")

plt.figure(figsize=(9, 4))
df_harga.hist(bins=30, color='#2E75B6', edgecolor='white')
plt.title(f'Distribusi Harga Satuan — {TARGET} baris', fontsize=13)
plt.xlabel('Harga (Rupiah)')
plt.ylabel('Jumlah Baris')
plt.tight_layout()
plt.savefig(f'../eda_output/distribusi_harga_{TARGET}.png', dpi=150)
plt.close()
print(f"Tersimpan -> eda_output/distribusi_harga_{TARGET}.png")

# ============================================================
# 3. DISTRIBUSI JUMLAH PESANAN
# ============================================================
print("\n--- DISTRIBUSI JUMLAH PESANAN ---")
print(df['quantity'].value_counts().sort_index())

plt.figure(figsize=(9, 4))
df['quantity'].value_counts().sort_index().plot(
    kind='bar', color='#70AD47', edgecolor='white'
)
plt.title(f'Distribusi Jumlah Pesanan — {TARGET} baris', fontsize=13)
plt.xlabel('Jumlah Pesanan')
plt.ylabel('Jumlah Baris')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(f'../eda_output/distribusi_qty_{TARGET}.png', dpi=150)
plt.close()
print(f"Tersimpan -> eda_output/distribusi_qty_{TARGET}.png")

# ============================================================
# 4. TOP 20 PRODUK TERBANYAK
# ============================================================
print("\n--- TOP 20 PRODUK ---")
top20 = df['product'].value_counts().head(20)
print(top20)

plt.figure(figsize=(10, 6))
top20.sort_values().plot(
    kind='barh', color='#ED7D31', edgecolor='white'
)
plt.title(f'Top 20 Produk Terbanyak — {TARGET} baris', fontsize=13)
plt.xlabel('Jumlah Muncul')
plt.tight_layout()
plt.savefig(f'../eda_output/top20_produk_{TARGET}.png', dpi=150)
plt.close()
print(f"Tersimpan -> eda_output/top20_produk_{TARGET}.png")

# ============================================================
# 5. PROPORSI BARIS TANPA HARGA
# ============================================================
print("\n--- PROPORSI HARGA ---")
ada_harga    = (df['price_satuan'] > 0).sum()
tanpa_harga  = (df['price_satuan'] == -1).sum()
print(f"Ada harga    : {ada_harga} ({ada_harga/len(df)*100:.1f}%)")
print(f"Tanpa harga  : {tanpa_harga} ({tanpa_harga/len(df)*100:.1f}%)")

plt.figure(figsize=(5, 5))
plt.pie(
    [ada_harga, tanpa_harga],
    labels=[f'Ada harga\n({ada_harga/len(df)*100:.1f}%)',
            f'Tanpa harga\n({tanpa_harga/len(df)*100:.1f}%)'],
    colors=['#2E75B6', '#ED7D31'],
    startangle=90,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
)
plt.title(f'Proporsi Harga — {TARGET} baris', fontsize=13)
plt.tight_layout()
plt.savefig(f'../eda_output/proporsi_harga_{TARGET}.png', dpi=150)
plt.close()
print(f"Tersimpan -> eda_output/proporsi_harga_{TARGET}.png")

# ============================================================
# SIMPAN RINGKASAN EDA KE CSV
# ============================================================
ringkasan = pd.DataFrame([{
    'dataset'           : f'synthetic_orders_weighted_{TARGET}.csv',
    'total_baris'       : len(df),
    'rata_rata_harga'   : round(df_harga.mean(), 0),
    'median_harga'      : round(df_harga.median(), 0),
    'harga_min'         : df_harga.min(),
    'harga_max'         : df_harga.max(),
    'qty_min'           : df['quantity'].min(),
    'qty_max'           : df['quantity'].max(),
    'rata_rata_qty'     : round(df['quantity'].mean(), 2),
    'baris_ada_harga'   : ada_harga,
    'baris_tanpa_harga' : tanpa_harga,
    'persen_tanpa_harga': round(tanpa_harga / len(df) * 100, 1),
    'produk_unik'       : df['product'].nunique(),
}])

ringkasan.to_csv(f'../eda_output/eda_ringkasan_{TARGET}.csv', index=False)
print(f"\nTersimpan -> eda_output/eda_ringkasan_{TARGET}.csv")
print("\nEDA selesai! Semua grafik tersimpan di folder eda_output/")