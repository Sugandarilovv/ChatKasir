# ╔══════════════════════════════════════════════════════════════════╗
# ║  app.py — ChatKasir Dashboard (Kerangka Navigasi)               ║
# ║  Streamlit · 3 Halaman: Ringkasan | Analisis | Simulasi         ║
# ╚══════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import re
from collections import Counter

# ── Konfigurasi halaman (WAJIB baris pertama setelah import) ──────────────────
st.set_page_config(
    page_title="ChatKasir Analytics",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Warna brand (konsisten dengan notebook) ───────────────────────────────────
WARNA = {
    "biru"   : "#2E86AB",
    "merah"  : "#E84855",
    "hijau"  : "#3BB273",
    "kuning" : "#F7B731",
}

# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 1 — FUNGSI MUAT DATA (dengan cache agar tidak reload terus)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def muat_data_sintetis():
    """Muat & bersihkan data sintetis dari CSV."""
    df = pd.read_csv("chatkasir_synthetic.csv")

    # Fitur turunan (logika dari notebook)
    df["harga_eksplisit"] = df["price_satuan"] != -1
    df["multi_produk"]    = df["product"].str.contains(" & ", na=False)
    df["qty_numerik"]     = pd.to_numeric(df["quantity"], errors="coerce").notna()

    def segmen_harga(h):
        if h == -1:        return "Tidak Disebutkan"
        elif h < 15_000:   return "Murah (< 15rb)"
        elif h < 35_000:   return "Sedang (15rb–35rb)"
        elif h < 60_000:   return "Agak Mahal (35rb–60rb)"
        else:              return "Mahal (≥ 60rb)"

    df["segmen_harga"] = df["price_satuan"].apply(segmen_harga)
    return df


@st.cache_data
def muat_data_makanan():
    """Muat & tambahkan kategori ke dataset makanan."""
    df = pd.read_csv("food_utama.csv")
    df["name_clean"] = df["name"].str.strip().str.lower()

    PETA_KATEGORI = {
        "nasi": "Nasi", "mie": "Mie & Pasta", "spaghetti": "Mie & Pasta",
        "pasta": "Mie & Pasta", "ayam": "Ayam", "chicken": "Ayam",
        "ikan": "Seafood", "udang": "Seafood", "kepiting": "Seafood",
        "cumi": "Seafood", "es": "Minuman Es", "ice": "Minuman Es",
        "iced": "Minuman Es", "kopi": "Kopi", "coffee": "Kopi",
        "teh": "Teh", "juice": "Jus & Smoothie", "jus": "Jus & Smoothie",
        "smoothie": "Jus & Smoothie", "roti": "Roti & Bakery",
        "bolu": "Roti & Bakery", "cake": "Roti & Bakery",
        "donat": "Roti & Bakery", "bakso": "Bakso & Soto",
        "soto": "Bakso & Soto", "sop": "Bakso & Soto",
        "sup": "Bakso & Soto", "pisang": "Buah & Dessert",
        "strawberry": "Buah & Dessert", "mangga": "Buah & Dessert",
        "seblak": "Jajanan", "cireng": "Jajanan", "batagor": "Jajanan",
        "beef": "Daging Sapi", "sapi": "Daging Sapi", "steak": "Daging Sapi",
        "kacang": "Camilan", "keripik": "Camilan", "chips": "Camilan",
        "hot": "Minuman Panas", "choco": "Minuman Panas",
    }

    df["kategori"]     = df["name_clean"].apply(
        lambda n: PETA_KATEGORI.get(n.split()[0], "Lainnya")
    )
    df["panjang_nama"] = df["name_clean"].apply(lambda n: len(n.split()))
    return df


@st.cache_data
def muat_data_slang():
    """Muat kamus slang & hitung fitur turunan."""
    df = pd.read_csv("slang_utama.csv")
    df["panjang_slang"]   = df["slang"].str.len()
    df["panjang_formal"]  = df["formal"].str.len()
    df["selisih_panjang"] = df["panjang_formal"] - df["panjang_slang"]
    df["tipe"] = df["selisih_panjang"].apply(
        lambda s: "Disingkat" if s > 0 else ("Sama panjang" if s == 0 else "Diperpanjang")
    )
    return df


@st.cache_data
def hitung_slang_aktif(n_sample: int = 10_000):
    """Hitung frekuensi kata slang dalam sampel teks percakapan."""
    df_synth = pd.read_csv("chatkasir_synthetic.csv")
    df_slang = pd.read_csv("slang_utama.csv")
    set_slang = set(df_slang["slang"].str.lower())

    sample = df_synth["input_text"].sample(n_sample, random_state=42)
    semua_kata = []
    for teks in sample:
        bagian_customer = teks.split("[SEP]")[0].lower()
        semua_kata.extend(re.findall(r"\b\w+\b", bagian_customer))

    counter = Counter(k for k in semua_kata if k in set_slang)
    return counter, df_slang


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 2 — SIDEBAR: NAVIGASI + FILTER
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.image(
        "https://via.placeholder.com/200x60/2E86AB/FFFFFF?text=ChatKasir",
        use_container_width=True,
    )
    st.markdown("---")

    # ── Menu navigasi ─────────────────────────────────────────────────────────
    halaman = st.radio(
        "📂 Navigasi",
        options=["🏠 Ringkasan Data", "📊 Analisis Bisnis", "💬 Simulasi ChatKasir"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # ── Panel filter (hanya aktif di halaman Analisis Bisnis) ─────────────────
    if halaman == "📊 Analisis Bisnis":
        st.markdown("### 🎛️ Filter Data")

        # Filter slider rentang harga
        harga_min, harga_max = st.slider(
            "Rentang Harga Satuan (Rp)",
            min_value=3_000,
            max_value=75_000,
            value=(3_000, 75_000),
            step=1_000,
            format="Rp %d",
        )

        # Filter pola percakapan
        pola_pilihan = st.multiselect(
            "Pola Percakapan",
            options=[1, 2, 3, 4],
            default=[1, 2, 3, 4],
            format_func=lambda x: f"Pola {x}",
        )

        # Filter segmen harga
        segmen_pilihan = st.multiselect(
            "Segmen Harga",
            options=["Murah (< 15rb)", "Sedang (15rb–35rb)",
                     "Agak Mahal (35rb–60rb)", "Mahal (≥ 60rb)"],
            default=["Murah (< 15rb)", "Sedang (15rb–35rb)",
                     "Agak Mahal (35rb–60rb)", "Mahal (≥ 60rb)"],
        )
    else:
        # Nilai default ketika filter tidak ditampilkan
        harga_min, harga_max = 3_000, 75_000
        pola_pilihan         = [1, 2, 3, 4]
        segmen_pilihan       = ["Murah (< 15rb)", "Sedang (15rb–35rb)",
                                "Agak Mahal (35rb–60rb)", "Mahal (≥ 60rb)"]

    st.markdown("---")
    st.caption("ChatKasir · CC26-PSU065 · Coding Camp 2026")


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 3 — FUNGSI FILTER DATA (terhubung ke sidebar)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def terapkan_filter(harga_min, harga_max, pola_pilihan_tuple, segmen_pilihan_tuple):
    """
    Muat data sintetis dan terapkan filter dari sidebar.
    Parameter filter dibuat tuple agar bisa di-cache oleh Streamlit.
    """
    df = muat_data_sintetis()

    # Filter harga (hanya baris dengan harga eksplisit)
    mask_harga = (
        (~df["harga_eksplisit"]) |  # baris tanpa harga tetap diikutkan
        ((df["price_satuan"] >= harga_min) & (df["price_satuan"] <= harga_max))
    )

    # Filter pola percakapan
    mask_pola = df["pattern"].isin(pola_pilihan_tuple)

    # Filter segmen harga
    mask_segmen = (
        (~df["harga_eksplisit"]) |
        df["segmen_harga"].isin(segmen_pilihan_tuple)
    )

    return df[mask_harga & mask_pola & mask_segmen].copy()


# Panggil fungsi filter dengan parameter yang bisa di-cache (pakai tuple)
df_filtered = terapkan_filter(
    harga_min,
    harga_max,
    tuple(sorted(pola_pilihan)),
    tuple(sorted(segmen_pilihan)),
)


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 4 — HALAMAN 1: RINGKASAN DATA
# ══════════════════════════════════════════════════════════════════════════════

if halaman == "🏠 Ringkasan Data":

    st.title("🧾 ChatKasir — Ringkasan Dataset")
    st.caption("Ikhtisar tiga dataset yang digunakan sistem ChatKasir")

    # ── Baris KPI: 4 kartu metrik utama ──────────────────────────────────────
    df_synth = muat_data_sintetis()
    df_food  = muat_data_makanan()
    df_slang = muat_data_slang()

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        label="📦 Total Data Sintetis",
        value=f"{len(df_synth):,}",
        help="Total baris percakapan pesanan dalam dataset latih",
    )
    k2.metric(
        label="🍜 Nama Produk Makanan",
        value=f"{len(df_food):,}",
        help="Total nama produk unik dalam dataset food_utama.csv",
    )
    k3.metric(
        label="💬 Entri Kamus Slang",
        value=f"{len(df_slang):,}",
        help="Total pasangan slang→formal dalam kamus normalisasi",
    )
    k4.metric(
        label="🏷️ Kategori Makanan",
        value=f"{df_food['kategori'].nunique()}",
        help="Jumlah kelompok kategori masakan yang teridentifikasi",
    )

    st.markdown("---")

    # ── Tabel pertanyaan bisnis ───────────────────────────────────────────────
    st.subheader("📋 Pertanyaan Bisnis yang Dijawab Dashboard Ini")

    with st.expander("ℹ️ Apa itu Pertanyaan Bisnis? Klik untuk baca penjelasan"):
        st.info(
            "Pertanyaan bisnis adalah daftar masalah nyata yang ingin dijawab "
            "menggunakan data. Setiap grafik di halaman **Analisis Bisnis** "
            "dirancang untuk menjawab tepat satu pertanyaan di bawah ini."
        )

    pb_data = {
        "Kode"  : ["PB-1","PB-2","PB-3","PB-4","PB-5","PB-6","PB-7"],
        "Pertanyaan Bisnis" : [
            "Produk apa yang paling sering dipesan?",
            "Berapa rata-rata nilai transaksi per pesanan?",
            "Bagaimana distribusi rentang harga produk?",
            "Pola kalimat pesanan mana yang paling umum?",
            "Kata slang apa yang paling aktif dalam percakapan?",
            "Berapa porsi pesanan tanpa harga eksplisit?",
            "Bagaimana distribusi tipe kuantitas (angka vs teks)?",
        ],
        "Manfaat untuk UMKM" : [
            "Prioritas stok & promo",
            "Dasar penetapan harga",
            "Segmentasi pasar",
            "Prioritas pengembangan model AI",
            "Kamus normalisasi AI",
            "Rancangan fallback model",
            "Desain parser kuantitas",
        ],
    }
    st.dataframe(
        pd.DataFrame(pb_data),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # ── Preview tiga dataset (tab) ────────────────────────────────────────────
    st.subheader("🔍 Preview Dataset")

    tab1, tab2, tab3 = st.tabs(
        ["📊 Data Sintetis", "🍜 Data Makanan", "💬 Data Slang"]
    )

    with tab1:
        st.caption(f"100.000 baris · 5 kolom asli + 4 kolom turunan")
        st.dataframe(df_synth.head(20), use_container_width=True, hide_index=True)

    with tab2:
        st.caption(f"{len(df_food):,} nama produk · 3 kolom")
        st.dataframe(df_food.head(20), use_container_width=True, hide_index=True)

    with tab3:
        st.caption(f"{len(df_slang):,} entri slang · 5 kolom")
        st.dataframe(df_slang.head(20), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 5 — HALAMAN 2: ANALISIS BISNIS (LENGKAP)
# ══════════════════════════════════════════════════════════════════════════════

elif halaman == "📊 Analisis Bisnis":
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # ── Warna Plotly (konsisten dengan brand) ─────────────────────────────────
    PALET = [
        "#2E86AB", "#3BB273", "#F7B731", "#E84855",
        "#7B2D8B", "#FF6B35", "#1B4332", "#F4A261",
    ]

    st.title("📊 Analisis Bisnis — ChatKasir")
    st.caption(
        f"Menampilkan **{len(df_filtered):,}** dari 100.000 baris  "
        f"· Filter: Rp {harga_min:,}–Rp {harga_max:,} "
        f"· Pola: {pola_pilihan}"
    )

    # ── 4 Kartu KPI ───────────────────────────────────────────────────────────
    df_harga = df_filtered[df_filtered["harga_eksplisit"]]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📋 Total Pesanan (Filtered)",  f"{len(df_filtered):,}")
    k2.metric(
        "💰 Rata-rata Harga Satuan",
        f"Rp {df_harga['price_satuan'].mean():,.0f}" if len(df_harga) else "N/A",
        help="Hanya dari pesanan yang menyebut harga secara eksplisit",
    )
    k3.metric(
        "📍 Median Harga",
        f"Rp {df_harga['price_satuan'].median():,.0f}" if len(df_harga) else "N/A",
    )
    k4.metric(
        "❓ Tanpa Harga Eksplisit",
        f"{(~df_filtered['harga_eksplisit']).sum():,}",
        delta=f"{(~df_filtered['harga_eksplisit']).mean()*100:.1f}% dari total",
        delta_color="inverse",
        help="Pesanan yang tidak menyebut harga → butuh fallback model",
    )

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # PB-1 & PB-2 — Baris pertama (dua kolom)
    # ══════════════════════════════════════════════════════════════════════════
    col_pb1, col_pb2 = st.columns(2, gap="medium")

    # ── PB-1: Top 20 Produk Terlaris ─────────────────────────────────────────
    with col_pb1:
        st.subheader("🏆 PB-1 — Produk Paling Sering Dipesan")

        with st.expander("💡 Insight"):
            st.info(
                "Produk di posisi teratas adalah prioritas stok utama. "
                "Pastikan produk ini tidak pernah habis di jam sibuk."
            )

        # Pisahkan multi-produk (separator ' & ')
        semua_produk = (
            df_filtered["product"]
            .dropna()
            .apply(lambda x: [p.strip().lower() for p in x.split(" & ")])
            .explode()
        )
        top20 = semua_produk.value_counts().head(20).reset_index()
        top20.columns = ["Produk", "Frekuensi"]
        top20 = top20.sort_values("Frekuensi", ascending=True)  # untuk barh

        fig_pb1 = px.bar(
            top20,
            x="Frekuensi",
            y="Produk",
            orientation="h",
            text="Frekuensi",
            color="Frekuensi",
            color_continuous_scale="Blues",
            labels={"Frekuensi": "Jumlah Kemunculan", "Produk": ""},
            title="Top 20 Produk — semakin panjang bar, semakin wajib tersedia",
        )
        fig_pb1.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
            textfont_size=11,
        )
        fig_pb1.update_layout(
            height=500,
            showlegend=False,
            coloraxis_showscale=False,
            title_font_size=13,
            margin=dict(l=0, r=40, t=50, b=20),
            hoverlabel=dict(bgcolor="white", font_size=12),
        )
        st.plotly_chart(fig_pb1, use_container_width=True)

    # ── PB-2: Distribusi Harga + Statistik ───────────────────────────────────
    with col_pb2:
        st.subheader("💰 PB-2 — Sebaran Harga Satuan per Produk")

        with st.expander("💡 Insight"):
            st.info(
                "Rata-rata transaksi ~Rp 39rb. Strategi bundling lebih efektif "
                "daripada diskon tunggal untuk segmen harga menengah ini."
            )

        if len(df_harga) == 0:
            st.warning("Tidak ada data harga pada filter yang dipilih.")
        else:
            mean_h   = df_harga["price_satuan"].mean()
            median_h = df_harga["price_satuan"].median()

            fig_pb2 = go.Figure()

            # Histogram harga
            fig_pb2.add_trace(go.Histogram(
                x=df_harga["price_satuan"] / 1000,
                nbinsx=30,
                name="Distribusi Harga",
                marker_color="#2E86AB",
                opacity=0.8,
                hovertemplate="Rp %{x:.0f}rb<br>Frekuensi: %{y:,}<extra></extra>",
            ))

            # Garis mean
            fig_pb2.add_vline(
                x=mean_h / 1000,
                line_dash="dash", line_color="#E84855", line_width=2,
                annotation_text=f"Mean: Rp {mean_h/1000:.0f}rb",
                annotation_position="top right",
                annotation_font_color="#E84855",
            )

            # Garis median
            fig_pb2.add_vline(
                x=median_h / 1000,
                line_dash="dot", line_color="#F7B731", line_width=2,
                annotation_text=f"Median: Rp {median_h/1000:.0f}rb",
                annotation_position="top left",
                annotation_font_color="#F7B731",
            )

            fig_pb2.update_layout(
                title="Histogram Harga — Garis merah=mean, kuning=median",
                xaxis_title="Harga (ribuan Rupiah)",
                yaxis_title="Frekuensi",
                height=500,
                title_font_size=13,
                margin=dict(l=0, r=20, t=50, b=20),
                bargap=0.05,
                hoverlabel=dict(bgcolor="white", font_size=12),
            )
            st.plotly_chart(fig_pb2, use_container_width=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # PB-3 & PB-4 — Baris kedua (dua kolom)
    # ══════════════════════════════════════════════════════════════════════════
    col_pb3, col_pb4 = st.columns(2, gap="medium")

    # ── PB-3: Segmentasi Harga ────────────────────────────────────────────────
    with col_pb3:
        st.subheader("🏷️ PB-3 — Segmen Harga yang Mendominasi Menu")

        with st.expander("💡 Insight"):
            st.info(
                "Segmen 'Agak Mahal (35rb–60rb)' mendominasi. "
                "Pelanggan UMKM muda bersedia membayar harga menengah ke atas."
            )

        urutan_segmen = [
            "Murah (< 15rb)", "Sedang (15rb–35rb)",
            "Agak Mahal (35rb–60rb)", "Mahal (≥ 60rb)",
        ]
        df_seg = (
            df_harga["segmen_harga"]
            .value_counts()
            .reindex(urutan_segmen)
            .fillna(0)
            .reset_index()
        )
        df_seg.columns = ["Segmen", "Jumlah"]
        df_seg["Persen"] = (df_seg["Jumlah"] / df_seg["Jumlah"].sum() * 100).round(1)

        fig_pb3 = px.bar(
            df_seg,
            x="Segmen",
            y="Jumlah",
            text=df_seg.apply(
                lambda r: f"{r['Jumlah']:,.0f}<br>({r['Persen']}%)", axis=1
            ),
            color="Segmen",
            color_discrete_sequence=["#3BB273", "#F7B731", "#2E86AB", "#E84855"],
            labels={"Jumlah": "Frekuensi", "Segmen": ""},
            title="4 Segmen Harga — persentase menunjukkan dominasi pasar",
        )
        fig_pb3.update_traces(
            textposition="outside",
            textfont_size=12,
            hovertemplate="<b>%{x}</b><br>Jumlah: %{y:,}<extra></extra>",
        )
        fig_pb3.update_layout(
            height=420,
            showlegend=False,
            title_font_size=13,
            margin=dict(l=0, r=20, t=50, b=20),
            xaxis_tickangle=-10,
        )
        st.plotly_chart(fig_pb3, use_container_width=True)

    # ── PB-4: Pola Percakapan ─────────────────────────────────────────────────
    with col_pb4:
        st.subheader("🗣️ PB-4 — Pola Kalimat yang Paling Sering Dipakai Pelanggan")

        with st.expander("💡 Insight"):
            st.info(
                "Pola 1 & 2 menyumbang ~62% percakapan. "
                "Model NLP harus diprioritaskan untuk dua pola ini terlebih dahulu."
            )

        pola_label_map = {
            1: "Pola 1 — Standar",
            2: "Pola 2 — Informal Singkat",
            3: "Pola 3 — Multi Produk Teks",
            4: "Pola 4 — Multi Produk Kompleks",
        }
        df_pola = (
            df_filtered["pattern"]
            .value_counts()
            .sort_index()
            .reset_index()
        )
        df_pola.columns = ["Pola", "Jumlah"]
        df_pola["Label"] = df_pola["Pola"].map(pola_label_map)
        df_pola["Persen"] = (df_pola["Jumlah"] / df_pola["Jumlah"].sum() * 100).round(1)

        # Donut chart interaktif
        fig_pb4 = go.Figure(go.Pie(
            labels=df_pola["Label"],
            values=df_pola["Jumlah"],
            hole=0.5,
            marker_colors=PALET[:4],
            textinfo="percent+label",
            textfont_size=11,
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Jumlah: %{value:,}<br>"
                "Proporsi: %{percent}<extra></extra>"
            ),
        ))
        fig_pb4.update_layout(
            title="Proporsi Pola — hover untuk detail angka",
            height=420,
            title_font_size=13,
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=-0.25,
                xanchor="center", x=0.5,
                font_size=10,
            ),
            annotations=[dict(
                text=f"<b>{len(df_filtered):,}</b><br>pesanan",
                x=0.5, y=0.5, font_size=13,
                showarrow=False,
            )],
        )
        st.plotly_chart(fig_pb4, use_container_width=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # PB-5 — Lebar penuh
    # ══════════════════════════════════════════════════════════════════════════
    st.subheader("💬 PB-5 — Kata Slang yang Paling Aktif dalam Percakapan Pelanggan")

    with st.expander("💡 Insight"):
        st.info(
            "Hanya 20–30 kata slang mendominasi sebagian besar percakapan. "
            "Tim AI cukup memprioritaskan kata-kata ini untuk normalisasi — "
            "dampak terbesar dengan effort terkecil."
        )

    with st.spinner("🔍 Menghitung frekuensi slang dari 10.000 sampel..."):
        counter_slang, df_slang_ref = hitung_slang_aktif(n_sample=10_000)

    top20_slang = pd.DataFrame(
        counter_slang.most_common(20), columns=["Slang", "Frekuensi"]
    )
    # Tambah kolom bentuk formal
    top20_slang["Formal"] = top20_slang["Slang"].map(
        df_slang_ref.set_index("slang")["formal"]
    )
    top20_slang = top20_slang.sort_values("Frekuensi", ascending=True)

    fig_pb5 = px.bar(
        top20_slang,
        x="Frekuensi",
        y="Slang",
        orientation="h",
        text="Frekuensi",
        color="Frekuensi",
        color_continuous_scale="Reds",
        custom_data=["Formal"],
        labels={"Frekuensi": "Kemunculan dalam 10.000 Sampel", "Slang": ""},
        title="Top 20 Slang Aktif — hover untuk melihat padanan formalnya",
    )
    fig_pb5.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        hovertemplate=(
            "<b>Slang:</b> %{y}<br>"
            "<b>Formal:</b> %{customdata[0]}<br>"
            "<b>Frekuensi:</b> %{x:,}<extra></extra>"
        ),
    )
    fig_pb5.update_layout(
        height=520,
        coloraxis_showscale=False,
        title_font_size=13,
        margin=dict(l=0, r=60, t=50, b=20),
    )
    st.plotly_chart(fig_pb5, use_container_width=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # PB-6 & PB-7 — Baris terakhir (dua kolom)
    # ══════════════════════════════════════════════════════════════════════════
    col_pb6, col_pb7 = st.columns(2, gap="medium")

    # ── PB-6: Harga Eksplisit vs Tidak ───────────────────────────────────────
    with col_pb6:
        st.subheader("❓ PB-6 — Seberapa Sering Pelanggan Tidak Menyebut Harga?")

        with st.expander("💡 Insight"):
            st.info(
                "~33.9% pesanan tidak menyebut harga. Ini adalah kasus edge "
                "terbesar yang harus ditangani model — bangun fallback "
                "'ambil harga terakhir dari database'."
            )

        jml_eksplisit = df_filtered["harga_eksplisit"].sum()
        jml_implisit  = (~df_filtered["harga_eksplisit"]).sum()

        # Stacked bar per pola (lebih informatif dari pie biasa)
        pola_breakdown = (
            df_filtered
            .groupby("pattern")["harga_eksplisit"]
            .value_counts(normalize=True)
            .unstack(fill_value=0)
            .rename(columns={True: "Disebutkan", False: "Tidak Disebutkan"})
            * 100
        )
        pola_breakdown.index = [f"Pola {i}" for i in pola_breakdown.index]
        pola_breakdown = pola_breakdown.reset_index().rename(
            columns={"index": "Pola", "pattern": "Pola"}
        )

        fig_pb6 = go.Figure()

        for col_name, warna in [("Disebutkan", "#3BB273"), ("Tidak Disebutkan", "#E84855")]:
            if col_name in pola_breakdown.columns:
                fig_pb6.add_trace(go.Bar(
                    name=col_name,
                    x=pola_breakdown["Pola"],
                    y=pola_breakdown[col_name].round(1),
                    marker_color=warna,
                    text=pola_breakdown[col_name].round(1).astype(str) + "%",
                    textposition="inside",
                    textfont_size=12,
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        f"{col_name}: %{{y:.1f}}%<extra></extra>"
                    ),
                ))

        fig_pb6.update_layout(
            barmode="stack",
            title=(
                f"Harga Disebutkan {jml_eksplisit:,} vs "
                f"Tidak {jml_implisit:,} — per pola percakapan"
            ),
            xaxis_title="Pola Percakapan",
            yaxis_title="Persentase (%)",
            height=420,
            title_font_size=12,
            legend=dict(orientation="h", y=1.12, x=0),
            margin=dict(l=0, r=20, t=70, b=20),
        )
        st.plotly_chart(fig_pb6, use_container_width=True)

    # ── PB-7: Tipe Kuantitas ──────────────────────────────────────────────────
    with col_pb7:
        st.subheader("🔢 PB-7 — Kuantitas Ditulis Angka atau Teks?")

        with st.expander("💡 Insight"):
            st.info(
                ">59% kuantitas ditulis sebagai teks ('setengah', 'seporsi', dll.). "
                "Wajib bangun konverter teks→angka sebelum data masuk ke model."
            )

        # Tab: donut + top ekspresi teks
        tab_donut, tab_teks = st.tabs(["📊 Proporsi", "📋 Top Ekspresi Teks"])

        with tab_donut:
            qty_counts = df_filtered["qty_numerik"].value_counts()
            labels_pie  = ["Numerik (angka)", "Deskriptif (teks)"]
            values_pie  = [
                qty_counts.get(True, 0),
                qty_counts.get(False, 0),
            ]

            fig_pb7a = go.Figure(go.Pie(
                labels=labels_pie,
                values=values_pie,
                hole=0.55,
                marker_colors=["#3BB273", "#F7B731"],
                textinfo="percent+label",
                textfont_size=12,
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Jumlah: %{value:,}<br>"
                    "Proporsi: %{percent}<extra></extra>"
                ),
            ))
            fig_pb7a.update_layout(
                height=360,
                margin=dict(l=20, r=20, t=30, b=20),
                annotations=[dict(
                    text=f"<b>{sum(values_pie):,}</b><br>pesanan",
                    x=0.5, y=0.5, font_size=13, showarrow=False,
                )],
                showlegend=True,
                legend=dict(orientation="h", y=-0.1, x=0.2),
            )
            st.plotly_chart(fig_pb7a, use_container_width=True)

        with tab_teks:
            qty_teks    = df_filtered.loc[~df_filtered["qty_numerik"], "quantity"]
            qty_tunggal = qty_teks[~qty_teks.str.contains("&", na=False)]
            top_qty     = qty_tunggal.value_counts().head(15).reset_index()
            top_qty.columns = ["Ekspresi", "Frekuensi"]

            fig_pb7b = px.bar(
                top_qty.sort_values("Frekuensi", ascending=True),
                x="Frekuensi",
                y="Ekspresi",
                orientation="h",
                text="Frekuensi",
                color="Frekuensi",
                color_continuous_scale="Oranges",
                title="Ekspresi teks ini perlu dikonversi ke angka oleh model",
                labels={"Frekuensi": "Kemunculan", "Ekspresi": ""},
            )
            fig_pb7b.update_traces(
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Frekuensi: %{x:,}<extra></extra>",
            )
            fig_pb7b.update_layout(
                height=400,
                coloraxis_showscale=False,
                title_font_size=12,
                margin=dict(l=0, r=60, t=50, b=20),
            )
            st.plotly_chart(fig_pb7b, use_container_width=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # BONUS — Tabel Ringkasan Insight (selalu di bawah semua grafik)
    # ══════════════════════════════════════════════════════════════════════════
    with st.expander("📝 Buka Ringkasan Semua Insight Bisnis"):
        insight_data = {
            "No" : ["1", "2", "3", "4", "5", "6"],
            "Insight" : [
                "Stok produk terlaris harus selalu terjaga di jam sibuk",
                "Pelanggan bersedia bayar Rp 35rb–60rb → strategi bundling lebih efektif dari diskon",
                "Pola 1 & 2 mendominasi 62% — prioritaskan akurasi model untuk dua pola ini",
                "1 dari 3 pesanan tidak sebut harga → wajib bangun fallback dari database",
                "20–30 kata slang teratas cukup untuk normalisasi teks yang efektif",
                ">59% kuantitas ditulis teks → bangun konverter teks→angka sebelum masuk model",
            ],
            "Tindakan yang Disarankan" : [
                "Gunakan laporan ChatKasir sebagai panduan belanja bahan mingguan",
                "Buat paket bundling 2–3 produk dengan satu harga menarik",
                "Uji model secara intensif dengan data Pola 1 & 2 terlebih dahulu",
                "Tambahkan endpoint fallback harga di API back-end",
                "Prioritaskan 30 kata teratas di kamus normalisasi AI-2",
                "Daftarkan: setengah=0.5, seporsi=1, segelas=1, sepiring=1 dst.",
            ],
        }
        st.dataframe(
            pd.DataFrame(insight_data),
            use_container_width=True,
            hide_index=True,
        )
# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 6 — HALAMAN 3: SIMULASI CHATKASIR
# ══════════════════════════════════════════════════════════════════════════════

elif halaman == "💬 Simulasi ChatKasir":

    st.title("💬 Simulasi Ekstraksi Pesanan")
    st.caption(
        "Tempel teks obrolan pelanggan di bawah ini. "
        "Sistem akan mengekstrak nama produk, jumlah, dan harga secara otomatis."
    )

    # ── Layout dua kolom ──────────────────────────────────────────────────────
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("✍️ Teks Obrolan Pelanggan")

        contoh_teks = (
            "kak pesen 2 nasi goreng spesial sama 1 es teh manis ya, "
            "bisa minta totalnya berapa?"
        )

        teks_input = st.text_area(
            label="Ketik atau tempel teks di sini:",
            value=contoh_teks,
            height=200,
            placeholder="Contoh: pesen 3 mie ayam sama 2 es jeruk kak...",
            label_visibility="collapsed",
        )

        with st.expander("💡 Tips format teks yang optimal"):
            st.markdown(
                """
                - Teks percakapan dari WhatsApp bisa langsung di-paste
                - Sistem mengenali kata gaul seperti **nasgor**, **pesen**, **minta**
                - Harga yang disebutkan seperti **39rb** atau **Rp 39.000** akan diekstrak
                - Untuk multi-produk, pastikan dipisah dengan **dan** atau **sama**
                """
            )

        tombol_proses = st.button(
            "🚀 Proses Teks Sekarang",
            type="primary",
            use_container_width=True,
        )

    with col_output:
        st.subheader("📤 Hasil Ekstraksi")

        if not tombol_proses:
            # Status awal sebelum tombol ditekan
            st.markdown(
                """
                <div style='
                    background:#f0f4f8;
                    border-radius:10px;
                    padding:40px;
                    text-align:center;
                    color:#888;
                    min-height:200px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                '>
                    ⬅️ Tekan tombol proses untuk melihat hasil ekstraksi
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:
            # Animasi spinner saat memproses
            with st.spinner("⚙️ Model sedang menganalisis teks..."):
                # ── PLACEHOLDER logika model ──────────────────────────────────
                # Nanti diganti dengan pemanggilan ke API model AI sesungguhnya.
                # Untuk sekarang, gunakan ekstraksi rule-based sederhana sebagai
                # demo agar kerangka ini bisa dikonfirmasi berjalan.
                import time
                time.sleep(1.2)   # simulasi latensi model

                # Normalisasi slang sederhana (rule-based demo)
                df_slang_sim = muat_data_slang()
                kamus_slang  = dict(zip(
                    df_slang_sim["slang"].str.lower(),
                    df_slang_sim["formal"].str.lower(),
                ))
                teks_norm = " ".join(
                    kamus_slang.get(w, w)
                    for w in teks_input.lower().split()
                )

                # Hasil dummy (akan diganti output model nyata)
                hasil_ekstraksi = {
                    "status"         : "sukses",
                    "teks_asli"      : teks_input.strip(),
                    "teks_ternormalisasi": teks_norm.strip(),
                    "entitas"        : [
                        {
                            "produk"  : "— (model belum terhubung)",
                            "jumlah"  : "—",
                            "harga"   : "—",
                        }
                    ],
                    "catatan"        : (
                        "Ini adalah output placeholder. "
                        "Hubungkan ke endpoint POST /predict milik AI-2 "
                        "untuk hasil ekstraksi nyata."
                    ),
                }

            # Tampilkan hasil dalam format JSON rapi
            st.success("✅ Ekstraksi selesai!")
            st.code(
                __import__("json").dumps(hasil_ekstraksi, ensure_ascii=False, indent=2),
                language="json",
            )

            # Tabel ringkasan hasil (jika model sudah terhubung nanti)
            st.markdown("**📋 Ringkasan Pesanan:**")
            st.dataframe(
                pd.DataFrame(hasil_ekstraksi["entitas"]),
                use_container_width=True,
                hide_index=True,
            )