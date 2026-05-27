import pandas as pd
import random

# ============================================================
# CHATKASIR - Data Engineering
# Author  : Muhammad Faradi Eka Damara (DS-1)
# Deskripsi: Rule-Based Generation dengan kontrol jumlah produk unik
#            (1000 food populer) + Fix: Diverse Patterns, Multi-Item,
#            Inner-Sentence Price Tag
# Changelog:
#   [FIX-1] Diversifikasi TEMPLATES_PEMBELI — tambah pola PRODUK-di-depan
#   [FIX-2] Fungsi generate_order_majemuk (Pola 4 / Multi-Item)
#   [FIX-3] Alokasi 20% data untuk Pola Majemuk di generate_dataset
#   [FIX-4] MODIFIER & QTY_STRING — noise/customization + ejaan qty (50:50)
#   [FIX-5] TEMPLATES_PEMBELI: pola pembeli sebut harga (B-PRICE di sisi pembeli)
#   [FIX-6] TEMPLATES_MAJEMUK: pola brutal tanpa kata hubung
#   [FIX-7] get_random_qty() dipakai di semua loop generate_dataset
# ============================================================

# ============================================================
# PRODUK MANUAL PER KATEGORI (populer, akan masuk prioritas)
# ============================================================
PRODUK_MANUAL = {
    'penyetan'        : [
        'ayam penyet', 'lele penyet', 'bebek penyet', 'tahu penyet',
        'tempe penyet', 'udang penyet', 'cumi penyet', 'ayam penyet sambal ijo',
        'lele penyet sambal bawang', 'bebek penyet sambal terasi',
    ],
    'nasi'            : [
        'nasi goreng', 'nasi uduk', 'nasi padang', 'nasi kuning',
        'nasi putih', 'nasi campur', 'nasi bakar', 'nasi kebuli',
        'nasi liwet', 'nasi goreng kampung', 'nasi goreng seafood',
        'nasi goreng spesial', 'nasi timbel', 'nasi pecel',
    ],
    'mie'             : [
        'mie ayam', 'mie goreng', 'mie rebus', 'bakmi goreng',
        'mie kuah', 'mie pangsit', 'mie ayam bakso', 'mie goreng seafood',
        'kwetiau goreng', 'kwetiau rebus', 'bihun goreng', 'bihun rebus',
    ],
    'bakso_soto'      : [
        'bakso', 'bakso urat', 'bakso malang', 'bakso gepeng',
        'soto ayam', 'soto betawi', 'soto lamongan', 'rawon',
        'sop buntut', 'sop ayam', 'coto makassar', 'konro',
    ],
    'gorengan_jajanan': [
        'tempe goreng', 'tahu goreng', 'pisang goreng', 'martabak',
        'martabak manis', 'martabak telur', 'risoles', 'pastel',
        'cireng', 'cilok', 'batagor', 'siomay', 'pempek',
        'kerupuk', 'tahu bulat', 'tahu crispy',
    ],
    'ayam'            : [
        'ayam goreng', 'ayam geprek', 'ayam bakar', 'fried chicken',
        'ayam crispy', 'ayam kremes', 'ayam rica rica', 'ayam kecap',
        'ayam sambal hijau', 'ayam sambal merah', 'ayam pop',
        'ayam bakar madu', 'chicken wings', 'ayam katsu',
    ],
    'seafood'         : [
        'udang goreng', 'cumi goreng', 'ikan bakar', 'ikan goreng',
        'udang saus tiram', 'cumi saus padang', 'kepiting saus',
        'ikan asam manis', 'udang tepung', 'kerang saus',
    ],
    'minuman_es'      : [
        'es teh', 'es jeruk', 'es campur', 'es buah',
        'es teh manis', 'es jeruk peras', 'es lemon tea',
        'es cincau', 'es kelapa muda', 'es cendol',
        'es dawet', 'es kopyor', 'jus alpukat', 'jus mangga',
        'jus jambu', 'jus semangka', 'jus wortel',
    ],
    'kopi_hangat'     : [
        'kopi susu', 'kopi hitam', 'americano', 'teh manis',
        'teh tarik', 'wedang jahe', 'wedang ronde', 'susu hangat',
        'coklat hangat', 'kopi tubruk', 'kopi gula aren',
        'cappuccino', 'latte', 'es kopi susu',
    ],
    'minuman_kekinian': [
        'boba', 'thai tea', 'taro', 'matcha latte',
        'brown sugar boba', 'cheese tea', 'es kopi susu gula aren',
        'kopi susu kekinian', 'green tea latte', 'strawberry tea',
        'lychee tea', 'passion fruit tea', 'mango smoothie',
    ],
}

# Bobot per kategori untuk seleksi produk populer dari dataset
BOBOT_KATEGORI = {
    'penyetan'        : 50,
    'nasi'            : 80,
    'mie'             : 60,
    'bakso_soto'      : 50,
    'gorengan_jajanan': 40,
    'ayam'            : 80,
    'seafood'         : 30,
    'minuman_es'      : 60,
    'kopi_hangat'     : 50,
    'minuman_kekinian': 40,
    'lainnya'         : 0,
}

# Proporsi alokasi produk per kategori (relatif terhadap bobot)
ALOKASI_KATEGORI = {
    'nasi'            : 0.16,
    'ayam'            : 0.16,
    'mie'             : 0.12,
    'minuman_es'      : 0.12,
    'kopi_hangat'     : 0.10,
    'bakso_soto'      : 0.10,
    'penyetan'        : 0.10,
    'minuman_kekinian': 0.08,
    'gorengan_jajanan': 0.08,
    'seafood'         : 0.06,
    'lainnya'         : 0.02,
}

SAPAAN = [
    # --- Sapaan Standar & Singkatan ---
    'bang', 'kak', 'kk', 'bg', 'mas', 'mbak', 'min', 'bu', 'pak', 'pakde', 'bude', 'aa', 'teh', '', 
    
    # --- Nama Orang Acak (Mencegah salah tebak tag PRICE/PROD) ---
    'budi', 'deni', 'andi', 'ani', 'siti', 'dewi', 'rudi', 'joko', 'reza', 'putri', 'bapak', 'ibu',
    
    # --- Istilah Gaul & Sapaan Chat Komunitas ---
    'gan', 'sis', 'bro', 'cuy', 'bos', 'juragan', 'admin', 'halo admin', 'p', 'ping', 'assalamualaikum', 'wr wb',
    
    # --- Penanda Waktu Real-Time ---
    'malam', 'siang', 'pagi', 'sore', 'subuh', 'hallo pagi', 'hallo sore', 'hallo malam'
]

PENUTUP = [
    # --- Tanpa Kata Penutup ---
    '', 
    
    # --- Partikel Penegas & Kata Seru Kasual ---
    'ya', 'dong', 'nih', 'tuh', 'loh', 'kok', 'deh', 'kah', 'saja', 'aja', 'doang',
    'yaaa', 'donggg', 'dehh', 'yah', 'dulu', 'ajaa',
    
    # --- Kombinasi Sapaan Akrab ---
    'kak', 'ya kak', 'dong kak', 'deh kak', 'ya bang', 'dong bang', 'deh bang',
    'ya mas', 'dong mas', 'deh mas', 'ya mbak', 'dong mbak', 'deh mbak',
    'ya min', 'dong min', 'deh min', 'pak', 'ya pak', 'bu', 'ya bu', 'gan', 'ya gan',
    
    # --- Penutup Berbasis Harapan / Kecepatan (Urgency Noise) ---
    'cepet ya', 'buruan ya', 'jangan lama', 'gercep ya', 'ditunggu', 'oke ditunggu',
    'langsung ya', 'sekarang ya', 'siap ditunggu', 'makasih', 'terima kasih',
    'suwun', 'matur suwun', 'thanks', 'thx ya'
]


# ============================================================
# [FIX BARU] Tambahan Noise/Modifier & QTY String
# ============================================================
MODIFIER = [
    # --- Tanpa Modifier ---
    '', 
    
    # --- Catatan Rasa & Level Pedas (Ekstrem) ---
    'level dewa', 'pedes mampus', 'gak pake bawang', 'esnya dikit aja', 'pedas sedang', 
    'anget aja', 'level 5', 'level 10', 'extra pedas', 'jangan pedes', 'pake sambel ijo',
    
    # --- Aturan Penyajian & Kemasan ---
    'dibungkus', 'makan sini', 'bawa pulang', 'bumbu pisah', 'paket', 'pack', 'pake kotak', 
    'porsi gede', 'porsi double', 'porsi kecil', 'setengah porsi', 'pisahin kuahnya',
    
    # --- Konteks Niat / Tujuan Acara ---
    'buat kantor', 'untuk anak saya', 'buat acara keluarga', 'buat arisan', 'buat buka puasa', 
    'titipan bos', 'buat makan siang', 'buat bekel sekolah',
    
    # --- Ungkapan Emosi / Kecepatan (Urgency Noise) ---
    'cepet ya', 'pake qris', 'tolong buruan', 'jangan lama ya', 'anter sekarang', 'santai aja',
    'yang kyk biasa', 'pake ojol', 'langsung proses ya'
]

QTY_STRING = [
    # --- Ejaan Angka Dasar (Sering Diketik Pembeli) ---
    'satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan', 'sepuluh',
    
    # --- Satuan Porsi & Bungkus Umum (Awalan 'Se-') ---
    'seporsi', 'sebungkus', 'setengah', 'setengah porsi', 'porsi gede', 'porsi jumbo', 'porsi kecil',
    
    # --- Satuan Wadah Makanan Populer (Dunia Nyata UMKM) ---
    'sebungkus', 'dua bungkus', 'tiga bungkus', 
    'seporsi', 'dua porsi', 'tiga porsi', 'lima porsi',
    'semangkok', 'dua mangkuk', 'lima mangkuk', 
    'sepiring', 'tiga piring', 'se-pack', 'dua pack', 'lima pack',
    'sebox', 'dua box', 'lima kotak', 'sepaket', 'dua paket',
    'semika', 'dua mika', 'se-thinwall', 'dua thinwall',
    
    # --- Satuan Wadah Minuman Populer (Es & Kopi) ---
    'segelas', 'dua gelas', 'tiga gelas', 
    'sebotol', 'dua botol', 'tiga botol',
    'secup', 'satu cup', 'dua cup', 'tiga cup', 'lima cup',
    'seplastik', 'dua plastik', 'sekotak', 'sedus'
]

def get_random_qty():
    """Fungsi untuk mix angka dan ejaan string (50:50)"""
    if random.random() < 0.5:
        return str(random.randint(1, 25))
    else:
        return random.choice(QTY_STRING)

def get_random_harga():
    """Fungsi mendistribusikan harga dari puluhan ribu hingga jutaan"""
    probabilitas = random.random()
    if probabilitas < 0.50:
        return random.randint(5, 99) * 1000       # 5.000 - 99.000
    elif probabilitas < 0.85:
        return random.randint(100, 999) * 1000    # 100.000 - 999.000
    else:
        return random.randint(1, 50) * 1000000     # 1.000.000 - 50.000.000

def format_price_text(price: int) -> str:
    # Membuat format pemisah ribuan titik Indonesia asli (cth: 15.000, 3.500.000)
    formatted_base = f"{price:,}".replace(",", ".")
    
    if price >= 1000000:
        formats = [
            f"{price // 1000000}jt",
            f"{price // 1000000} juta",
            formatted_base,
            f"rp{formatted_base}",
            f"rp {formatted_base}"
        ]
    else:
        formats = [
            f"{price // 1000}rb",
            f"{price // 1000}k",
            f"{price // 1000} ribu",
            formatted_base,
            f"rp{price // 1000}rb",
            f"rp {formatted_base}"
        ]
    return random.choice(formats)

# ============================================================
# [FIX-1] TEMPLATES_PEMBELI — Pola Dunia Nyata yang Sangat Liar
# ============================================================
TEMPLATES_PEMBELI = [
    # --- POLA LAMA: QTY di depan ---
    "{sapaan} {qty} {produk} {modifier} {penutup}",
    "{sapaan} mau pesen {qty} {produk} {modifier} {penutup}",
    "kak mau order {qty} {produk} {modifier} {penutup}",
    "minta {qty} {produk} {modifier} {penutup}",
    "{qty} {produk} {modifier} {penutup}",
    "pesan {qty} {produk} {modifier} {penutup}",
    "beli {qty} {produk} {modifier} {penutup}",
    "{sapaan} bisa pesan {qty} {produk} {modifier} {penutup}",
    "mau {qty} {produk} {modifier} {penutup}",
    "boleh pesan {qty} {produk} {modifier} {penutup}",

    # --- POLA BARU: PRODUK di depan (Mengatasi Posisi Terbalik) ---
    "{sapaan} order {produk} {modifier} {qty} {penutup}",
    "pesen {produk} nya {qty} {penutup}",
    "{sapaan} {produk} {modifier} {qty} {penutup}",
    "{produk} {qty} ya {sapaan}",
    "mau {produk} jumlahnya {qty} {penutup}",

    # --- POLA KASUAL / AKSI DUNIA NYATA ---
    "buatin {produk} {modifier} {qty} {penutup}",
    "bungkusin {qty} {produk} {modifier} {penutup}",
    "bikinin {produk} {qty} {modifier} {penutup}",
    "nitip {qty} {produk} {modifier} {penutup}",
    "{sapaan} masih ada {produk}? kalau ada mau {qty} {modifier} {penutup}",
    "{produk} {modifier} {qty} aja {penutup}",
    "{sapaan} {produk} {modifier} dibikin {qty} ya",
    
    # --- POLA PENGANTAR ---
    "mau pesen buat {qty} {produk} {modifier} {penutup}",
    "tolong siapin {qty} {produk} {modifier} {penutup}",
    "order {produk} {modifier} untuk {qty} {penutup}",
    "bikin {qty} {produk} {modifier} {penutup}",

    # --- POLA PEMBELI SEBUT HARGA ---
    "{sapaan} pesen {produk} {modifier} yang harganya {harga} {qty} {penutup}",
    "{sapaan} {produk} {qty}, beneran {harga} kan {penutup}",
    "mau {qty} {produk} {modifier} budget {harga} {penutup}",
    "{produk} {modifier} yang {harga} pesen {qty} {penutup}",
    "beli {produk} {harga} an {qty} {penutup}",
]

TEMPLATES_PENJUAL = [
    # --- POLA STANDAR ---
    "oke kak {produk} harganya {harga} totalnya {total}",
    "siap kak {produk} {harga} total {total} ya",
    "{produk} {harga} ya kak jadi {total}",
    "baik kak {produk} {harga} satuan totalnya {total}",
    "noted kak {produk} {harga} totalnya {total}",
    "oke {produk} harga {harga} total {total} ya kak",
    "siap {produk} {harga} totalnya {total} kak",

    # --- POLA NOTA / RINCIAN KASIR ---
    "rincian pesanan: {produk} ({harga}) jadi {total} ya kak",
    "pesanan masuk: {produk} x {harga} = {total}",
    "halo kak, pesanan {produk} seharga {harga} sudah kami proses, total bayar {total}",
    "total tagihan {total} untuk {produk} harga {harga} per item ya",
    "baik, {total} ya kak rinciannya {produk} harganya {harga}",
]

# ============================================================
# [FIX-1] TEMPLATES_TANPA_HARGA_PEMBELI 
# ============================================================
TEMPLATES_TANPA_HARGA_PEMBELI = [
    # --- POLA STANDAR ---
    "{sapaan} {qty} {produk} {modifier} {penutup}",
    "kak mau pesen {qty} {produk} {modifier} {penutup}",
    "minta {qty} {produk} {modifier} {penutup}",
    "{qty} {produk} {modifier} {penutup}",
    "pesan {qty} {produk} {modifier} {penutup}",

    # --- POLA PRODUK DI DEPAN ---
    "{sapaan} order {produk} {modifier} {qty} {penutup}",
    "pesen {produk} nya {qty} {penutup}",
    "{sapaan} {produk} {modifier} {qty} {penutup}",
    "mau {produk} jumlahnya {qty} {penutup}",

    # --- POLA SANGAT SINGKAT / AGGRESIF (Dunia Nyata) ---
    "{produk} {qty}",
    "{qty} {produk}",
    "{produk} {qty} {modifier}",
    "buatin {produk} {qty}",
    "bungkusin {qty} {produk}",
    "{sapaan} {produk} {qty} cepet ya",
]

TEMPLATES_TANPA_HARGA_PENJUAL = [
    "oke siap kak",
    "noted kak ditunggu ya",
    "oke kak pesanannya masuk ya",
    "siap kak",
    "baik kak",
    "oke noted",
    "pesanan sedang disiapkan",
    "oke, mohon ditunggu sebentar ya",
    "siap, segera diproses",
    "baik, langsung kami buatkan",
    "", "", "" # Sengaja diperbanyak string kosong agar model terbiasa dengan chat yang tidak dibalas kasir
]

# ============================================================
# [FIX-2] TEMPLATES PESANAN MAJEMUK (Multi-Item)
# ============================================================
TEMPLATES_MAJEMUK_PEMBELI = [
    # --- POLA STANDAR / KATA HUBUNG ---
    "{sapaan} pesen {qty1} {produk1} dan {qty2} {produk2} {penutup}",
    "{sapaan} {produk1} {qty1} sama {produk2} {qty2} {penutup}",
    "order {qty1} {produk1}, terus {produk2} nya {qty2} {penutup}",
    "{produk1} {qty1} bungkus dan {qty2} {produk2} {penutup}",
    "{sapaan} mau {qty1} {produk1} sama {qty2} {produk2} {penutup}",
    
    # --- POLA BRUTAL / TANPA KATA HUBUNG ---
    "{produk1} {modifier} {qty1}, {produk2} {qty2} {penutup}",
    "pesan {qty1} {produk1} {qty2} {produk2} {penutup}",
    "{qty1} {produk1} {qty2} {produk2}",
    "{produk1} {qty1} {produk2} {qty2}",
    
    # --- POLA PLUS / SIMBOL ---
    "{sapaan} {qty1} {produk1} + {qty2} {produk2} {penutup}",
    "{produk1} {qty1} + {produk2} {qty2} ya",
    "mau {qty1} {produk1} tambah {qty2} {produk2} {penutup}",
    
    # --- POLA SEKALIAN (Khas Indonesia) ---
    "aku pesen {qty1} {produk1} sekalian {produk2} {qty2} ya",
    "pesan {produk1} {qty1} {modifier}, oh iya sekalian {produk2} {qty2} ya",
]

TEMPLATES_MAJEMUK_PENJUAL = [
    # --- POLA STANDAR ---
    "oke kak {produk1} {qty1} dan {produk2} {qty2}, totalnya {total_semua}",
    "siap kak, {produk1} {harga1} dan {produk2} {harga2}, jadi total {total_semua} ya",
    "noted kak {produk1} {qty1} {harga1} sama {produk2} {qty2} {harga2}, total {total_semua}",
    
    # --- POLA MATEMATIKA / STRUKTURAL ---
    "baik kak, {qty1} {produk1} ({harga1}) + {qty2} {produk2} ({harga2}) = {total_semua} ya",
    "pesanan: {produk1} {harga1}, {produk2} {harga2}. Total bayar = {total_semua}",
    "siap. {produk1} {harga1} & {produk2} {harga2}. total semuanya {total_semua} kak",
]

# ============================================================
# LOAD DATASET
# ============================================================
def load_datasets(food_path, slang_path):
    df_food  = pd.read_csv(food_path)
    df_slang = pd.read_csv(slang_path)

    food_list  = df_food['name'].dropna().str.lower().str.strip().tolist()
    slang_dict = dict(zip(
        df_slang['slang'].str.lower().str.strip(),
        df_slang['formal'].str.lower().str.strip()
    ))

    formal_to_slang = {}
    for slang, formal in slang_dict.items():
        if formal not in formal_to_slang:
            formal_to_slang[formal] = []
        formal_to_slang[formal].append(slang)

    return food_list, slang_dict, formal_to_slang

# ============================================================
# FILTER PRODUK DARI FOOD_UTAMA PER KATEGORI
# ============================================================
def filter_produk_dari_dataset(food_list):
    kata_kunci = {
        'penyetan'        : ['penyet'],
        'nasi'            : ['nasi'],
        'mie'             : ['mie', 'bakmi', 'kwetiau', 'bihun'],
        'bakso_soto'      : ['bakso', 'soto', 'rawon', 'sop', 'coto', 'konro'],
        'gorengan_jajanan': ['goreng', 'martabak', 'risoles', 'pastel', 'cireng',
                             'cilok', 'batagor', 'siomay', 'pempek'],
        'ayam'            : ['ayam', 'chicken'],
        'seafood'         : ['udang', 'cumi', 'ikan', 'kepiting', 'kerang'],
        'minuman_es'      : ['es ', 'jus'],
        'kopi_hangat'     : ['kopi', 'teh', 'wedang', 'susu'],
        'minuman_kekinian': ['boba', 'thai', 'matcha', 'taro', 'latte', 'smoothie'],
    }

    produk_per_kategori = {k: [] for k in kata_kunci}
    produk_lainnya      = []

    for produk in food_list:
        masuk_kategori = False
        for kategori, keywords in kata_kunci.items():
            if any(kw in produk for kw in keywords):
                produk_per_kategori[kategori].append(produk)
                masuk_kategori = True
                break
        if not masuk_kategori:
            produk_lainnya.append(produk)

    return produk_per_kategori, produk_lainnya

# ============================================================
# GABUNGKAN PRODUK MANUAL + DARI DATASET
# ============================================================
def gabungkan_produk(produk_per_kategori, produk_lainnya):
    gabungan = {}
    for kategori, produk_dataset in produk_per_kategori.items():
        produk_manual  = PRODUK_MANUAL.get(kategori, [])
        gabungan[kategori] = list(set(produk_dataset + produk_manual))
    gabungan['lainnya'] = produk_lainnya
    return gabungan

# ============================================================
# SELEKSI N PRODUK POPULER
# ============================================================
def seleksi_produk_populer(gabungan, n_target):
    selected = []
    sisa = n_target

    for kategori, proporsi in ALOKASI_KATEGORI.items():
        if sisa <= 0:
            break

        pool       = gabungan.get(kategori, [])
        manual     = list(set(PRODUK_MANUAL.get(kategori, [])))
        dari_ds    = [p for p in pool if p not in manual]

        kuota = max(1, round(n_target * proporsi))
        kuota = min(kuota, sisa)

        ambil = []
        ambil += manual[:kuota]
        if len(ambil) < kuota:
            sisa_kuota = kuota - len(ambil)
            random.shuffle(dari_ds)
            ambil += dari_ds[:sisa_kuota]

        ambil = [p for p in ambil if p not in selected]
        selected += ambil
        sisa -= len(ambil)

    if sisa > 0:
        lainnya = [p for p in gabungan.get('lainnya', []) if p not in selected]
        random.shuffle(lainnya)
        selected += lainnya[:sisa]

    selected = list(dict.fromkeys(selected))[:n_target]
    print(f"  Produk terpilih: {len(selected)} (target: {n_target})")
    return selected

# ============================================================
# BUAT WEIGHTED LIST DARI PRODUK TERPILIH
# ============================================================
def buat_weighted_list_dari_selected(selected_products, gabungan):
    produk_ke_kategori = {}
    for kategori, produk_list in gabungan.items():
        for p in produk_list:
            if p not in produk_ke_kategori:
                produk_ke_kategori[p] = kategori

    weighted_list = []
    for produk in selected_products:
        kategori = produk_ke_kategori.get(produk, 'lainnya')
        bobot    = BOBOT_KATEGORI.get(kategori, 10)
        bobot    = max(bobot, 10)
        weighted_list.extend([produk] * bobot)

    return weighted_list

# ============================================================
# FORMAT HARGA
# ============================================================
def format_price_text(price: int) -> str:
    formats = [
        f"{price // 1000}rb",
        f"{price // 1000}k",
        f"{price // 1000} ribu",
        f"{price // 1000}.000",
        f"rp{price // 1000}rb",
        f"rp {price // 1000}.000",
    ]
    return random.choice(formats)

# ============================================================
# APPLY SLANG
# ============================================================
def apply_slang(text: str, formal_to_slang: dict) -> str:
    words  = text.split()
    result = []
    for word in words:
        word_lower = word.lower()
        if word_lower in formal_to_slang and random.random() < 0.4:
            result.append(random.choice(formal_to_slang[word_lower]))
        else:
            result.append(word)
    return " ".join(result)

# ============================================================
# GENERATE SATU BARIS (POLA 1-3)
# ============================================================
def generate_order_dengan_harga(produk, qty, price, pattern):
    sapaan   = random.choice(SAPAAN)
    penutup  = random.choice(PENUTUP)
    modifier = random.choice(MODIFIER)  # [FIX BARU] inject modifier/noise
    harga    = format_price_text(price)
    # Qty bisa berupa int (untuk kalkulasi total) atau string ejaan
    qty_int  = qty if isinstance(qty, int) else 1  # fallback qty_int untuk total
    total    = format_price_text(price * qty_int)
    pembeli  = random.choice(TEMPLATES_PEMBELI).format(
        sapaan=sapaan, qty=qty, produk=produk, penutup=penutup,
        modifier=modifier, harga=harga
    ).strip()
    penjual  = random.choice(TEMPLATES_PENJUAL).format(
        produk=produk, harga=harga, total=total
    ).strip()
    return {
        "input_text"   : f"{pembeli} [SEP] {penjual}",
        "product"      : produk,
        "quantity"     : qty,
        "price_satuan" : price,
        "pattern"      : pattern,
    }

def generate_order_tanpa_harga(produk, qty, pattern):
    sapaan   = random.choice(SAPAAN)
    penutup  = random.choice(PENUTUP)
    modifier = random.choice(MODIFIER)  # [FIX BARU] inject modifier/noise
    pembeli  = random.choice(TEMPLATES_TANPA_HARGA_PEMBELI).format(
        sapaan=sapaan, qty=qty, produk=produk, penutup=penutup, modifier=modifier
    ).strip()
    penjual    = random.choice(TEMPLATES_TANPA_HARGA_PENJUAL)
    input_text = f"{pembeli} [SEP] {penjual}" if penjual else pembeli
    return {
        "input_text"   : input_text,
        "product"      : produk,
        "quantity"     : qty,
        "price_satuan" : -1,
        "pattern"      : pattern,
    }

# ============================================================
# [FIX-2] GENERATE PESANAN MAJEMUK (POLA 4 — 2 PRODUK SEKALIGUS)
# ============================================================
def generate_order_majemuk(produk1, qty1, price1, produk2, qty2, price2):
    sapaan   = random.choice(SAPAAN)
    penutup  = random.choice(PENUTUP)
    modifier = random.choice(MODIFIER)  # [FIX BARU] inject modifier/noise

    harga1      = format_price_text(price1)
    harga2      = format_price_text(price2)
    qty1_int    = qty1 if isinstance(qty1, int) else 1
    qty2_int    = qty2 if isinstance(qty2, int) else 1
    total_semua = format_price_text((price1 * qty1_int) + (price2 * qty2_int))

    pembeli = random.choice(TEMPLATES_MAJEMUK_PEMBELI).format(
        sapaan=sapaan, qty1=qty1, produk1=produk1,
        qty2=qty2, produk2=produk2, penutup=penutup, modifier=modifier
    ).strip()

    penjual = random.choice(TEMPLATES_MAJEMUK_PENJUAL).format(
        produk1=produk1, qty1=qty1, harga1=harga1,
        produk2=produk2, qty2=qty2, harga2=harga2, total_semua=total_semua
    ).strip()

    return {
        "input_text"   : f"{pembeli} [SEP] {penjual}",
        "product"      : f"{produk1} & {produk2}",
        "quantity"     : f"{qty1} & {qty2}",
        "price_satuan" : -1,
        "pattern"      : 4,
    }

# ============================================================
# [FIX-3] MAIN GENERATE — integrasi Pola 4 dengan alokasi 20%
# Rasio lama dikurangi proporsional agar total tetap = target_rows
# ============================================================
def generate_dataset(weighted_list, formal_to_slang, target_rows,
                     ratio_pola_1, ratio_pola_2, ratio_pola_3, ratio_no_harga):
    rows = []

    # Alokasi 20% untuk data majemuk; sisa 80% dibagi ke pola lama secara proporsional
    ratio_majemuk  = 0.20
    ratio_remaining = 1.0 - ratio_majemuk   # 0.80

    # Normalisasi rasio pola lama agar akumulasinya = 0.80 (bukan 1.00)
    ratio_lama_total = ratio_pola_1 + ratio_pola_2 + ratio_pola_3 + ratio_no_harga
    n_pola1    = int(target_rows * (ratio_pola_1   / ratio_lama_total) * ratio_remaining)
    n_pola2    = int(target_rows * (ratio_pola_2   / ratio_lama_total) * ratio_remaining)
    n_pola3    = int(target_rows * (ratio_pola_3   / ratio_lama_total) * ratio_remaining)
    n_no_harga = int(target_rows * (ratio_no_harga / ratio_lama_total) * ratio_remaining)
    n_majemuk  = int(target_rows * ratio_majemuk)

    # Koreksi sisa akibat pembulatan int() agar total tepat = target_rows
    n_generated = n_pola1 + n_pola2 + n_pola3 + n_no_harga + n_majemuk
    n_pola1    += (target_rows - n_generated)   # tambahkan selisih ke pola terbesar

    print(f"  Alokasi baris: P1={n_pola1} | P2={n_pola2} | P3={n_pola3} "
          f"| NoHarga={n_no_harga} | Majemuk={n_majemuk} | "
          f"Total={n_pola1+n_pola2+n_pola3+n_no_harga+n_majemuk}")

    print("  Generating Pola 1...")
    for _ in range(n_pola1):
        rows.append(generate_order_dengan_harga(
            random.choice(weighted_list), get_random_qty(),
            get_random_harga(), pattern=1
        ))

    print("  Generating Pola 2...")
    for _ in range(n_pola2):
        rows.append(generate_order_dengan_harga(
            random.choice(weighted_list), get_random_qty(),
            get_random_harga(), pattern=2
        ))

    print("  Generating Pola 3 (slang)...")
    for _ in range(n_pola3):
        row = generate_order_dengan_harga(
            random.choice(weighted_list), get_random_qty(),
            get_random_harga(), pattern=3
        )
        row["input_text"] = apply_slang(row["input_text"], formal_to_slang)
        rows.append(row)

    print("  Generating baris tanpa harga...")
    for _ in range(n_no_harga):
        rows.append(generate_order_tanpa_harga(
            random.choice(weighted_list), get_random_qty(),
            pattern=random.choice([1, 2, 3])
        ))

    # [FIX-2 + FIX-3] Pola 4 — Majemuk / Multi-Item
    print("  Generating Pola 4 (Majemuk / Multi-Item)...")
    for _ in range(n_majemuk):
        p1 = random.choice(weighted_list)
        p2 = random.choice(weighted_list)
        # Proteksi: pastikan dua produk berbeda dalam satu baris
        while p1 == p2:
            p2 = random.choice(weighted_list)
        
        rows.append(generate_order_majemuk(
            p1, get_random_qty(), get_random_harga(),
            p2, get_random_qty(), get_random_harga() 
        ))

    random.shuffle(rows)
    return rows

# ============================================================
# MAIN — hanya generate chatkasir_synthetic.csv
# ============================================================
if __name__ == "__main__":
    import os

    FOOD_PATH  = 'data\\final\\food_utama.csv'
    SLANG_PATH = 'data\\final\\slang_utama.csv'
    OUTPUT_DIR = 'data\\script-based'

    RANDOM_SEED    = 42
    RATIO_POLA_1   = 0.3325
    RATIO_POLA_2   = 0.3325
    RATIO_POLA_3   = 0.165
    RATIO_NO_HARGA = 0.175

    N_UNIQUE    = 1000
    TARGET_ROWS = 100000

    random.seed(RANDOM_SEED)

    print("Loading datasets...")
    food_list, slang_dict, formal_to_slang = load_datasets(FOOD_PATH, SLANG_PATH)
    print(f"Food list   : {len(food_list)} produk")
    print(f"Slang dict  : {len(slang_dict)} entri")

    print("\nMemfilter dan menggabungkan produk per kategori...")
    produk_per_kategori, produk_lainnya = filter_produk_dari_dataset(food_list)
    gabungan = gabungkan_produk(produk_per_kategori, produk_lainnya)

    print("\nJumlah produk per kategori (total pool):")
    for kategori, produk in gabungan.items():
        print(f"  {kategori:20s}: {len(produk)} produk")

    print(f"\n{'='*60}")
    print(f"SELEKSI {N_UNIQUE} PRODUK UNIK POPULER")
    print(f"{'='*60}")

    random.seed(RANDOM_SEED)
    selected_products = seleksi_produk_populer(gabungan, N_UNIQUE)
    weighted_list     = buat_weighted_list_dari_selected(selected_products, gabungan)

    print(f"  Total weighted list: {len(weighted_list)} entri")
    print(f"  Contoh produk terpilih (10 pertama): {selected_products[:10]}")

    print(f"\n  --- Generating {TARGET_ROWS} baris ({N_UNIQUE} produk unik) ---")
    random.seed(RANDOM_SEED)
    rows = generate_dataset(
        weighted_list, formal_to_slang, TARGET_ROWS,
        RATIO_POLA_1, RATIO_POLA_2, RATIO_POLA_3, RATIO_NO_HARGA
    )
    df = pd.DataFrame(rows)

    # Verifikasi
    # Untuk produk unik: pisahkan Pola 4 (majemuk "A & B") agar tidak
    # dihitung sebagai entitas baru — pecah lalu flatten untuk akurasi hitungan
    df_single   = df[df['pattern'] != 4]
    df_majemuk  = df[df['pattern'] == 4]
    produk_majemuk_flat = set()
    for val in df_majemuk['product']:
        for p in val.split(' & '):
            produk_majemuk_flat.add(p.strip())
    produk_unik_efektif = len(set(df_single['product'].unique()) | produk_majemuk_flat)

    print(f"\n  === HASIL {TARGET_ROWS} rows | {N_UNIQUE} produk unik ===")
    print(f"  Total baris              : {len(df)}")
    print(f"  Produk unik (efektif)    : {produk_unik_efektif} (target: {N_UNIQUE})")
    print(f"  Distribusi pattern       :\n{df['pattern'].value_counts().sort_index().to_string()}")
    print(f"  Baris Pola 4 (majemuk)   : {len(df_majemuk)}")
    print(f"  Baris tanpa harga total  : {(df['price_satuan'] == -1).sum()}")
    print(f"  Top 5 produk terbanyak (single):")
    print(df_single['product'].value_counts().head(5).to_string())
    print(f"  Preview:\n{df[['input_text','product','quantity','price_satuan','pattern']].head(5).to_string()}")

    FINAL_DIR = 'data\\final'
    FNAME     = 'chatkasir_synthetic.csv'
 
    # Simpan ke folder script-based (lokal)
    path_local = os.path.join(OUTPUT_DIR, FNAME)
    df.to_csv(path_local, index=False)
    print(f"\n  Tersimpan -> {path_local}")
 
    # Simpan salinan ke folder final
    os.makedirs(FINAL_DIR, exist_ok=True)
    path_final = os.path.join(FINAL_DIR, FNAME)
    df.to_csv(path_final, index=False)
    print(f"  Tersimpan -> {path_final}")
    
    print("\nSELESAI.")
