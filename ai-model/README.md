# AI-1 Model Architect — Achmad Rifan

Bagian ini berisi seluruh pekerjaan **AI-1 (Model Architect)**: perancangan arsitektur, *pipeline* pelatihan tingkat lanjut, dan evaluasi model Deep Learning NLP yang menjadi inti dari aplikasi ChatKasir.

> **Catatan:** Dokumen ini adalah **referensi utama** bagi seluruh anggota tim yang bekerja di area yang bersentuhan dengan model AI.

---

## Daftar Isi

1. [Struktur Folder & File](#struktur-folder--file)
2. [Pola Percakapan yang Ditangani Model](#pola-percakapan-yang-ditangani-model)
3. [Alur Pemrosesan Lengkap](#alur-pemrosesan-lengkap-dari-input-mentah-ke-dashboard)
4. [Arsitektur Model](#arsitektur-model-transformer--task-specific-branches)
5. [Custom Training & Evaluation Loop](#custom-training--evaluation-loop-tfgradienttape)
6. [Custom Loss Function & Optimasi Training](#custom-loss-function--optimasi-training)
7. [Format Kontrak Data](#format-kontrak-data-model-ke-api)

---

## Struktur Folder & File

```text
ai-model/
├── notebooks/
│   ├── 01_model_architecture.ipynb   # Eksperimen arsitektur Transformer
│   ├── 02_training.ipynb             # Proses training dengan Dynamic Weighting
│   └── 03_evaluation.ipynb           # Evaluasi metrik dan visualisasi
├── src/
│   ├── model.py                      # Fungsi arsitektur final
│   └── custom_loss.py              # Fungsi loss kustom
├── assets/
│   └── tokenizers/                   # File tokenizer Subword/BPE
├── logs/                             # Log TensorBoard untuk pemantauan
├── RESEARCH_NOTES.md                 # Catatan referensi ilmiah
├── pyproject.toml
├── uv.lock
├── .python-version
└── README.md
```

---

## Pola Percakapan yang Ditangani Model

Pengguna ChatKasir adalah penjual UMKM yang meng-*copy-paste* percakapan WhatsApp ke dalam aplikasi. Ada **3 pola percakapan nyata** yang mendefinisikan *scope* model dan acuan pembuatan dataset.

### Pola 1: Pesanan Sederhana 1 Produk

Satu produk, satu jumlah, dan harga satuan disebutkan secara eksplisit.

```text
[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya
[07.44, 22/4/2026] Penjual: oke kak, 1 nasi goreng harganya 10rb, jadi totalnya 20rb ya
```

### Pola 2: Multi-Produk dengan Harga Satuan Eksplisit

Pembeli memesan beberapa produk, direspons penjual dengan memecah harga. Sistem AI-2 (Denny) akan memisahkan iterasi setiap produk satu per satu sebelum masuk ke model.

```text
# Iterasi 1 — produk pertama
bang pesan 2 nasi goreng 2 es teh ya [SEP] nasi goreng harganya 10rb es tehnya 5rb totalnya 30rb
→ product: nasi goreng | quantity: 2 | price_satuan: 10000

# Iterasi 2 — produk kedua
bang pesan 2 nasi goreng 2 es teh ya [SEP] nasi goreng harganya 10rb es tehnya 5rb totalnya 30rb
→ product: es teh | quantity: 2 | price_satuan: 5000
```

### Pola 3: Chat Penuh Slang & Subword Tokenization

Merepresentasikan pembeli yang mengetik dengan *slang* atau *typo*.

| Langkah | Deskripsi | Contoh |
| :--- | :--- | :--- |
| **Normalisasi** | Koreksi singkatan umum menggunakan kamus dari DS-1 (Faradi) | `bg` → `abang`, `rb` → `ribu` |
| **Subword Tokenization** | Pecah kata aneh yang lolos normalisasi menjadi sub-bagian | `grngg` → `["gr", "##ngg"]` |

---

## Alur Pemrosesan Lengkap: Dari Input Mentah ke Dashboard

Bagian ini menjelaskan perjalanan data dengan contoh nyata, dari saat pengguna menekan tombol *paste* di aplikasi hingga angka transaksi muncul di *dashboard*, beserta batas tanggung jawab setiap anggota tim.

**Contoh Kasus:** Pembeli memesan dengan singkatan (*slang*) dan *typo* yang cukup parah.

---

### [1] Input dari Aplikasi
**Penanggung Jawab:** FS-1 Alfan

Pengguna melakukan *copy-paste* chat WhatsApp mentah ke dalam kotak teks di aplikasi.

```text
[07.42, 22/4/2026] Pembeli: bg psnnn nasgorrrr 2 yak
[07.44, 22/4/2026] Penjual: oke kak, 1 nasi goreng 10rb total 20rb
```

---

### [2] Preprocessing & Tokenization
**Penanggung Jawab:** AI-2 Denny & AI-1 Rifan

| Langkah | Proses | Hasil |
| :--- | :--- | :--- |
| **2a & 2b**: Hapus Timestamp & Ekstrak | Regex membuang metadata tanggal/waktu | `bg psnnn nasgorrrr 2 yak` `oke kak, 1 nasi goreng 10rb total 20rb` |
| **2c**: Normalisasi Slang | Kamus DS-1 (Faradi) memperbaiki singkatan | `abang pesanan nasgorrrr 2 iya` `oke kak 1 nasi goreng 10ribu total 20ribu` |
| **2d**: Subword Tokenization & `[SEP]` | Pecah kata aneh menjadi sub-token, gabungkan dengan separator | `["abang", "pesanan", "nas", "gor", "##rrr", "2", "iya", "[SEP]", "oke", "kak", "1", "nasi", "goreng", "10", "ribu", "total", "20", "ribu"]` |

---

### [3] Prediksi Model AI-1
**Penanggung Jawab:** AI-1 Rifan

Model menerima susunan *token* di atas, memprosesnya melalui arsitektur *Transformer* ke tiga cabang khusus, lalu mengembalikan nilai mentah.

```json
{
  "product_tags": ["O", "O", "B-PROD", "I-PROD", "I-PROD", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
  "quantity": 1.98,
  "price_satuan": 10000.45
}
```

---

### [4] Postprocessing
**Penanggung Jawab:** AI-2 Denny

Menerjemahkan *tag* NER kembali menjadi teks utuh (`"nasi goreng"`), membulatkan angka desimal, menghitung total prediksi (`quantity × price_satuan`), lalu memverifikasinya dengan teks total di chat asli.

```json
{
  "product": "nasi goreng",
  "quantity": 2,
  "price_satuan": 10000,
  "total": 20000,
  "confidence": "HIGH"
}
```

---

### [5] Simpan ke Database
**Penanggung Jawab:** FS-2 Reihan

Menerima JSON yang sudah rapi dari langkah [4] dan menyimpannya ke tabel transaksi di database PostgreSQL.

---

### [6] Tampilan Dashboard
**Penanggung Jawab:** FS-1 Alfan

Menyajikan data dari *database* ke layar penjual dalam bentuk antarmuka yang ramah pengguna.

| Produk | Jumlah | Harga Satuan | Total |
| :--- | :---: | ---: | ---: |
| nasi goreng | 2 | Rp10.000 | Rp20.000 |

---

## Arsitektur Model: Transformer + Task-Specific Branches

Model berevolusi dari *Shared Bi-LSTM* menjadi **Transformer Encoder** yang dilatih dari nol (*from scratch*). Pendekatan *Multi-Task Learning* dipertahankan, namun kini menggunakan **cabang spesifik** untuk mencegah entitas saling bertabrakan (*Task Interference*).

### 1. Shared Backbone: Transformer Encoder
Membaca seluruh kalimat secara bersamaan dengan mekanisme *Multi-Head Attention*, menciptakan ringkasan pemahaman konteks yang sangat kaya.

### 2. Task-Specific Branches: Tiga Cabang Khusus

| Cabang | Mekanisme | Deskripsi |
| :--- | :--- | :--- |
| **Product** | NER + CRF | Mengekstrak urutan kata (misal: `"nasi"` = `B-PROD`). CRF (*Conditional Random Field*) mencegah urutan *tag* yang tidak logis. |
| **Quantity** | Dense Regresi | Layer khusus yang berfokus memprediksi angka kontinu positif. |
| **Price** | Dense Regresi | Layer khusus yang berfokus memprediksi harga *satuan* (dinormalisasi ÷1000 saat training). |

---

## Custom Training & Evaluation Loop (tf.GradientTape)

Berbeda dengan model standar yang menggunakan fungsi otomatis `model.fit()`, ChatKasir menggunakan **Custom Training Loop** penuh untuk memberikan kendali total atas proses belajar model. Hal ini krusial karena kompleksitas arsitektur kita yang memiliki tiga *output* berbeda.

### Mengapa Menggunakan tf.GradientTape?
* **Kontrol Multi-Task:** Memungkinkan kita mengatur bagaimana *loss* dari cabang Produk, Jumlah, dan Harga digabungkan secara presisi sebelum memperbaiki bobot model.
* **Dynamic Loss Weighting:** Mempermudah penerapan algoritma yang menyeimbangkan prioritas belajar antar cabang secara otomatis di setiap *epoch*.
* **Efisiensi Masked Loss:** Memastikan fungsi `MaskedPriceLoss` terintegrasi sempurna dalam perhitungan gradien, sehingga model benar-benar mengabaikan data harga yang tidak valid (`-1`).

### Logika Siklus Pelatihan:
1.  **Forward Pass:** Model menerima input teks dan mengeluarkan tiga prediksi (product, quantity, price_satuan) secara bersamaan.
2.  **Recording:** tf.GradientTape bertindak sebagai "perekam" yang mencatat semua operasi matematika yang terjadi saat model membuat tebakan.
3.  **Loss Calculation:** Menghitung seberapa besar kesalahan model berdasarkan fungsi *loss* masing-masing cabang.
4.  **Backpropagation:** Tape "memutar balik" rekaman untuk menghitung gradien (arah perbaikan) bagi setiap saraf/bobot dalam model.
5.  **Optimization:** *Optimizer* (Adam) menggunakan nilai gradien tersebut untuk memperbarui bobot model agar tebakan berikutnya lebih akurat.

> **Catatan Teknis:** Seluruh logika ini diimplementasikan dalam fungsi kustom `train_step()` dan `val_step()` yang dapat ditemukan di `src/model.py` atau `notebooks/02_training.ipynb`.

---

## Custom Loss Function & Optimasi Training

Karena sifat matematika dari setiap tugas berbeda, *loss function* yang digunakan pun berbeda agar model tidak dihukum secara keliru.

| Cabang | Loss Function | Alasan |
| :--- | :--- | :--- |
| **Product** | Categorical Crossentropy / CRF Loss | Mengukur akurasi *sequence tagging* kata per kata. Keyakinan yang salah dihukum keras. |
| **Quantity** | Mean Squared Error (MSE) | Menghukum error besar secara tidak proporsional (dikuadratkan). Selisih tebakan "10 porsi" untuk pesanan "2 porsi" sangat merusak. |
| **Price** | **MaskedPriceLoss (Custom)** | **Wajib dipertahankan.** Mengabaikan baris bernilai `-1` (harga tidak disebutkan di chat). Jika MSE standar dipakai, model akan belajar keliru menebak angka `-1`. |

> **Optimasi Tambahan:** Diterapkan **Dynamic Loss Weighting** agar saat proses *training*, model memberikan porsi perhatian yang seimbang antara memprediksi Produk, Jumlah, dan Harga — tanpa ada cabang yang mendominasi.

---

## Format Kontrak Data: Model ke API

Output model final (sebelum masuk tahap postprocessing AI-2):

```json
{
  "product_tags": ["B-PROD", "I-PROD", "O", "O"],
  "quantity": 1.98,
  "price_satuan": 10000.45
}
```

> **Catatan untuk AI-2 (Denny):** Konversi `product_tags` kembali menjadi string utuh, dan lakukan pembulatan integer pada `quantity` serta `price_satuan` saat memformulasikan response akhir ke Backend.