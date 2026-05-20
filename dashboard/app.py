import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Dashboard ChatKasir", layout="wide")
sns.set_theme(style="whitegrid")

current_dir = os.path.dirname(os.path.abspath(__file__))
path_food = os.path.join(current_dir, 'food_utama.csv')
path_slang = os.path.join(current_dir, 'slang_utama.csv')

@st.cache_data
def load_data():
    try:
        df_food = pd.read_csv(path_food)
        df_slang = pd.read_csv(path_slang)
        
        # Membuat kolom kategori mockup untuk keperluan visualisasi EDA
        if 'kategori' not in df_food.columns:
            kategori_pilihan = ['Makanan Utama', 'Minuman', 'Cemilan', 'Dessert']
            df_food['kategori'] = np.random.choice(kategori_pilihan, len(df_food))
        
        tanggal_hari_ini = datetime.now()
        dates = [tanggal_hari_ini - timedelta(days=i) for i in range(30)]
        
        # Perbaikan utama: Menggunakan 'name' sesuai isi kolom asli CSV
        nama_produk = df_food['name'].head(10).tolist()
        
        df_sintetis = pd.DataFrame({
            'tanggal': pd.to_datetime(np.random.choice(dates, 200)),
            'produk': np.random.choice(nama_produk, 200),
            'kuantitas': np.random.randint(1, 5, 200),
            'harga_satuan': np.random.choice([15000, 20000, 25000, 50000], 200)
        })
        df_sintetis['harga_total'] = df_sintetis['kuantitas'] * df_sintetis['harga_satuan']
        return df_food, df_slang, df_sintetis
    except Exception as e:
        st.error(f"Gagal memuat data internal: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_food, df_slang, df_sintetis = load_data()

st.sidebar.title("Navigasi ChatKasir")
pilihan_halaman = st.sidebar.radio("Halaman", ["Ringkasan EDA", "Visualisasi Bisnis", "Simulasi Ekstraksi AI"])

if pilihan_halaman == "Ringkasan EDA":
    st.title("Ringkasan Eksplorasi Data (EDA)")
    
    if df_food.empty:
        st.warning("Data makanan tidak ditemukan atau gagal diproses.")
    else:
        st.write(f"### Statistik Cepat")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Total Katalog Makanan: {len(df_food)} Item")
        with col2:
            st.info(f"Total Kosakata Slang: {len(df_slang)} Kata")
        
        st.markdown("---")
        
        with st.expander("Lihat Sampel Data Makanan"):
            st.dataframe(df_food.head())

        st.subheader("Distribusi Kategori Makanan")
        fig_cat, ax_cat = plt.subplots(figsize=(10, 5))
        sns.countplot(y='kategori', data=df_food, 
                      order=df_food['kategori'].value_counts().index, 
                      palette='viridis', ax=ax_cat)
        st.pyplot(fig_cat)

elif pilihan_halaman == "Visualisasi Bisnis":
    st.title("Dasbor Analitik Bisnis")
    
    if df_sintetis.empty:
        st.write("Data transaksi tidak tersedia.")
    else:
        st.write("### Tren Pendapatan Harian")
        tren_harian = df_sintetis.groupby('tanggal')['harga_total'].sum().reset_index()
        fig_trend, ax_trend = plt.subplots(figsize=(12, 4))
        sns.lineplot(x='tanggal', y='harga_total', data=tren_harian, marker='o', color='teal', ax=ax_trend)
        plt.xticks(rotation=45)
        st.pyplot(fig_trend)
        
        st.write("### Produk Terlaris")
        terlaris = df_sintetis.groupby('produk')['kuantitas'].sum().reset_index().sort_values('kuantitas', ascending=False)
        fig_best, ax_best = plt.subplots(figsize=(10, 5))
        sns.barplot(x='kuantitas', y='produk', data=terlaris, palette='magma', ax=ax_best)
        st.pyplot(fig_best)

elif pilihan_halaman == "Simulasi Ekstraksi AI":
    st.title("Uji Coba Model Ekstraksi (Mockup)")
    teks_input = st.text_area("Teks Obrolan Pelanggan:", "bang pesen seblak 2 porsi")
    if st.button("Proses Pesanan"):
        st.json({"status": "success", "produk": "seblak", "qty": 2})
