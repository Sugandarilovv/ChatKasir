# ================================================================
# app.py — Dashboard Interaktif ChatKasir
# Cara menjalankan di terminal:
#   streamlit run app.py
#
# Pastikan file CSV sudah ada di folder yang SAMA dengan app.py:
#   - food_utama (1).csv
#   - slang_utama (1).csv
# ================================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import random
import re
import json
from collections import Counter
from datetime import date, timedelta

# ----------------------------------------------------------------
# KONFIGURASI HALAMAN (wajib ada di baris paling awal)
# ----------------------------------------------------------------
st.set_page_config(
    page_title="ChatKasir Dashboard",   # judul tab browser
    page_icon="🧾",                     # ikon tab browser
    layout="wide",                      # gunakan lebar penuh layar
    initial_sidebar_state="expanded",   # sidebar terbuka by default
)

# ----------------------------------------------------------------
# KONSTANTA WARNA — konsisten dengan notebook EDA
# ----------------------------------------------------------------
PRIMARY   = "#2ECC71"   # hijau merek ChatKasir
ACCENT    = "#E74C3C"   # merah untuk highlight
SECONDARY = "#3498DB"   # biru untuk info
BG        = "#F9F9F9"

# ================================================================
# BAGIAN 1: FUNGSI LOAD DATA (pakai @st.cache_data agar cepat)
# Fungsi yang di-cache hanya dijalankan SEKALI; hasil disimpan
# di memori sehingga reload halaman tidak muat data dari awal.
# ================================================================

@st.cache_data
def load_food():
    """Memuat dan membersihkan dataset makanan."""
    df = pd.read_csv("food_utama (1).csv")
    df = df.dropna(subset=["name"]).drop_duplicates(subset=["name"]).reset_index(drop=True)
    df["name"]         = df["name"].str.strip().str.lower()
    df["panjang_nama"] = df["name"].str.len()
    df["jumlah_kata"]  = df["name"].str.split().str.len()

    # Buat kolom kategori dengan keyword matching
    def cari_kategori(nama):
        kategori_keyword = {
            "Ayam"    : ["ayam"],
            "Kopi"    : ["kopi", "coffee", "latte", "espresso", "americano", "cappuccino"],
            "Minuman" : ["juice", "jus", "teh", "tea", "milk", "milkshake", "soda", "air"],
            "Nasi"    : ["nasi", "rice"],
            "Mie"     : ["mie", "ramen", "udon", "soba", "kwetiau"],
            "Kue"     : ["kue", "cake", "cookies", "donut", "pastry", "croissant"],
            "Seafood" : ["ikan", "udang", "cumi", "kepiting", "kerang", "lobster"],
            "Sapi"    : ["sapi", "beef", "steak", "daging"],
            "Sayur"   : ["sayur", "vegetable", "vege", "salad"],
        }
        for kat, keywords in kategori_keyword.items():
            for kw in keywords:
                if kw in nama:
                    return kat
        return "Lainnya"

    df["kategori"] = df["name"].apply(cari_kategori)
    return df


@st.cache_data
def load_slang():
    """Memuat dan membersihkan dataset slang."""
    df = pd.read_csv("slang_utama (1).csv")
    df = df.dropna().drop_duplicates(subset=["slang"]).reset_index(drop=True)
    df["slang"]          = df["slang"].str.strip().str.lower()
    df["formal"]         = df["formal"].str.strip().str.lower()
    df["panjang_slang"]  = df["slang"].str.len()
    df["panjang_formal"] = df["formal"].str.len()
    df["selisih"]        = df["panjang_formal"] - df["panjang_slang"]
    return df


@st.cache_data
def buat_data_sintetis(n=1000):
    """
    Membuat n baris data transaksi sintetis (Rule-Based).
    random.seed(42) memastikan data selalu sama setiap kali dibuat.
    """
    random.seed(42)
    np.random.seed(42)

    # Ambil sampel nama produk pendek dari dataset makanan
    df_food = load_food()
    produk_pool = (
        df_food[df_food["jumlah_kata"].between(1, 3)]["name"]
        .sample(100, random_state=42)
        .tolist()
    )

    pola_pesan = [
        "mau pesan {qty} {produk} harga {harga}",
        "pesen {qty} {produk} ya kak, {harga} kan?",
        "boleh minta {qty} {produk}? totalnya {harga}",
        "order {qty} {produk} donk, bayar {harga}",
        "nitip {qty} {produk} harganya {harga} ya",
        "beli {produk} {qty} biji aja, {harga} total",
        "kak mau {qty} {produk} dong harga {harga}",
        "{produk} {qty} pcs harga {harga} ya min",
        "tolong pesankan {qty} {produk}, harga {harga}",
    ]

    kata_slang = ["ya kak", "donk", "dlu", "mks", "oke bos", "sip", "gas"]

    def fmt_harga(nilai):
        pilihan = [
            f"Rp{nilai:,}".replace(",", "."),
            f"rp {nilai // 1000}rb",
            f"{nilai // 1000}k",
            f"{nilai:,}".replace(",", "."),
        ]
        return random.choice(pilihan)

    data = []
    # Buat tanggal acak dalam rentang 90 hari terakhir
    start_date = date.today() - timedelta(days=90)

    for i in range(n):
        produk       = random.choice(produk_pool)
        qty          = random.choices([1, 2, 3, 4, 5, 10], weights=[40, 25, 15, 10, 7, 3])[0]
        harga_satuan = random.randrange(5000, 150001, 500)
        total_harga  = harga_satuan * qty
        pola         = random.choice(pola_pesan)
        teks_chat    = pola.format(qty=qty, produk=produk, harga=fmt_harga(total_harga))

        if random.random() < 0.3:
            teks_chat += " " + random.choice(kata_slang)

        hari_acak = start_date + timedelta(days=random.randint(0, 89))

        data.append({
            "id_transaksi" : f"TRX-{i+1:04d}",
            "tanggal"      : hari_acak,
            "teks_chat"    : teks_chat,
            "nama_produk"  : produk,
            "qty"          : qty,
            "harga_satuan" : harga_satuan,
            "total_harga"  : total_harga,
        })

    df = pd.DataFrame(data)
    df["tanggal"] = pd.to_datetime(df["tanggal"])

    # Buat kolom segmen harga
    df["segmen_harga"] = pd.cut(
        df["harga_satuan"],
        bins=[0, 20000, 60000, 200000],
        labels=["Budget (< 20rb)", "Menengah (20-60rb)", "Premium (> 60rb)"]
    )
    return df


# ================================================================
# BAGIAN 2: SIDEBAR — Navigasi Halaman
# Logika if/elif sederhana untuk berpindah halaman
# ================================================================

# Logo/header sidebar
st.sidebar.image(
    "https://via.placeholder.com/280x60/2ECC71/FFFFFF?text=🧾+ChatKasir",
    use_container_width=True
)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🗂️ Navigasi")

# Tombol pilihan halaman
halaman = st.sidebar.radio(
    label="Pilih Halaman:",
    options=[
        "📊 Ringkasan EDA",
        "💡 Visualisasi Bisnis",
        "🤖 Simulasi Ekstraksi",
    ],
    index=0,       # halaman pertama aktif by default
)

st.sidebar.markdown("---")
st.sidebar.caption("ChatKasir © 2026 | CC26-PSU065")
st.sidebar.caption("Data Science: Salman Pandu Pandiya")


# ================================================================
# HALAMAN 1: RINGKASAN EDA
# ================================================================

if halaman == "📊 Ringkasan EDA":

    # --- Header Halaman ---
    st.title("📊 Ringkasan Exploratory Data Analysis")
    st.markdown(
        """
        Halaman ini merangkum temuan utama dari dua dataset pendukung
        ChatKasir: **Dataset Makanan** dan **Dataset Slang**.
        """
    )
    st.markdown("---")

    # --- Load data ---
    df_food  = load_food()
    df_slang = load_slang()

    # ── SEKSI A: KPI Metrics ─────────────────────────────────────
    st.subheader("🔢 Metrik Utama Dataset")

    # Buat 4 kolom untuk kartu metrik
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📦 Total SKU Makanan",
            value=f"{len(df_food):,}",           # jumlah produk unik
            delta="Setelah de-duplikasi",
        )
    with col2:
        st.metric(
            label="💬 Entri Kamus Slang",
            value=f"{len(df_slang):,}",
            delta="Pasangan slang↔formal",
        )
    with col3:
        st.metric(
            label="📝 Rata-rata Kata / Produk",
            value=f"{df_food['jumlah_kata'].mean():.1f}",
            delta="kata per nama produk",
        )
    with col4:
        st.metric(
            label="🔤 Rata-rata Panjang Slang",
            value=f"{df_slang['panjang_slang'].mean():.1f} karakter",
            delta=f"→ formal: {df_slang['panjang_formal'].mean():.1f} kar",
        )

    st.markdown("---")

    # ── SEKSI B: EDA Dataset Makanan ─────────────────────────────
    st.subheader("🍽️ Eksplorasi Dataset Makanan")

    # Bagi layar menjadi 2 kolom (kiri: grafik, kanan: info)
    col_kiri, col_kanan = st.columns([3, 2])

    with col_kiri:
        st.markdown("**Distribusi Jumlah Produk per Kategori**")
        cat_counts = df_food["kategori"].value_counts()

        # Buat grafik horizontal bar chart dengan matplotlib
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        palette = sns.color_palette("Set2", len(cat_counts))
        ax.barh(cat_counts.index[::-1], cat_counts.values[::-1], color=palette[::-1])
        ax.set_xlabel("Jumlah Produk", fontsize=10)
        ax.set_title("Kategori Produk dalam Katalog", fontsize=11, fontweight="bold")
        for i, v in enumerate(cat_counts.values[::-1]):
            ax.text(v + 20, i, f"{v:,}", va="center", fontsize=8)
        plt.tight_layout()
        # st.pyplot() menampilkan grafik matplotlib langsung di Streamlit
        st.pyplot(fig)
        plt.close(fig)   # tutup figure agar tidak memori bocor

    with col_kanan:
        st.markdown("**Distribusi Jumlah Kata pada Nama Produk**")
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        fig2.patch.set_facecolor(BG)
        ax2.set_facecolor(BG)
        ax2.hist(df_food["jumlah_kata"], bins=range(1, 15),
                 color=PRIMARY, edgecolor="white", rwidth=0.85)
        ax2.axvline(df_food["jumlah_kata"].mean(), color=ACCENT,
                    linestyle="--",
                    label=f"Rata-rata: {df_food['jumlah_kata'].mean():.1f}")
        ax2.set_xlabel("Jumlah Kata", fontsize=10)
        ax2.set_ylabel("Frekuensi", fontsize=10)
        ax2.set_title("Sebaran Panjang Nama Produk", fontsize=11, fontweight="bold")
        ax2.legend(fontsize=9)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    st.markdown("---")

    # ── SEKSI C: EDA Dataset Slang ───────────────────────────────
    st.subheader("💬 Eksplorasi Dataset Slang")

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown("**Top 15 Kata Formal dengan Paling Banyak Variasi Slang**")
        top_formal = df_slang["formal"].value_counts().head(15)
        fig3, ax3  = plt.subplots(figsize=(6, 5))
        fig3.patch.set_facecolor(BG)
        ax3.set_facecolor(BG)
        colors_slang = sns.color_palette("Blues_d", len(top_formal))
        ax3.barh(top_formal.index[::-1], top_formal.values[::-1],
                 color=colors_slang[::-1])
        ax3.set_xlabel("Jumlah Variasi Slang", fontsize=10)
        ax3.set_title("Kata Formal Paling Beragam Slangnya", fontsize=11, fontweight="bold")
        for i, v in enumerate(top_formal.values[::-1]):
            ax3.text(v + 0.1, i, str(v), va="center", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    with col_s2:
        st.markdown("**Perbandingan Panjang: Slang vs Formal**")
        fig4, ax4 = plt.subplots(figsize=(6, 5))
        fig4.patch.set_facecolor(BG)
        ax4.set_facecolor(BG)
        ax4.scatter(df_slang["panjang_slang"], df_slang["panjang_formal"],
                    alpha=0.25, color=SECONDARY, s=12)
        max_val = max(df_slang["panjang_formal"].max(), df_slang["panjang_slang"].max())
        ax4.plot([0, max_val], [0, max_val], color=ACCENT,
                 linestyle="--", label="Panjang sama (y=x)")
        ax4.set_xlabel("Panjang Kata Slang (kar)", fontsize=10)
        ax4.set_ylabel("Panjang Kata Formal (kar)", fontsize=10)
        ax4.set_title("Slang vs Formal: Panjang Karakter", fontsize=11, fontweight="bold")
        ax4.legend(fontsize=9)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

    # Tabel sampel slang yang bisa dijelajahi pengguna
    st.markdown("**🔍 Jelajahi Kamus Slang (Sampel 20 Entri)**")
    # st.dataframe() menampilkan tabel interaktif yang bisa di-scroll
    st.dataframe(
        df_slang[["slang", "formal", "panjang_slang", "panjang_formal"]]
        .sample(20, random_state=7)
        .reset_index(drop=True),
        use_container_width=True,
    )


# ================================================================
# HALAMAN 2: VISUALISASI PERTANYAAN BISNIS + FILTER INTERAKTIF
# ================================================================

elif halaman == "💡 Visualisasi Bisnis":

    st.title("💡 Visualisasi Pertanyaan Bisnis (BQ)")
    st.markdown(
        """
        Halaman ini menjawab 6 pertanyaan bisnis dari data transaksi sintetis.
        Gunakan **filter di bawah** untuk mengeksplorasi data secara interaktif.
        """
    )
    st.markdown("---")

    # --- Load data sintetis ---
    df = buat_data_sintetis(1000)
    df_food  = load_food()
    df_slang = load_slang()

    # ── FILTER INTERAKTIF ────────────────────────────────────────
    st.subheader("🎛️ Filter Data")

    # Buat 3 kolom filter sejajar
    fcol1, fcol2, fcol3 = st.columns(3)

    with fcol1:
        # Filter rentang tanggal
        min_tgl = df["tanggal"].min().date()
        max_tgl = df["tanggal"].max().date()
        tgl_awal, tgl_akhir = st.date_input(
            "📅 Rentang Tanggal",
            value=(min_tgl, max_tgl),
            min_value=min_tgl,
            max_value=max_tgl,
        )

    with fcol2:
        # Filter pilihan produk (multiselect)
        semua_produk = sorted(df["nama_produk"].unique().tolist())
        pilihan_produk = st.multiselect(
            "🍱 Pilih Produk (kosong = semua)",
            options=semua_produk,
            default=[],           # default kosong = tampilkan semua
        )

    with fcol3:
        # Filter rentang harga dengan slider
        harga_min = int(df["harga_satuan"].min())
        harga_max = int(df["harga_satuan"].max())
        range_harga = st.slider(
            "💰 Rentang Harga Satuan (Rp)",
            min_value=harga_min,
            max_value=harga_max,
            value=(harga_min, harga_max),
            step=1000,
            format="Rp%d",
        )

    # --- Terapkan semua filter ke dataframe ---
    # Konversi date ke datetime agar bisa dibandingkan
    df_filtered = df[
        (df["tanggal"].dt.date >= tgl_awal) &
        (df["tanggal"].dt.date <= tgl_akhir) &
        (df["harga_satuan"] >= range_harga[0]) &
        (df["harga_satuan"] <= range_harga[1])
    ]

    # Terapkan filter produk hanya jika ada yang dipilih
    if pilihan_produk:
        df_filtered = df_filtered[df_filtered["nama_produk"].isin(pilihan_produk)]

    # Tampilkan info jumlah data setelah filter
    st.info(
        f"✅ Menampilkan **{len(df_filtered):,}** dari {len(df):,} transaksi "
        f"| {df_filtered['nama_produk'].nunique()} produk unik "
        f"| Periode: {tgl_awal} s/d {tgl_akhir}"
    )
    st.markdown("---")

    # Peringatan jika data kosong setelah filter
    if df_filtered.empty:
        st.warning("⚠️ Tidak ada data yang cocok dengan filter. Coba perlebar rentang filter.")
        st.stop()   # hentikan eksekusi halaman di sini

    # ── BQ-1: PRODUK TERLARIS ────────────────────────────────────
    st.subheader("🏆 BQ-1 | Produk Apa yang Paling Sering Dipesan?")

    top_n = st.slider("Tampilkan Top N produk:", min_value=5, max_value=20, value=10)
    top_produk = df_filtered.groupby("nama_produk")["qty"].sum().nlargest(top_n)

    fig_bq1, ax_bq1 = plt.subplots(figsize=(10, max(4, top_n * 0.4)))
    fig_bq1.patch.set_facecolor(BG)
    ax_bq1.set_facecolor(BG)
    warna = [PRIMARY if i < 3 else "#A9DFBF" for i in range(len(top_produk))]
    ax_bq1.barh(top_produk.index[::-1], top_produk.values[::-1], color=warna[::-1])
    ax_bq1.set_title(f"Top {top_n} Produk Terlaris (berdasarkan Total Qty)",
                     fontsize=12, fontweight="bold")
    ax_bq1.set_xlabel("Total Unit Terjual")
    for i, v in enumerate(top_produk.values[::-1]):
        ax_bq1.text(v + 0.3, i, f"{int(v):,}", va="center", fontsize=8)
    plt.tight_layout()
    st.pyplot(fig_bq1)
    plt.close(fig_bq1)

    # Insight otomatis
    if not top_produk.empty:
        produk_no1 = top_produk.index[0]
        st.success(
            f"💡 **Insight BQ-1:** Produk **{produk_no1.title()}** adalah yang paling "
            f"laris dengan {int(top_produk.iloc[0]):,} unit terjual. "
            f"Pastikan stok produk ini selalu tersedia!"
        )
    st.markdown("---")

    # ── BQ-2: RATA-RATA NILAI TRANSAKSI ──────────────────────────
    st.subheader("💰 BQ-2 | Berapa Rata-rata Nilai Transaksi?")

    mean_trx   = df_filtered["total_harga"].mean()
    median_trx = df_filtered["total_harga"].median()
    max_trx    = df_filtered["total_harga"].max()

    # Kartu KPI untuk BQ-2
    m1, m2, m3 = st.columns(3)
    m1.metric("📈 Rata-rata Transaksi", f"Rp {mean_trx:,.0f}")
    m2.metric("📊 Median Transaksi",    f"Rp {median_trx:,.0f}")
    m3.metric("🚀 Transaksi Terbesar",  f"Rp {max_trx:,.0f}")

    fig_bq2, ax_bq2 = plt.subplots(figsize=(9, 4))
    fig_bq2.patch.set_facecolor(BG)
    ax_bq2.set_facecolor(BG)
    sns.kdeplot(df_filtered["total_harga"] / 1000, ax=ax_bq2,
                fill=True, color=SECONDARY, alpha=0.5)
    ax_bq2.axvline(mean_trx / 1000, color=ACCENT, linestyle="--",
                   label=f"Rata-rata: Rp{mean_trx/1000:.0f}rb")
    ax_bq2.axvline(median_trx / 1000, color="#F39C12", linestyle="-.",
                   label=f"Median: Rp{median_trx/1000:.0f}rb")
    ax_bq2.set_title("Distribusi Nilai Transaksi per Pesanan", fontsize=12, fontweight="bold")
    ax_bq2.set_xlabel("Total Harga (ribu Rp)")
    ax_bq2.set_ylabel("Densitas")
    ax_bq2.legend()
    plt.tight_layout()
    st.pyplot(fig_bq2)
    plt.close(fig_bq2)
    st.markdown("---")

    # ── BQ-3: SEGMENTASI HARGA ───────────────────────────────────
    st.subheader("🏷️ BQ-3 | Bagaimana Distribusi & Segmentasi Harga Produk?")

    col_bq3a, col_bq3b = st.columns(2)

    with col_bq3a:
        segmen_pct = df_filtered["segmen_harga"].value_counts()
        fig_bq3a, ax_bq3a = plt.subplots(figsize=(5, 4))
        fig_bq3a.patch.set_facecolor(BG)
        ax_bq3a.set_facecolor(BG)
        ax_bq3a.hist(df_filtered["harga_satuan"] / 1000, bins=30,
                     color="#5DADE2", edgecolor="white", alpha=0.85)
        for batas in [20, 60]:
            ax_bq3a.axvline(batas, color=ACCENT, linestyle="--", alpha=0.7)
        ax_bq3a.set_title("Histogram Harga Satuan", fontsize=11, fontweight="bold")
        ax_bq3a.set_xlabel("Harga Satuan (ribu Rp)")
        ax_bq3a.set_ylabel("Frekuensi")
        plt.tight_layout()
        st.pyplot(fig_bq3a)
        plt.close(fig_bq3a)

    with col_bq3b:
        fig_bq3b, ax_bq3b = plt.subplots(figsize=(5, 4))
        fig_bq3b.patch.set_facecolor(BG)
        ax_bq3b.pie(
            segmen_pct.values,
            labels=[f"{l}\n({v/len(df_filtered)*100:.0f}%)"
                    for l, v in zip(segmen_pct.index, segmen_pct.values)],
            colors=["#58D68D", "#F7DC6F", "#EC7063"],
            startangle=90,
            wedgeprops={"edgecolor": "white"},
        )
        ax_bq3b.set_title("Proporsi Segmen Harga", fontsize=11, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig_bq3b)
        plt.close(fig_bq3b)

    st.markdown("---")

    # ── BQ-4: DISTRIBUSI QTY ─────────────────────────────────────
    st.subheader("📦 BQ-4 | Berapa Item yang Biasanya Dipesan?")

    qty_dist   = df_filtered["qty"].value_counts().sort_index()
    omset_qty  = df_filtered.groupby("qty")["total_harga"].sum()

    col_bq4a, col_bq4b = st.columns(2)

    with col_bq4a:
        fig_bq4a, ax_bq4a = plt.subplots(figsize=(5, 4))
        fig_bq4a.patch.set_facecolor(BG)
        ax_bq4a.set_facecolor(BG)
        ax_bq4a.bar(qty_dist.index.astype(str), qty_dist.values,
                    color=sns.color_palette("Set2", len(qty_dist)))
        ax_bq4a.set_title("Frekuensi Transaksi per Jumlah Item", fontsize=11, fontweight="bold")
        ax_bq4a.set_xlabel("Jumlah Item (qty)")
        ax_bq4a.set_ylabel("Jumlah Transaksi")
        for i, v in enumerate(qty_dist.values):
            ax_bq4a.text(i, v + 1, str(int(v)), ha="center", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig_bq4a)
        plt.close(fig_bq4a)

    with col_bq4b:
        fig_bq4b, ax_bq4b = plt.subplots(figsize=(5, 4))
        fig_bq4b.patch.set_facecolor(BG)
        ax_bq4b.set_facecolor(BG)
        ax_bq4b.bar(omset_qty.index.astype(str), omset_qty.values / 1e6,
                    color=sns.color_palette("Oranges_d", len(omset_qty)))
        ax_bq4b.set_title("Total Omset per Kelompok Qty", fontsize=11, fontweight="bold")
        ax_bq4b.set_xlabel("Jumlah Item (qty)")
        ax_bq4b.set_ylabel("Total Omset (juta Rp)")
        plt.tight_layout()
        st.pyplot(fig_bq4b)
        plt.close(fig_bq4b)

    st.markdown("---")

    # ── BQ-5: KATA SLANG ─────────────────────────────────────────
    st.subheader("🗣️ BQ-5 | Kata Slang Apa yang Paling Sering Muncul?")

    kamus_slang = set(df_slang["slang"].tolist())

    def cari_slang(teks):
        """Cari kata slang dari kamus di dalam satu kalimat."""
        kata = re.sub(r"[^\w\s]", "", str(teks).lower()).split()
        return [k for k in kata if k in kamus_slang]

    df_filtered = df_filtered.copy()
    df_filtered["slang_ditemukan"] = df_filtered["teks_chat"].apply(cari_slang)
    semua_slang  = [k for sub in df_filtered["slang_ditemukan"] for k in sub]
    top_slang    = Counter(semua_slang).most_common(15)

    if top_slang:
        slang_labels, slang_vals = zip(*top_slang)
        fig_bq5, ax_bq5 = plt.subplots(figsize=(9, 5))
        fig_bq5.patch.set_facecolor(BG)
        ax_bq5.set_facecolor(BG)
        colors_bq5 = ["#8E44AD" if i < 5 else "#D7BDE2" for i in range(len(slang_labels))]
        ax_bq5.barh(slang_labels[::-1], slang_vals[::-1], color=colors_bq5[::-1])
        ax_bq5.set_title("Top 15 Kata Slang Terdeteksi dalam Chat", fontsize=12, fontweight="bold")
        ax_bq5.set_xlabel("Frekuensi")
        plt.tight_layout()
        st.pyplot(fig_bq5)
        plt.close(fig_bq5)
    else:
        # Fallback: tampilkan dari kamus slang langsung jika tidak ada match
        st.info("ℹ️ Menampilkan kata formal dengan paling banyak variasi slang "
                "(dari kamus, sebagai referensi normalisasi).")
        top_formal_bq5 = df_slang["formal"].value_counts().head(15)
        fig_bq5b, ax_bq5b = plt.subplots(figsize=(9, 5))
        fig_bq5b.patch.set_facecolor(BG)
        ax_bq5b.set_facecolor(BG)
        ax_bq5b.barh(top_formal_bq5.index[::-1], top_formal_bq5.values[::-1], color="#8E44AD")
        ax_bq5b.set_title("Kata Formal dengan Variasi Slang Terbanyak", fontsize=12, fontweight="bold")
        ax_bq5b.set_xlabel("Jumlah Variasi")
        plt.tight_layout()
        st.pyplot(fig_bq5b)
        plt.close(fig_bq5b)

    st.markdown("---")

    # ── BQ-6: KATEGORI KATALOG ───────────────────────────────────
    st.subheader("🍽️ BQ-6 | Kategori Apa yang Paling Banyak di Katalog?")

    cat_dist = df_food["kategori"].value_counts()

    col_bq6a, col_bq6b = st.columns(2)

    with col_bq6a:
        fig_bq6a, ax_bq6a = plt.subplots(figsize=(6, 4))
        fig_bq6a.patch.set_facecolor(BG)
        ax_bq6a.set_facecolor(BG)
        palette_cat = sns.color_palette("Set2", len(cat_dist))
        ax_bq6a.bar(cat_dist.index, cat_dist.values, color=palette_cat)
        ax_bq6a.set_title("Jumlah SKU per Kategori", fontsize=11, fontweight="bold")
        ax_bq6a.set_ylabel("Jumlah Produk")
        ax_bq6a.tick_params(axis="x", rotation=30)
        for i, v in enumerate(cat_dist.values):
            ax_bq6a.text(i, v + 20, f"{v:,}", ha="center", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig_bq6a)
        plt.close(fig_bq6a)

    with col_bq6b:
        # Donut chart menggunakan wedgeprops width
        fig_bq6b, ax_bq6b = plt.subplots(figsize=(6, 4))
        fig_bq6b.patch.set_facecolor(BG)
        ax_bq6b.pie(
            cat_dist.values,
            labels=cat_dist.index,
            autopct="%1.0f%%",
            colors=palette_cat,
            startangle=90,
            wedgeprops={"edgecolor": "white", "width": 0.6},
        )
        ax_bq6b.set_title("Proporsi Kategori (Donut)", fontsize=11, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig_bq6b)
        plt.close(fig_bq6b)


# ================================================================
# HALAMAN 3: SIMULASI EKSTRAKSI TEKS (MOCKUP AI)
# ================================================================

elif halaman == "🤖 Simulasi Ekstraksi":

    st.title("🤖 Simulasi Ekstraksi Pesanan dari Chat")
    st.markdown(
        """
        Ketik atau tempel teks obrolan WhatsApp pelanggan di bawah.
        Sistem akan **mensimulasikan** proses ekstraksi AI ChatKasir
        dan menampilkan hasilnya dalam format JSON terstruktur.

        > ⚠️ **Catatan:** Ini adalah **mockup** (tampilan antarmuka) —
        > ekstraksi sesungguhnya dilakukan oleh model NLP yang dikembangkan
        > oleh tim AI Engineer.
        """
    )
    st.markdown("---")

    # --- Load kamus slang untuk normalisasi sederhana ---
    df_slang = load_slang()
    kamus_normalisasi = dict(zip(df_slang["slang"], df_slang["formal"]))
    df_food  = load_food()
    daftar_produk = df_food["name"].tolist()

    # ── SEKSI A: Input Teks ──────────────────────────────────────
    st.subheader("📝 Masukkan Teks Chat Pesanan")

    # Contoh teks untuk memudahkan pengguna mencoba
    contoh_teks = [
        "mau pesan 2 ayam geprek harga 25rb ya kak",
        "beli 3 nasi goreng special 15k total",
        "kak order 1 kopi susu panas 18000 donk",
        "nitip 5 gorengan 500 per biji ya, total 2500",
        "minta 2 mie ayam biasa harganya brp kak?",
    ]

    # Dropdown untuk memilih contoh atau ketik sendiri
    pilihan_contoh = st.selectbox(
        "📋 Pilih contoh teks (atau ketik sendiri di bawah):",
        options=["— Ketik sendiri —"] + contoh_teks,
    )

    # Tentukan nilai awal text area
    nilai_awal = "" if pilihan_contoh == "— Ketik sendiri —" else pilihan_contoh

    # Text area untuk input teks chat
    teks_input = st.text_area(
        label="💬 Teks Chat Pelanggan:",
        value=nilai_awal,
        height=120,
        placeholder="Contoh: mau pesan 2 ayam geprek 25rb ya kak",
    )

    # Tombol untuk memicu proses ekstraksi
    tombol_ekstrak = st.button("🔍 Ekstrak Pesanan", type="primary", use_container_width=True)

    # ── SEKSI B: Proses & Tampilkan Hasil ───────────────────────
    if tombol_ekstrak:

        if not teks_input.strip():
            st.warning("⚠️ Teks chat tidak boleh kosong!")
        else:
            # Animasi loading spinner saat "memproses"
            with st.spinner("🤖 Model AI sedang memproses teks..."):
                import time
                time.sleep(1)   # simulasi delay pemrosesan

            # ── Langkah 1: Normalisasi Slang ──────────────────
            def normalisasi(teks, kamus):
                """Ganti setiap kata slang dengan kata formalnya."""
                kata_kata = teks.lower().split()
                hasil = []
                for kata in kata_kata:
                    # Cari di kamus; jika tidak ada, pakai kata aslinya
                    hasil.append(kamus.get(kata, kata))
                return " ".join(hasil)

            teks_normal = normalisasi(teks_input, kamus_normalisasi)

            # ── Langkah 2: Ekstraksi Entitas (Rule-Based Mockup) ──
            def ekstrak_angka(teks):
                """Cari semua angka dalam teks (termasuk format 'rb' dan 'k')."""
                # Cari format "Xrb" atau "Xk" dulu (harga informal)
                rb_match = re.findall(r"(\d+)\s*rb", teks, re.IGNORECASE)
                k_match  = re.findall(r"(\d+)\s*k\b", teks, re.IGNORECASE)
                rp_match = re.findall(r"rp\s?(\d+[\.,]?\d*)", teks, re.IGNORECASE)
                # Cari angka biasa
                num_match = re.findall(r"\b(\d+)\b", teks)
                return rb_match, k_match, rp_match, num_match

            def ekstrak_produk_mockup(teks, daftar):
                """
                Cari nama produk dalam teks dengan mencocokkan 2-3 kata.
                Ini versi sederhana — model asli pakai deep learning.
                """
                teks_lower = teks.lower()
                cocok = []
                for nama in daftar:
                    if nama in teks_lower:
                        cocok.append(nama)
                # Kembalikan produk terpanjang yang cocok (paling spesifik)
                if cocok:
                    return sorted(cocok, key=len, reverse=True)[0]
                return None

            rb_m, k_m, rp_m, num_m = ekstrak_angka(teks_normal)
            produk_cocok = ekstrak_produk_mockup(teks_normal, daftar_produk)

            # Tentukan qty: cari angka kecil (1-20) yang bukan harga
            qty_kandidat = [int(n) for n in num_m if 1 <= int(n) <= 20]
            qty_terdeteksi = qty_kandidat[0] if qty_kandidat else None

            # Tentukan harga: prioritaskan format informal
            harga_terdeteksi = None
            if rb_m:
                harga_terdeteksi = int(rb_m[0]) * 1000
            elif k_m:
                harga_terdeteksi = int(k_m[0]) * 1000
            elif rp_m:
                harga_terdeteksi = int(re.sub(r"[.,]", "", rp_m[0]))
            elif len(num_m) > 1:
                # Ambil angka terbesar sebagai harga
                kandidat_harga = [int(n) for n in num_m if int(n) > 1000]
                if kandidat_harga:
                    harga_terdeteksi = max(kandidat_harga)

            # ── Langkah 3: Susun Hasil JSON ───────────────────
            # Hitung confidence score mockup (simulasi saja)
            skor_produk    = 0.92 if produk_cocok     else 0.31
            skor_qty       = 0.88 if qty_terdeteksi   else 0.45
            skor_harga     = 0.85 if harga_terdeteksi else 0.28
            skor_keseluruhan = round((skor_produk + skor_qty + skor_harga) / 3, 2)

            hasil_json = {
                "status"      : "success",
                "versi_model" : "ChatKasir-NLP v1.0 (mockup)",
                "input"       : {
                    "teks_asli"         : teks_input,
                    "teks_normalisasi"  : teks_normal,
                },
                "ekstraksi" : {
                    "nama_produk" : {
                        "nilai"      : produk_cocok.title() if produk_cocok else "Tidak terdeteksi",
                        "confidence" : skor_produk,
                    },
                    "qty" : {
                        "nilai"      : qty_terdeteksi if qty_terdeteksi else "Tidak terdeteksi",
                        "confidence" : skor_qty,
                    },
                    "harga_total" : {
                        "nilai"      : f"Rp {harga_terdeteksi:,}" if harga_terdeteksi else "Tidak terdeteksi",
                        "confidence" : skor_harga,
                    },
                },
                "confidence_keseluruhan" : skor_keseluruhan,
                "catatan" : (
                    "Hasil ini adalah mockup untuk demonstrasi UI. "
                    "Pada sistem produksi, ekstraksi dilakukan oleh "
                    "model TensorFlow dengan akurasi target ≥ 85%."
                ),
            }

            # ── Tampilkan Hasil ───────────────────────────────
            st.success("✅ Ekstraksi selesai!")
            st.markdown("---")

            # Kartu hasil utama
            st.subheader("📋 Hasil Ekstraksi")
            r1, r2, r3, r4 = st.columns(4)

            def warna_confidence(val):
                """Tentukan warna berdasarkan nilai confidence."""
                if val >= 0.8: return "normal"
                if val >= 0.5: return "off"
                return "inverse"

            r1.metric(
                "🍱 Produk",
                hasil_json["ekstraksi"]["nama_produk"]["nilai"],
                f"conf: {skor_produk:.0%}",
                delta_color=warna_confidence(skor_produk),
            )
            r2.metric(
                "📦 Qty",
                str(hasil_json["ekstraksi"]["qty"]["nilai"]),
                f"conf: {skor_qty:.0%}",
                delta_color=warna_confidence(skor_qty),
            )
            r3.metric(
                "💰 Harga",
                hasil_json["ekstraksi"]["harga_total"]["nilai"],
                f"conf: {skor_harga:.0%}",
                delta_color=warna_confidence(skor_harga),
            )
            r4.metric(
                "🎯 Confidence",
                f"{skor_keseluruhan:.0%}",
                "keseluruhan",
            )

            # Progress bar confidence keseluruhan
            st.markdown("**Confidence Score Keseluruhan:**")
            st.progress(skor_keseluruhan)

            # Teks setelah normalisasi slang
            st.markdown("---")
            st.subheader("🔄 Detail Proses")

            col_detail1, col_detail2 = st.columns(2)
            with col_detail1:
                st.markdown("**Teks Asli:**")
                # st.code menampilkan teks dalam box kode yang rapi
                st.code(teks_input, language=None)

            with col_detail2:
                st.markdown("**Setelah Normalisasi Slang:**")
                st.code(teks_normal, language=None)

            # Tampilkan output JSON lengkap
            st.markdown("---")
            st.subheader("📄 Response JSON Lengkap (Format API)")
            # st.json() menampilkan JSON dengan syntax highlighting otomatis
            st.json(hasil_json)

            # Tombol download hasil JSON
            json_str = json.dumps(hasil_json, ensure_ascii=False, indent=2)
            st.download_button(
                label="⬇️ Download Hasil sebagai JSON",
                data=json_str,
                file_name="hasil_ekstraksi_chatkasir.json",
                mime="application/json",
            )
