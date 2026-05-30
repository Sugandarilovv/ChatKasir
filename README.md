# DS1-Data — Muhammad Faradi Eka Damara

Dataset dan pipeline data engineering untuk proyek **ChatKasir** — sistem NLP berbasis kasir warung makan yang mampu mengekstrak entitas pesanan (produk, kuantitas, harga) dari percakapan chat berbahasa Indonesia sehari-hari.

---

## Struktur Direktori

```
data/
├── raw/                        # Dataset mentah dari sumber eksternal
│   ├── food_gofood_raw.csv         # Data makanan dari GoFood (Kaggle)
│   ├── food_indonesian_raw.csv     # Data makanan Indonesia (HuggingFace)
│   ├── slang_indonesia_raw.csv     # Kamus slang Indonesia (HuggingFace)
│   └── slang_theonlydo_raw.csv     # Kamus slang alternatif (HuggingFace)
│
├── final/                      # Dataset bersih siap pakai
│   ├── food_utama.csv              # 18.558 nama makanan/minuman baku
│   ├── slang_utama.csv             # 1.231 pasangan slang ↔ formal
│   └── chatkasir_synthetic.csv     # 100.000 data sintetis percakapan kasir
│
├── data-dictionary/            # Dokumentasi skema kolom
│   ├── data_dictionary_food.csv
│   ├── data_dictionary_slang.csv
│   └── data_dictionary_synthetic.csv
│
├── scripts/                    # Script eksplorasi & asesmen kualitas data
│   ├── explore_food.py
│   ├── explore_slang.py
│   ├── assessing_food.py
│   ├── assessing_slang.py
│   ├── assessing_synthetic.py
│   ├── generate_data_dictionary.py
│   └── laporan_kualitas_data.ipynb
│
└── script-based/               # Script generasi data & analisis ringkasan
    ├── generate_data.py            # Generator utama data sintetis (rule-based)
    ├── analisis_dataset.py         # Analisis statistik dataset
    ├── analisis_ringkasan.csv      # Ringkasan statistik hasil generate
    ├── analisis_top100_chatkasir.csv
    └── chatkasir_synthetic.csv     # Salinan dataset untuk analisis
```

---

## Dataset

### `food_utama.csv`
Daftar nama makanan dan minuman Indonesia dalam huruf kecil.

| Kolom | Tipe | Jumlah Baris | Deskripsi |
|-------|------|-------------|-----------|
| `name` | string | 18.558 | Nama makanan/minuman, panjang 1–5 kata |

**Sumber:** Gabungan dari [eriko-syah/indonesian-food](https://huggingface.co/datasets/eriko-syah/indonesian-food) (HuggingFace) dan [ariqsyahalam/indonesia-food-delivery-gofood-product-list](https://www.kaggle.com/datasets/ariqsyahalam/indonesia-food-delivery-gofood-product-list) (Kaggle).

---

### `slang_utama.csv`
Kamus normalisasi teks: pasangan kata slang/singkatan dengan bentuk formalnya.

| Kolom | Tipe | Jumlah Baris | Deskripsi |
|-------|------|-------------|-----------|
| `slang` | string | 1.231 | Kata slang/singkatan chat WhatsApp, semua huruf kecil |
| `formal` | string | 1.231 | Bentuk baku dari kata slang (552 nilai unik) |

**Sumber:** Gabungan dari [nahiar/indonesia-slang](https://huggingface.co/datasets/nahiar/indonesia-slang) dan [theonlydo/indonesia-slang](https://huggingface.co/datasets/theonlydo/indonesia-slang) (HuggingFace).

**Kegunaan:** Dipakai oleh AI-2 (Denny) sebagai kamus normalisasi teks sebelum diproses model NER.

---

### `chatkasir_synthetic.csv`
Dataset utama: 100.000 percakapan sintetis antara pembeli dan penjual warung makan, dilabeli untuk task Named Entity Recognition (NER).

| Kolom | Tipe | Jumlah Baris | Deskripsi |
|-------|------|-------------|-----------|
| `input_text` | string | 100.000 | Teks percakapan `<pembeli> [SEP] <penjual>` |
| `product` | string | 100.000 | Nama produk yang dipesan (target NER) |
| `quantity` | string | 100.000 | Jumlah pesanan (angka atau satuan string) |
| `price_satuan` | integer | 100.000 | Harga satuan dalam rupiah; `-1` = tidak disebutkan |
| `pattern` | integer | 100.000 | Pola kalimat yang digunakan (1–4) |

**Format `input_text`:**
```
<teks_pembeli> [SEP] <teks_penjual>
```
Baris tanpa token `[SEP]` berarti pesanan tanpa konfirmasi harga dari penjual.

**Pola Kalimat (`pattern`):**

| Pattern | Deskripsi |
|---------|-----------|
| 1 | Satu produk, template standar QTY-di-depan dengan konfirmasi harga penjual |
| 2 | Satu produk, template PRODUK-di-depan atau variasi kasual (`buatin`, `bungkusin`, `nitip`) |
| 3 | Input mengandung slang dan typo berat (`apply_slang`), label tetap baku |
| 4 | Pesanan majemuk 2 produk sekaligus; `product` = `"produk1 & produk2"`, `price_satuan` = `-1` |

**Statistik Dataset:**

| Metrik | Nilai |
|--------|-------|
| Total baris | 100.000 |
| Pattern 1 | 31.017 (31%) |
| Pattern 2 | 31.183 (31,2%) |
| Pattern 3 (slang) | 17.800 (17,8%) |
| Pattern 4 (majemuk) | 20.000 (20%) |
| Baris tanpa harga (`price_satuan = -1`) | 33.930 (33,9%) |
| Baris dengan harga | 66.070 (66,1%) |
| Produk unik yang ter-generate | 1.000 dari 18.558 |
| QTY format angka | 40.046 |
| QTY format ejaan string | 39.954 |

**Distribusi harga:**
- 50% harga kecil (Rp 5.000 – Rp 99.000)
- 35% harga menengah (Rp 100.000 – Rp 999.000)
- 15% harga besar (Rp 1.000.000 – Rp 50.000.000) — mencakup katering & pesanan besar

---

## Pipeline Data

```
raw/ ──► scripts/explore_*.py ──► scripts/assessing_*.py
                                         │
                                         ▼
                                    final/food_utama.csv
                                    final/slang_utama.csv
                                         │
                                         ▼
                              script-based/generate_data.py
                                         │
                                         ▼
                              final/chatkasir_synthetic.csv (100.000 baris)
```

---

## Scripts

| Script | Deskripsi |
|--------|-----------|
| `scripts/explore_food.py` | Eksplorasi awal dataset makanan mentah |
| `scripts/explore_slang.py` | Eksplorasi awal dataset slang mentah |
| `scripts/assessing_food.py` | Asesmen kualitas data `food_utama.csv` |
| `scripts/assessing_slang.py` | Asesmen kualitas data `slang_utama.csv` |
| `scripts/assessing_synthetic.py` | Asesmen kualitas data sintetis |
| `scripts/generate_data_dictionary.py` | Generator otomatis data dictionary |
| `scripts/laporan_kualitas_data.ipynb` | Laporan kualitas data (Jupyter Notebook) |
| `script-based/generate_data.py` | Generator utama dataset sintetis (rule-based) |
| `script-based/analisis_dataset.py` | Analisis statistik dataset hasil generasi |

---

## Konteks Proyek

Dataset ini dibuat untuk melatih model NLP **ChatKasir** yang bertugas memahami pesan chat pembeli warung makan dan mengekstrak tiga entitas utama:

- **Produk** — nama makanan/minuman yang dipesan
- **Kuantitas** — jumlah pesanan
- **Harga** — harga satuan jika disebutkan

Data dirancang agar model tahan terhadap variasi input nyata: penggunaan slang, typo, satuan informal (`sebungkus`, `dua porsi`), dan pesanan majemuk dalam satu pesan.

---

## Author

**Muhammad Faradi Eka Damara** — DS-1
