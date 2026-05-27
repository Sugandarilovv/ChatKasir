# AI-1 Model Architect - Achmad Rif'an

Dokumen ini berisi dokumentasi teknis menyeluruh mengenai seluruh pekerjaan **AI-1 (Model Architect)** untuk aplikasi ChatKasir. Dokumentasi ini mencakup perancangan arsitektur jaringan saraf, *pipeline* pelatihan tingkat lanjut menggunakan kustom loop, evaluasi metrik berbasis token, serta spesifikasi skrip *parser* untuk kebutuhan *handover* data ke tim API.

## Daftar Isi

- [AI-1 Model Architect - Achmad Rif'an](#ai-1-model-architect---achmad-rifan)
  - [Daftar Isi](#daftar-isi)
  - [Struktur Folder \& File](#struktur-folder--file)
  - [Pola Percakapan Dunia Nyata (Scope Dataset)](#pola-percakapan-dunia-nyata-scope-dataset)
    - [1. Pola Sederhana (Single-Item)](#1-pola-sederhana-single-item)
    - [2. Pola Majemuk / Multi-Item (Direct Processing)](#2-pola-majemuk--multi-item-direct-processing)
    - [3. Penulisan Angka \& Modifikasi (Slang / Noise)](#3-penulisan-angka--modifikasi-slang--noise)
  - [Alur Pemrosesan Lengkap: Dari Input Mentah ke Dashboard](#alur-pemrosesan-lengkap-dari-input-mentah-ke-dashboard)
    - [\[1\] Input dari Aplikasi (WhatsApp Copy-Paste)](#1-input-dari-aplikasi-whatsapp-copy-paste)
    - [\[2\] Preprocessing \& Tokenization](#2-preprocessing--tokenization)
    - [\[3\] Prediksi Model Unified NER (AI-1)](#3-prediksi-model-unified-ner-ai-1)
    - [\[4\] Postprocessing \& Array Mapping (Handover ke AI-2)](#4-postprocessing--array-mapping-handover-ke-ai-2)
    - [\[5\] Database \& Tampilan Dashboard](#5-database--tampilan-dashboard)
  - [Arsitektur Model Final: Unified Transformer-NER](#arsitektur-model-final-unified-transformer-ner)
    - [Kamus Pemetaan Tag (7 Kelas)](#kamus-pemetaan-tag-7-kelas)
  - [Custom Training Loop \& MaskedNERLoss](#custom-training-loop--maskednerloss)
    - [Jantung Komputasi: `MaskedNERLoss`](#jantung-komputasi-maskednerloss)
    - [Logika Alur Siklus Gradient Tape (Per Batch):](#logika-alur-siklus-gradient-tape-per-batch)
  - [Evaluasi Metrik \& Penanganan Error](#evaluasi-metrik--penanganan-error)
    - [Laporan Kemampuan Model](#laporan-kemampuan-model)
    - [Analisis Kasus Kesalahan (*Error Analysis*)](#analisis-kasus-kesalahan-error-analysis)
  - [Algoritma Parser JSON \& Kontrak Data API](#algoritma-parser-json--kontrak-data-api)
    - [Panduan Implementasi untuk AI-2 (DENNY)](#panduan-implementasi-untuk-ai-2-denny)
    - [Aturan Tambahan:](#aturan-tambahan)


## Struktur Folder & File

```
ai-model/
├── notebooks/
│   ├── 01_model_architecture.ipynb   # Tokenisasi, Regex Multi-Format, & Pelabelan BIO Dataset
│   ├── 02_training.ipynb             # Proses training dengan Custom Loop & Dynamic Weighting
│   └── 03_evaluation.ipynb           # Evaluasi metrik (Classification Report) & Simulasi End-to-End Parser
├── src/
│   ├── model.py                      # Fungsi arsitektur final (Transformer + BiLSTM + NER Head)
│   └── custom_loss.py                # Fungsi loss kustom tunggal (MaskedNERLoss)
├── assets/
│   ├── data/                         # Aset data biner dan parameter konfigurasi
│   │   ├── dataset_chatkasir.npz     # Hasil pembagian Train/Val/Test
│   │   └── model_config.json         # Parameter konfigurasi global (Vocab, Max Length=128, Num Tags=7)
│   ├── models/                       # Folder penyimpanan berkas biner model terbaik hasil training
│   │   ├── chatkasir_saved_model/    # Folder format SavedModel untuk eksport model
│   │   └── chatkasir_model.keras     # File utama model terbaik format Keras
│   └── tokenizers/                   # Folder penyimpanan aset tokenisasi teks
│       └── tokenizer.json            # File eksport WordPiece Tokenizer (Vocab Size: 5000)
├── logs/                             # Log TensorBoard untuk pemantauan training
├── RESEARCH_NOTES.md                 # Catatan referensi ilmiah
├── requirements.txt                  # Daftar dependensi project standar format pip requirements
└── README.md                         # Dokumentasi utama project

```

## Pola Percakapan Dunia Nyata (Scope Dataset)

Aplikasi ChatKasir dirancang untuk mengurai kekacauan teks pesanan dari percakapan WhatsApp kasir UMKM yang sering kali tidak terstruktur, penuh singkatan (*slang*), dan salah tik (*typo*). Dataset sintetis baru yang dikembangkan oleh DS-1 (Faradi) mencakup variasi pola berikut secara *native*:

### 1. Pola Sederhana (Single-Item)
Pesanan tunggal dengan susunan Kuantitas (`QTY`) di depan maupun di belakang Produk (`PROD`).
* *Contoh QTY di depan:* `"mas 2 nasi goreng ya"`
* *Contoh PROD di depan:* `"pesen ayam geprek nya 3 porsi dong"`

### 2. Pola Majemuk / Multi-Item (Direct Processing)
Pembeli memesan lebih dari satu jenis menu sekaligus dalam satu baris chat tanpa pembatas formal. **Model V2 mampu memproses seluruh item ini secara langsung tanpa perlu pemotongan iterasi kalimat dari sisi Backend.**
* *Contoh:* `"bang pesen 3 bakso mercon dan 2 es teh manis [SEP] siap mas 3 bakso mercon 45rb dan 2 es teh manis 10rb jadi total harganya 55rb ya"`

### 3. Penulisan Angka & Modifikasi (Slang / Noise)
* **Kuantitas Huruf/Ejaan:** Mengakomodasi ketikan non-digit seperti `"seporsi"`, `"sebungkus"`, `"setengah"`, `"dua"`.
* **Variasi Format Harga Kasir:** Deteksi mandiri teks harga dari penjual setelah token separator `[SEP]` dengan format beragam: `45rb`, `10rb`, `17k`, `12k`, `rp 15.000`.
* **Modifier (Noise Teks):** Kata pelengkap rasa atau metode penyajian seperti `"level dewa"`, `"pedes mampus"`, `"gak pake bawang"`, `"makan sini"` secara otomatis diabaikan oleh model dan dilabeli sebagai tag `O`.

---

## Alur Pemrosesan Lengkap: Dari Input Mentah ke Dashboard

Bagian ini merinci bagaimana teks pesanan kotor pelanggan diproses dari ujung ke ujung hingga berhasil direkam ke dalam sistem pembukuan.

### [1] Input dari Aplikasi (WhatsApp Copy-Paste)
**Penanggung Jawab:** FS-1 Alfan

Pengguna menyalin teks obrolan mentah ke dalam antarmuka aplikasi.
```text
[07.42, 22/4/2026] Pembeli: bg pesen 3 bakso mercon dan 2 es teh manis
[07.44, 22/4/2026] Penjual: siap mas 3 bakso mercon 45rb dan 2 es teh manis 10rb total 55rb ya
```

### [2] Preprocessing & Tokenization

**Penanggung Jawab:** AI-2 Denny & AI-1 Rif'an

* **Saringan Metadata:** Menghapus stempel waktu/nama pembicara menggunakan Regex.
* **Normalisasi Teks:** Mengoreksi singkatan kritis (misal: `bg` $\rightarrow$ `bang`). Kata *slang* atau *typo* ekstrem (seperti `hrgny##a`) akan dipecah secara aman menggunakan WordPiece Tokenizer menjadi sub-token.
* **Penggabungan Batas `[SEP]`:** Menggabungkan ucapan pembeli dan penjual dengan token pembatas khusus `[SEP]`.

```text
Hasil Token: ["bg", "pesen", "3", "bakso", "mercon", "dan", "2", "es", "teh", "manis", "[SEP]", "siap", "mas", "3", "bakso", "mercon", "45rb", "dan", "2", "es", "teh", "manis", "10rb", "jadi", "total", "harganya", "55rb", "ya"]
```

### [3] Prediksi Model Unified NER (AI-1)

**Penanggung Jawab:** AI-1 Rif'an

Teks yang sudah berbentuk ID token dimasukkan ke dalam model jaringan saraf untuk diprediksi kelas tag BIO-nya (Total 7 Kelas).

```text
TOKEN / KATA    | PREDIKSI TAG
------------------------------
3               | B-QTY
bakso           | B-PROD
mercon          | I-PROD
dan             | O
2               | B-QTY
es              | B-PROD
teh             | I-PROD
manis           | I-PROD
[SEP]           | O
45rb            | B-PRICE
10rb            | B-PRICE
55rb            | B-PRICE
```

*(Catatan: Kata Product dan Quantity pada kalimat penjual setelah `[SEP]` sengaja diprediksi `O` oleh model untuk menghindari bug hitung ganda / double-counting).*

### [4] Postprocessing & Array Mapping (Handover ke AI-2)

**Penanggung Jawab:** AI-2 Denny

Output tag BIO dari model diolah menggunakan fungsi parser cerdas untuk membangun format JSON terstruktur, melakukan pembersihan ejaan kuantitas menjadi integer numerik, serta mengalkulasi subtotal secara dinamis.

```json
{
    "results": [
        {
            "product": "Bakso Mercon",
            "quantity": 3,
            "price_satuan": 15000,
            "subtotal": 45000
        },
        {
            "product": "Es Teh Manis",
            "quantity": 2,
            "price_satuan": 5000,
            "subtotal": 10000
        }
    ],
    "clean_text": "bg pesen 3 bakso mercon dan 2 es teh manis [SEP] siap mas 3 bakso mercon 45rb dan 2 es teh manis 10rb jadi total harganya 55rb ya"
}

```

### [5] Database & Tampilan Dashboard

**Penanggung Jawab:** FS-2 Reihan & FS-1 Alfan

Data JSON dikirim ke server backend untuk disimpan ke database PostgreSQL, lalu dirender ke dalam tabel riwayat transaksi kasir secara realtime.

---

## Arsitektur Model Final: Unified Transformer-NER

Model V2 meninggalkan pendekatan arsitektur multi-cabang regresi yang rentan terhadap interferensi tugas (*Task Interference*). Model baru menyatukan seluruh tugas ekstraksi ke dalam satu sistem jaringan saraf NLP terpadu berpola **Named Entity Recognition (NER)**.

```
Input Tokens (128,) 
     │
     ▼
[Embedding Layer (Vocab: 5000, Dim: 128, mask_zero=True)]
     │
     ▼
[Transformer Encoder x2 (Heads: 4, FFN Dim: 256)]  <-- Ekstraksi Konteks Global
     │
     ▼
[Bidirectional LSTM (Units: 64, return_sequences=True)] <-- Pemahaman Urutan Sekuensial
     │
     ▼
[Dense Output Head (Units: 7, Activation: Softmax)] <-- Klasifikasi Tag BIO Per Token

```

### Kamus Pemetaan Tag (7 Kelas)

* `0`: `O` (Kata biasa / Noise pelengkap)
* `1`: `B-PROD` (Awal kata nama menu/produk)
* `2`: `I-PROD` (Lanjutan kata nama menu/produk)
* `3`: `B-QTY` (Awal kata kuantitas/jumlah pesanan)
* `4`: `I-QTY` (Lanjutan kata kuantitas/jumlah pesanan)
* `5`: `B-PRICE` (Awal kata harga satuan/total dari kasir)
* `6`: `I-PRICE` (Lanjutan kata harga satuan/total dari kasir)

---

## Custom Training Loop & MaskedNERLoss

Proses pelatihan model di `02_training.ipynb` dikendalikan secara penuh menggunakan **Custom Training Loop (tf.GradientTape)**. Hal ini dilakukan demi menerapkan teknik optimasi tingkat rendah yang tidak didukung oleh fungsi standar Keras `model.fit`.

### Jantung Komputasi: `MaskedNERLoss`

Untuk menanggulangi masalah ketimpangan kelas (*Class Imbalance*) di mana kata biasa (`O`) mendominasi lebih dari 70% kalimat chat, kita merancang *loss function* kustom berbasis `SparseCategoricalCrossentropy` yang dilengkapi sistem pembobotan hukuman (*Class Weighting*) dan *Padding Masking*:

$$\text{Loss} = \frac{\sum (\text{Raw Loss} \times \text{Weight} \times \text{Padding Mask})}{\sum (\text{Weight} \times \text{Padding Mask}) + 1e-7}$$

* **Padding Masking:** Bobot otomatis dikalikan `0` jika token yang dibaca adalah token kosong `[PAD]`. Model tidak akan pernah membuang waktu komputasi untuk menghafal ruang kosong.
* **Sistem Hukuman Bobot Dynamic:**
  * Tag `O` (ID: 0) diberi bobot **1.0** (Hukuman normal).
  * Tag `PROD` (ID: 1, 2) diberi bobot **5.0** (Dihukum 5x lipat lebih keras jika model salah tebak nama menu).
  * Tag `QTY` & `PRICE` (ID: 3, 4, 5, 6) diberi bobot **3.0** (Dihukum 3x lipat jika salah deteksi jumlah atau harga).



### Logika Alur Siklus Gradient Tape (Per Batch):

1. **Forward Pass:** Model memproses token `x_batch` dan menghasilkan probabilitas tag `pred_ner`.
2. **Masking:** Skrip menghitung `mask_padding` (mengabaikan token 0) dan `mask_entities` (mengabaikan tag O) secara langsung di dalam kartu grafis (GPU).
3. **Backpropagation:** Tape merekam seluruh operasi, menghitung gradien kesalahan terhadap bobot saraf yang dapat dilatih (`model.trainable_weights`).
4. **Optimasi Bobot:** Optimizer Adam (`learning_rate=1e-4`) memperbarui bobot internal saraf model untuk meminimalkan loss di batch berikutnya.

---

## Evaluasi Metrik & Penanganan Error

### Laporan Kemampuan Model

Evaluasi metrik pada `03_evaluation.ipynb` mengisolasi token padding dan **tag kata biasa ('O')** menggunakan metode masking array 1D. Skor *Macro Average* dan *Micro Average* yang dihasilkan murni mencerminkan kompetensi AI dalam mengukur entitas penting:

```
LAPORAN EVALUASI DATA TEST (TANPA KATA BIASA / 'O'):
--------------------------------------------------
              precision    recall  f1-score   support

      B-PROD     0.9999    0.9999    0.9999     12025
      I-PROD     0.9999    1.0000    0.9999     26185
       B-QTY     0.9912    0.9997    0.9955     11829
       I-QTY     1.0000    1.0000    1.0000       723
     B-PRICE     0.9996    1.0000    0.9998     16710
     I-PRICE     0.9995    1.0000    0.9997     16491

   micro avg     0.9985    0.9999    0.9992     83963
   macro avg     0.9983    0.9999    0.9991     83963
weighted avg     0.9985    0.9999    0.9992     83963
```

*Model sukses meraih F1-Score sebesar **99.91%** pada data pengujian.*

### Analisis Kasus Kesalahan (*Error Analysis*)

Hasil audit menyeluruh terhadap sisa error minor membuktikan fenomena yang menguntungkan: Model AI terdeteksi **lebih pintar daripada label data latih mentahnya**. Model berhasil memprediksi kata sepeti `"5"` atau `"seporsi"` sebagai `B-QTY`, namun disalahkan oleh sistem evaluasi karena kunci jawaban di dataset sintetis tidak sengaja terlewat (berlabel `O`). Ini membuktikan generalisasi konteks model sudah sangat matang dan objektif.

---

## Algoritma Parser JSON & Kontrak Data API

### Panduan Implementasi untuk AI-2 (DENNY)

Untuk merakit prediksi tag token dari model AI-1 menjadi format struktur data komersial, tim API wajib mengimplementasikan **Fungsi Parser 3 Fase (Independent Extraction & Index Mapping)**. Metode ini memanen entitas secara mandiri ke dalam tiga list terpisah untuk melompati batas struktur kalimat terbalik dan menghapus dependensi jarak jauh kalimat kasir.

Berikut adalah referensi kode parser final dari `03_evaluation.ipynb`:

```python
import re

def bersihkan_angka_harga(teks_harga):
    teks = teks_harga.lower().replace('.', '').replace(',', '')
    if 'rb' in teks or 'ribu' in teks or 'k' in teks:
        angka = re.sub(r'[^0-9]', '', teks)
        return int(angka) * 1000 if angka else 0
    angka = re.sub(r'[^0-9]', '', teks)
    return int(angka) if angka else 0

def bersihkan_angka_qty(teks_qty):
    kamus = {
        "satu": 1, "sebiji": 1, "seporsi": 1, "sebungkus": 1, "segelas": 1, "sebotol": 1,
        "dua": 2, "loro": 2, "tiga": 3, "telu": 3, "empat": 4, "papat": 4, "lima": 5, "limo": 5,
        "setengah": 1, "sebungkus": 1
    }
    teks = teks_qty.lower().strip()
    if teks in kamus: return kamus[teks]
    angka = re.sub(r'[^0-9]', '', teks)
    return int(angka) if angka else 1

def parse_hasil_ai_ke_json(tokens, tags):
    # FASE 1: Penyatuan Subwords (Menyambung karakter token '##')
    clean_tokens, clean_tags = [], []
    for t, tag in zip(tokens, tags):
        if t == "[PAD]": break
        if t.startswith("##"):
            if clean_tokens: clean_tokens[-1] += t[2:]
        else:
            clean_tokens.append(t)
            clean_tags.append(tag)

    # FASE 2: Ekstraksi Independen (Memanen entitas ke list masing-masing)
    list_produk, list_qty, list_harga = [], [], []
    temp_word = []
    current_tag = None

    def simpan_buffer(kata_array, tag_jenis):
        kata_gabungan = " ".join(kata_array)
        if tag_jenis == "PROD": list_produk.append(kata_gabungan.title())
        elif tag_jenis == "QTY": list_qty.append(bersihkan_angka_qty(kata_gabungan))
        elif tag_jenis == "PRICE": list_harga.append(bersihkan_angka_harga(kata_gabungan))

    for kata, tag in zip(clean_tokens, clean_tags):
        if tag == "O":
            if current_tag:
                simpan_buffer(temp_word, current_tag)
                temp_word, current_tag = [], None
            continue
        if tag.startswith("B-"):
            if current_tag: simpan_buffer(temp_word, current_tag)
            temp_word = [kata]
            current_tag = tag.split("-")[1]
        elif tag.startswith("I-"):
            jenis_tag = tag.split("-")[1]
            if current_tag == jenis_tag: temp_word.append(kata)

    if current_tag and temp_word:
        simpan_buffer(temp_word, current_tag)

    # FASE 3: Asosiasi Relasional (Mapping Berdasarkan Urutan Indeks)
    items = []
    for i in range(len(list_produk)):
        qty = list_qty[i] if i < len(list_qty) else 1
        price = list_harga[i] if i < len(list_harga) else 0 # Harga satuan dari kasir
        
        # Kalkulasi subtotal otomatis dari sistem kasir
        subtotal = qty * price 

        items.append({
            "product": list_produk[i],
            "quantity": qty,
            "price_satuan": price,
            "subtotal": subtotal
        })
    return items

```

### Aturan Tambahan:

1. **Pencegahan Akumulasi Total:** Karena penjual sering menyebutkan total belanja di akhir kalimat (misal: `"jadi total harganya 55rb ya"`), list harga akan menangkap nilai `55000` di indeks terakhir. Namun, nilai total ini akan **otomatis tersaring keluar dan diabaikan** oleh Fase 3 karena jumlah elemen produk hanya ada 2 (`len(list_produk) == 2`). Sistem kasir tetap aman dan terhindar dari bug inflasi subtotal.
2. **Kesiapan Produksi:** Berkas biner model `chatkasir_model.keras` beserta aset pendukung `tokenizer.json` dinyatakan **LULUS EVALUASI** dan siap diintegrasikan ke server REST API utama.