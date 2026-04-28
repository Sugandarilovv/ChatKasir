# AI-1 Model Architect - Achmad Rifan

Bagian ini berisi seluruh pekerjaan **AI-1 (Model Architect)**: perancangan arsitektur,
pipeline pelatihan, dan evaluasi model Deep Learning NLP yang menjadi inti dari aplikasi
ChatKasir. Dokumen ini adalah **referensi utama** bagi seluruh anggota tim yang bekerja
di area yang bersentuhan dengan model AI.

---

## Tools & Environment

### Bahasa & Runtime

| Tool | Versi | Keterangan |
|------|-------|------------|
| Python | `>=3.12` | Versi runtime yang digunakan |
| uv | Latest | Package & environment manager pengganti pip + venv |

### Dependencies

| Library | Versi | Kegunaan |
|---------|-------|----------|
| TensorFlow | `>=2.21.0` | Framework utama untuk membangun dan melatih model Deep Learning NLP |
| NumPy | `>=2.4.4` | Operasi numerik dalam pipeline data dan preprocessing |
| Pandas | `>=3.0.2` | Manipulasi dan loading dataset dari DS-1 |
| scikit-learn | `>=1.8.0` | Evaluasi model: precision, recall, dan F1-score per entitas |
| Jupyter | `>=1.1.1` | Lingkungan eksplorasi dan dokumentasi proses eksperimen |
| ipykernel | `>=7.2.0` | Menghubungkan environment uv ke kernel Jupyter di VS Code |

### Cara Setup Environment

```bash
# Clone repo dan masuk ke folder ini
cd ai-model

# uv otomatis membaca pyproject.toml dan menginstall semua dependencies
uv sync

# Daftarkan kernel ke Jupyter / VS Code
uv run python -m ipykernel install --user --name chatkasir-ai --display-name "ChatKasir AI (uv)"
```

Setelah itu, buka file `.ipynb` di VS Code dan pilih kernel **"ChatKasir AI (uv)"**
di pojok kanan atas.

---

## Struktur Folder & File

```
ai-model/
├── notebooks/
│   ├── 01_model_architecture.ipynb
│   ├── 02_training.ipynb
│   └── 03_evaluation.ipynb
├── src/
│   └── model.py
├── logs/
├── RESEARCH_NOTES.md
├── pyproject.toml
├── uv.lock
├── .python-version
└── README.md
```

Folder `notebooks/` berisi seluruh proses eksperimen dalam format Jupyter Notebook,
diberi nomor urut agar alur kerja mudah diikuti.
1.  `01_model_architecture.ipynb` berisi
perancangan dan verifikasi arsitektur model, mencakup eksplorasi awal dataset dari DS-1,
definisi hyperparameter, dan `model.summary()`. 
2. `02_training.ipynb` berisi pipeline
pelatihan end-to-end: data loading, tokenisasi, padding, konfigurasi optimizer, dan
iterasi eksperimen hingga akurasi ≥85%. 
3. `03_evaluation.ipynb` berisi evaluasi model
final pada test set: tabel metrik precision, recall, F1-score per entitas, dan analisis
kesalahan.

Folder `src/` berisi kode Python bersih yang diekspor dari notebook setelah model
final. File `model.py` — yang berisi fungsi `build_model()` — **baru dibuat di Minggu
4** setelah arsitektur final dikonfirmasi, dan inilah file yang akan digunakan AI-2
(Denny) untuk diintegrasikan ke FastAPI.

Folder `logs/` akan diisi log TensorBoard mulai Minggu 4 saat training final
dijalankan. Jalankan dengan `uv run tensorboard --logdir logs/`.

File `RESEARCH_NOTES.md` berisi catatan studi referensi ilmiah (Lample et al. 2016
dan Wilie et al. 2020) yang menjadi landasan keputusan desain arsitektur.

---

## Pola Percakapan yang Ditangani Model

Pengguna ChatKasir adalah penjual UMKM yang meng-copy-paste percakapan WhatsApp
ke dalam aplikasi. Karena format WhatsApp menyertakan timestamp secara otomatis,
input mentah yang masuk ke sistem selalu mengandung metadata waktu dan tanggal yang
**tidak relevan untuk model** dan harus dibersihkan oleh preprocessing sebelum teks
masuk ke model AI.

Ada 3 pola percakapan nyata yang menjadi target pemrosesan ChatKasir. Ketiga pola
ini mendefinisikan scope model dan menjadi acuan bagi DS-1 dalam membuat dataset
sintetis.

### Pola 1: Pesanan Sederhana 1 Produk

Pola ini adalah kasus paling mudah: satu  produk, satu jumlah, dan harga satuan
disebutkan secara eksplisit oleh penjual dalam balasannya.

```
[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya
[07.44, 22/4/2026] Penjual: oke kak, 1 nasi goreng harganya 10rb, jadi totalnya 20rb ya
```

Setelah preprocessing menghapus timestamp dan menggabungkan pesan dengan separator
`[SEP]`, teks yang masuk ke model menjadi:

```
bang 2 nasi goreng ya [SEP] oke kak 1 nasi goreng harganya 10rb jadi totalnya 20rb ya
```

Model kemudian menghasilkan: `product = "nasi goreng"`, `quantity = 2`,
`price_satuan = 10000`.

### Pola 2: Multi-Produk dengan Harga Satuan Eksplisit

Pola ini adalah yang paling umum di UMKM makanan: pembeli memesan beberapa produk sekaligus dan penjual menyebutkan harga satuan masing-masing sebelum memberikan total. Karena ada lebih dari satu produk, sistem memproses setiap produk satu per satu, bukan sekaligus dalam satu prediksi.

```
[07.42, 22/4/2026] Pembeli: bang pesan 2 nasi goreng, 2 es teh ya
[07.44, 22/4/2026] Penjual: oke kak, nasi goreng harganya 10rb ya, dan es tehnya 5rb, jadi totalnya 30rb kak
```

Setelah preprocessing, teks bersih yang sama diumpankan ke model dua kali, sekali untuk setiap produk yang terdeteksi:

```
# Iterasi 1 — untuk produk pertama
bang pesan 2 nasi goreng 2 es teh ya [SEP] nasi goreng harganya 10rb es tehnya 5rb totalnya 30rb
→ product: nasi goreng | quantity: 2 | price_satuan: 10000

# Iterasi 2 — untuk produk kedua
bang pesan 2 nasi goreng 2 es teh ya [SEP] nasi goreng harganya 10rb es tehnya 5rb totalnya 30rb
→ product: es teh | quantity: 2 | price_satuan: 5000
```

Strategi pemisahan produk ini adalah tanggung jawab logika di sisi AI-2 (Denny), bukan di dalam model itu sendiri.

### Pola 3: Chat Pesanan Penuh Slang

Pola ini merepresentasikan pembeli muda yang mengetik tanpa memperhatikan ejaan. Preprocessing normalisasi slang menggunakan kamus dari DS-1 (Faradi) wajib dijalankan sebelum teks masuk ke model, karena tanpa normalisasi model tidak akan mengenali
`"nasi grngg"` sebagai `"nasi goreng"`.

```
[07.42, 22/4/2026] Pembeli: bg mau psnnn nasi grngg 2 sm es tjeh 1 deh brp tuh smua
[07.44, 22/4/2026] Penjual: nasi goreng 10rb es teh 5rb total 25rb ya kak
```

Setelah preprocessing menghapus timestamp dan menormalisasi slang:

```
abang mau pesan nasi goreng 2 sama es teh 1 berapa semua [SEP] nasi goreng 10rb es teh 5rb total 25rb ya kak
```

---

## Alur Pemrosesan Lengkap: Dari Input Mentah ke Tampilan Dashboard

Bagian ini menjelaskan perjalanan data dari saat pengguna menekan tombol paste di aplikasi hingga angka transaksi muncul di dashboard. Penting dipahami oleh seluruh anggota tim karena setiap komponen sistem bertanggung jawab atas satu tahap berbeda.

```
[1] PENGGUNA: copy-paste chat WhatsApp ke aplikasi (FS-1 Alfan)
    ↓
    Input mentah:
    "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya
     [07.44, 22/4/2026] Penjual: oke kak 1 nasi goreng 10rb totalnya 20rb"

[2] PREPROCESSING: tanggung jawab AI-2 (Denny) di sisi API
    ↓
    Langkah 2a: Hapus timestamp dengan regex
                "[07.42, 22/4/2026] Pembeli: " → dihapus
    Langkah 2b: Ekstrak isi pesan per pengirim
                pembeli = "bang 2 nasi goreng ya"
                penjual = "oke kak 1 nasi goreng 10rb totalnya 20rb"
    Langkah 2c: Normalisasi slang menggunakan kamus DS-1 (Faradi)
                "bg" → "abang", "rb" → "ribu", dst.
    Langkah 2d: Gabungkan dengan separator [SEP]
                "bang 2 nasi goreng ya [SEP] oke kak 1 nasi goreng 10rb totalnya 20rb"
    ↓
    Teks bersih siap masuk model

[3] MODEL AI-1 (Rifan): prediksi tiga entitas
    ↓
    Input  : "bang 2 nasi goreng ya [SEP] oke kak 1 nasi goreng 10rb totalnya 20rb"
    Output : {
               "product": "nasi goreng",
               "quantity": 2,
               "price_satuan": 10000 ← harga SATUAN, rupiah penuh
             }

[4] POSTPROCESSING: tanggung jawab AI-2 (Denny) di sisi API
    ↓
    Hitung total prediksi  : quantity × price_satuan = 2 × 10000 = 20000
    Ekstrak total dari chat: regex menemukan "totalnya 20rb" → 20000
    Verifikasi             : 20000 == 20000 ✓ → confidence = "HIGH"
    ↓
    Response JSON lengkap ke backend:
    {
      "product":      "nasi goreng",
      "quantity":     2,
      "price_satuan": 10000,
      "total":        20000,
      "confidence":   "HIGH"
    }

[5] BACKEND: tanggung jawab FS-2 (Reihan)
    ↓
    Simpan ke database PostgreSQL (tabel transaksi)

[6] DASHBOARD: tanggung jawab FS-1 (Alfan)
    ↓
    Tampilkan ke penjual:
    ┌─────────────┬────────┬──────────────┬──────────┐
    │ Produk      │ Jumlah │ Harga Satuan │ Total    │
    ├─────────────┼────────┼──────────────┼──────────┤
    │ nasi goreng │ 2      │ Rp10.000     │ Rp20.000 │
    └─────────────┴────────┴──────────────┴──────────┘
```

---

## Arsitektur Model

Model menggunakan pendekatan **Multi-Output dengan Shared Bidirectional LSTM Encoder** untuk mengekstrak tiga entitas sekaligus dari satu teks bersih yang sudah melalui preprocessing. Kata "shared" berarti satu encoder memproses seluruh kalimat sekali,
lalu hasilnya dibagikan ke tiga output head yang masing-masing mengekstrak satu entitas, jauh lebih efisien dibanding membuat tiga encoder terpisah.

```
INPUT
Array integer hasil tokenisasi dan padding dari teks yang sudah bersih
Contoh: "bang 2 nasi goreng ya [SEP] oke kak 1 nasi goreng 10rb totalnya 20rb"
        → [45, 302, 17, 89, 12, 999, 203, 56, 17, 89, 78, 521, 34, 0, 0]
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  EMBEDDING LAYER                                    │
│  Ubah setiap angka (token) → vektor bermakna        │
│  Kata yang mirip maknanya → vektor yang berdekatan  │
│  Contoh: "goreng" dan "bakar" → posisi vektor dekat │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  BIDIRECTIONAL LSTM                                 │
│  Baca kalimat dari DUA arah sekaligus:              │
│  → Kiri ke kanan: "bang 2 nasi goreng ya [SEP] ..." │
│  ← Kanan ke kiri: "... [SEP] ya goreng nasi 2 bang" │
│  Hasil: satu ringkasan pemahaman seluruh kalimat    │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  DROPOUT (0.3)                                      │
│  Matikan 30% neuron secara acak saat training       │
│  Tujuan: agar model tidak "menghafal" data,         │
│  melainkan benar-benar "memahami" polanya           │
└─────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  SHARED DENSE (128 neuron)                          │
│  Proses lanjutan dari ringkasan LSTM                │
│  Hasilnya dibagikan ke KETIGA output di bawah       │
│  (inilah yang disebut "shared" / bersama)           │
└─────────────────────────────────────────────────────┘
        │
        │ ← satu representasi, terpecah ke tiga arah
        │
   ┌────┴──────────────┬──────────────────┐
   ▼                   ▼                  ▼

┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   PRODUCT    │ │   QUANTITY   │ │    PRICE     │
│              │ │              │ │   SATUAN     │
│  Klasifikasi │ │   Regresi    │ │   Regresi    │
│  (softmax)   │ │   (relu)     │ │   (relu)     │
│              │ │              │ │              │
│ Pilih 1 nama │ │ Prediksi     │ │ Prediksi     │
│ produk dari  │ │ angka jumlah │ │ harga SATUAN │
│ daftar yang  │ │ pesanan      │ │ dalam rupiah │
│ dikenal      │ │              │ │ penuh        │
└──────────────┘ └──────────────┘ └──────────────┘
       │                │                │
       ▼                ▼                ▼

OUTPUT MODEL (tiga nilai, dikirim ke AI-2 Denny)
{
  "product": "nasi goreng",  ← nama produk baku, huruf kecil
  "quantity": 2,             ← integer, default 1 jika tidak disebutkan
  "price_satuan": 10000      ← rupiah PENUH, BUKAN ribuan, BUKAN total
}
```

### Keputusan Desain

| Komponen | Pilihan | Alasan |
|----------|---------|--------|
| Encoder | Bidirectional LSTM | Konteks dua arah penting untuk NER (Lample et al., 2016) |
| Embedding | Dilatih dari nol | Kosakata domain ChatKasir sangat spesifik |
| Product head | Softmax (klasifikasi) | Memilih satu dari daftar produk yang dikenal di dataset |
| Quantity head | ReLU (regresi) | Angka kontinu, selalu positif, dibulatkan saat inferensi |
| Price head | ReLU (regresi) | Harga SATUAN dalam rupiah penuh, dinormalisasi ÷1000 saat training |
| Dropout | 0.3 | Mengurangi risiko overfitting pada dataset skala kecil |
| Harga total | Tidak diprediksi model | Dihitung deterministik oleh AI-2: `quantity × price_satuan` |

Detail lengkap, kode, dan hasil verifikasi ada di `notebooks/01_model_architecture.ipynb`.

---

## Custom Loss Function untuk 3 Output Head

Model ChatKasir memiliki 3 output head yang masing-masing menyelesaikan jenis tugas yang berbeda, 1 klasifikasi dan 2 regresi. 

Karena sifat matematika dari setiap tugas berbeda, maka definisi "seberapa salah sebuah prediksi" juga berbeda untuk setiap head. Itulah mengapa setiap head membutuhkan loss function yang berbeda pula.
 
Prinsip yang mendasari seluruh pilihan di bawah ini adalah:
**loss function harus mencerminkan sifat matematika dari apa yang diprediksi, bukan sekadar alat pengukur error generik.**

### Head product: Sparse Categorical Crossentropy
 
Output head `product` melakukan tugas klasifikasi: dari sekian ribu nama produk yang dikenal model (berasal dari dataset `food_utama.csv` DS-1), model memilih satu yang paling mungkin. Output layer menggunakan `softmax` yang menghasilkan vektor probabilitas, misalnya `[0.02, 0.87, 0.01, ...]` di mana nilai tertinggi adalah prediksi produk.
 
Loss function yang tepat untuk ini adalah **Sparse Categorical Crossentropy**. Ia mengukur jarak antara distribusi probabilitas yang diprediksi model versus distribusi "sempurna" di mana probabilitas 1.0 ada tepat di posisi produk yang benar dan 0.0 di semua posisi lainnya. Intuisinya: **keyakinan yang salah dihukum jauh lebih keras daripada keraguan yang salah**. Jika model 87% yakin produknya "nasi goreng" dan ternyata memang benar, loss-nya kecil. Jika model 87% yakin tapi ternyata salah, loss-nya besar.
 
Varian "Sparse" dipilih, bukan Categorical Crossentropy biasa, karena label produk di dataset disimpan sebagai integer tunggal (misalnya `2` untuk "nasi goreng"), bukan sebagai one-hot vector `[0, 1, 0, 0, ...]`. Dengan ratusan hingga ribuan kelas produk dari `food.csv`, format one-hot akan memakan memori yang sangat besar tanpa manfaat komputasi apapun. Sparse Categorical Crossentropy menghasilkan nilai loss yang identik secara matematis
dengan jauh lebih efisien.
 
```
tf.keras.losses.SparseCategoricalCrossentropy()
```
 
### Head quantity: Mean Squared Error
 
Output head `quantity` melakukan tugas regresi: memprediksi angka kontinu yang merepresentasikan jumlah pesanan. Output layer menggunakan `relu` yang menghasilkan satu angka non-negatif, misalnya `2.3` yang kemudian dibulatkan menjadi integer `2` saat inferensi.
 
Loss function yang tepat untuk ini adalah **Mean Squared Error (MSE)**. Ia mengukur rata-rata dari kuadrat selisih antara prediksi dan jawaban yang benar. Pengkuadratan memiliki dua efek yang keduanya diinginkan: 
- Pertama, error negatif dan positif diperlakukan setara (selisih `-3` dan `+3` sama-sama menghasilkan loss `9`). 
- Kedua dan lebih penting, **error besar dihukum secara tidak proporsional** selisih 1 menghasilkan loss 1, tapi selisih 3 menghasilkan loss 9. Ini mendorong model menghindari kesalahan besar, yang masuk akal untuk konteks jumlah pesanan di mana prediksi "10 porsi" untuk pesanan yang sebenarnya "2 porsi" jauh lebih merusak, daripada prediksi "3 porsi".
 
```
tf.keras.losses.MeanSquaredError()
```
 
> **Catatan penting tentang skala:** Karena `quantity` bernilai kecil (1–10)
> sedangkan `price_satuan` bisa bernilai puluhan ribu, loss dari `price_satuan`
> akan mendominasi secara masif jika tidak ditangani. Inilah mengapa
> `price_satuan` **dinormalisasi dengan dibagi 1000** sebelum masuk ke training
> untuk menyamakan skala kedua output regresi agar keduanya berkontribusi
> secara proporsional terhadap total loss.
 
### Head price: MaskedPriceLoss (Custom)
 
Output head `price` juga melakukan tugas regresi, tapi memiliki karakteristik unik yang tidak bisa ditangani oleh MSE standar: **sebagian baris dataset memiliki `price_satuan = -1`**, yaitu kasus di mana harga tidak disebutkan dalam percakapan chat (misalnya pembeli hanya berkata `"bang 2 nasi goreng ya"` tanpa ada balasan penjual yang menyebut harga).
 
Jika MSE standar digunakan, ia akan menghukum model setiap kali prediksinya tidak sama dengan `-1` pada baris-baris tersebut, yang secara konseptual salah, karena `-1` bukan harga yang valid melainkan hanya sentinel penanda "harga tidak diketahui". Model akan belajar pola yang keliru: mencoba memprediksi `-1` untuk kasus yang sebenarnya tidak memiliki jawaban.
 
**MaskedPriceLoss menyelesaikan masalah ini dengan mengecualikan baris bernilai `-1` dari perhitungan loss sama sekali.** Hanya baris yang memiliki harga valid yang berkontribusi terhadap gradient dan pembaruan bobot model. Dengan cara ini, model tidak dihukum untuk situasi yang memang tidak memiliki jawaban, ia belajar untuk "mengakui ketidaktahuan" alih-alih menebak angka acak.
 
Konsep masking ini terinspirasi dari teknik serupa yang digunakan dalam sequence labeling (Lample et al., 2016) untuk mengabaikan token padding saat menghitung loss, namun diterapkan di level baris data alih-alih level token.
 
```
class MaskedPriceLoss(tf.keras.losses.Loss):
    """
    Custom Loss Function untuk output head 'price_satuan'.
 
    Mengecualikan baris dengan price_satuan = -1 (harga tidak diketahui)
    dari perhitungan loss, sehingga model tidak belajar pola yang keliru
    dari data yang memang tidak memiliki jawaban valid.
 
    Nilai sentinel -1 dipilih karena:
    - Harga valid selalu >= 0, sehingga -1 tidak ambigu
    - Aman secara matematis (tidak seperti NaN yang meracuni gradient)
    - Mudah dicek dengan operasi != -1
    """
 
    def __init__(self, name="masked_price_loss"):
        super().__init__(name=name)
        self.NULL_INDICATOR = -1.0
 
    def call(self, y_true, y_pred):
        # 1. Buat mask - True (1.0) untuk baris yang PUNYA harga valid
        mask = tf.cast(
            tf.not_equal(y_true, self.NULL_INDICATOR),
            dtype=tf.float32
        )
        # Contoh: y_true = [-1, 10.0, 8.0, -1, 5.0]  ← sudah dinormalisasi ÷1000
        # mask  = [  0,  1.0,  1.0,   0,  1.0]
 
        # 2. Hitung squared error untuk semua baris
        squared_error = tf.square(y_true - y_pred)
 
        # 3. Terapkan mask - baris null menghasilkan error = 0
        masked_error = squared_error * mask
 
        # 4. Rata-ratakan berdasarkan jumlah baris VALID saja
        # (bukan total baris) agar skala loss tidak mengecil secara palsu
        n_valid = tf.maximum(tf.reduce_sum(mask), 1.0)  # hindari division by zero
        loss = tf.reduce_sum(masked_error) / n_valid
 
        return loss
```
  
### Bagaimana Ketiga Loss Digabungkan
 
Saat kompilasi model, TensorFlow menghitung loss masing-masing head secara terpisah lalu menjumlahkannya menjadi satu nilai *total loss* yang digunakan untuk memperbarui seluruh bobot model melalui backpropagation. Parameter `loss_weights` mengontrol seberapa besar kontribusi masing-masing head terhadap total loss.
 
```
model.compile(
    optimizer="adam",
 
    loss={
        # Klasifikasi multi-kelas - label berupa integer, bukan one-hot
        "product":  tf.keras.losses.SparseCategoricalCrossentropy(),
 
        # Regresi jumlah - MSE standar, quantity bernilai kecil (1–10)
        "quantity": tf.keras.losses.MeanSquaredError(),
 
        # Regresi harga - custom, mengabaikan baris dengan price = -1
        # price dinormalisasi ÷1000 sebelum training untuk samakan skala
        "price":    MaskedPriceLoss(),
    },
 
    loss_weights={
        # Bobot awal yang sama untuk semua head
        # Akan di-tune di Minggu 3 jika salah satu head dominan
        # atau sulit konvergen berdasarkan kurva loss di TensorBoard
        "product":  1.0,
        "quantity": 1.0,
        "price":    1.0,
    }
)
```
 
Ringkasan keputusan loss function untuk seluruh tim:
 
```
┌──────────────┬─────────────────────────────────┬────────────────────────────┐
│ Output Head  │ Loss Function                   │ Alasan                     │
├──────────────┼─────────────────────────────────┼────────────────────────────┤
│ product      │ SparseCategoricalCrossentropy   │ Klasifikasi multi-kelas,   │
│              │ (standar TensorFlow)            │ label berupa integer       │
├──────────────┼─────────────────────────────────┼────────────────────────────┤
│ quantity     │ MeanSquaredError                │ Regresi angka kontinu,     │
│              │ (standar TensorFlow)            │ hukum error besar lebih    │
│              │                                 │ keras (dikuadratkan)       │
├──────────────┼─────────────────────────────────┼────────────────────────────┤
│ price        │ MaskedPriceLoss                 │ Regresi dengan data tidak  │
│ (price_stn)  │ (CUSTOM — AI-1)                 │ lengkap: abaikan baris     │
│              │                                 │ price_satuan = -1          │
└──────────────┴─────────────────────────────────┴────────────────────────────┘
 
Catatan untuk DS-1 (Faradi): price_satuan yang tidak diketahui diisi dengan
nilai sentinel -1 (bukan null, NaN, atau 0) di dataset sintetis.

Catatan untuk AI-2 (Denny): model mengembalikan price_satuan dalam skala
rupiah penuh SETELAH de-normalisasi (×1000). De-normalisasi dilakukan di
postprocessing sebelum response dikirim ke backend, bukan di dalam model.
```
 
---

## Catatan untuk Anggota Tim

### Untuk DS-1: Faradi (Data Engineer)

Model hanya menerima teks yang sudah bersih — **tanpa timestamp WhatsApp**. Kolom
`input_text` di dataset sintetis yang kamu buat harus langsung berisi teks bersih
dengan separator `[SEP]`, bukan format mentah WhatsApp. Timestamp akan selalu dihapus
oleh preprocessing di sisi API, jadi tidak perlu dan tidak boleh ada di dataset training.

Setiap baris dataset harus memiliki empat kolom dengan tipe data berikut:

| Kolom | Tipe Python | Aturan Wajib |
|-------|-------------|--------------|
| `input_text` | `str` | Teks bersih dengan `[SEP]` sebagai separator. Tidak mengandung timestamp, tidak mengandung label `"Pembeli:"` atau `"Penjual:"` |
| `product` | `str` | Nama produk baku, **huruf kecil semua**, konsisten dengan dataset `eriko-syah/indonesian-food`. Contoh: `"nasi goreng"`, bukan `"Nasi Goreng"` |
| `quantity` | `int` | Angka bulat positif. Default `1` jika tidak disebutkan. Konversi semua bentuk: `"dua"` → `2`, `"3 porsi"` → `3` |
| `price_satuan` | `int` | Rupiah **penuh** — `"10rb"` → `10000`. **Selalu harga satuan, tidak pernah harga total.** Gunakan `null` jika harga tidak disebutkan |

Aturan paling kritis yang tidak boleh dilanggar satu baris pun: kolom `price_satuan`
harus selalu berisi harga satuan dalam rupiah penuh. Kalau ada baris yang menggunakan
harga total atau nilai dalam ribuan, model akan belajar konvensi yang salah dan seluruh
kalkulasi di dashboard akan keliru.

Variasi penulisan yang perlu dicakup untuk memastikan model robust: 
1. Untuk harga,
sertakan `10rb`, `10ribu`, `10.000`, `10k`, `Rp10.000`, dan `sepuluh ribu` — semuanya
dikonversi ke `10000` di kolom label.
2. Untuk quantity, sertakan `"2 porsi"`, `"dua"`,
`"2 biji"`, `"2 pcs"` — semuanya dikonversi ke integer `2`.

Contoh format baris yang benar di dataset:

```
input_text                                                          | product      | quantity | price_satuan
--------------------------------------------------------------------|--------------|----------|-------------
"bang 2 nasi goreng ya [SEP] oke kak 1 nasi goreng 10rb total 20rb" | nasi goreng  | 2        | 10000
"pesen es teh 3 [SEP] es teh 5rb per gelas total 15rb ya kak"       | es teh       | 3        | 5000
"bg mau nasi grngg 2 [SEP] nasi goreng 10rb ya"                     | nasi goreng  | 2        | 10000
```

### Untuk AI-2: Denny (API & Inference)

Tanggung jawabmu dimulai **sebelum** teks masuk ke model dan berlanjut **setelah**
model menghasilkan output. Ada dua blok kerja utama.

Blok pertama adalah preprocessing. Sebelum teks masuk ke model, hapus timestamp
WhatsApp dengan regex, pisahkan pesan pembeli dan penjual, gabungkan dengan `[SEP]`,
lalu jalankan normalisasi slang menggunakan kamus dari Faradi. Berikut kerangka kode
yang bisa dikembangkan:

```python
import re

def parse_whatsapp_chat(raw_text: str) -> dict:
    """
    Membersihkan format timestamp WhatsApp dan memisahkan
    pesan pembeli dan penjual.
    Pola yang ditangani:
    "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya"
    "[07.44, 22/4/2026] Penjual: oke kak 10rb ya"
    """
    # Regex mengenali format: [timestamp] NamaPengirim: isi pesan
    pattern = r'\[([^\]]+)\]\s*(Pembeli|Penjual):\s*'
    lines = raw_text.strip().split('\n')
    hasil = {"pembeli": "", "penjual": ""}

    for line in lines:
        match = re.match(pattern, line)
        if match:
            pengirim = match.group(2).lower()
            isi_pesan = re.sub(pattern, '', line).strip()
            hasil[pengirim] = isi_pesan

    return hasil


def prepare_model_input(raw_text: str) -> str:
    """Mengubah raw chat WhatsApp → string bersih siap masuk model."""
    parsed = parse_whatsapp_chat(raw_text)

    if parsed["penjual"]:
        return parsed["pembeli"] + " [SEP] " + parsed["penjual"]

    return parsed["pembeli"]
```

Blok kedua adalah postprocessing. Setelah model menghasilkan output, hitung `total`
dan `confidence` sebelum response dikirim ke backend Reihan. Perhatikan bahwa model
memberikan `price_satuan` dalam **rupiah penuh** — tidak perlu konversi apapun.

```python
def postprocess(model_output: dict, teks_bersih: str) -> dict:
    """Menghitung total dan confidence flag dari output model."""
    quantity     = model_output["quantity"]
    price_satuan = model_output["price_satuan"]  # sudah dalam rupiah penuh

    # Hitung total dari prediksi model
    total_prediksi = quantity * price_satuan

    # Ekstrak total yang disebutkan di chat dengan regex
    # Menangani: "totalnya 20rb", "total 20.000", "20ribu"
    match = re.search(
        r'total(?:nya)?\s*(\d+(?:\.\d+)?)\s*(rb|ribu|k)?',
        teks_bersih, re.IGNORECASE
    )
    total_chat = None
    if match:
        angka = float(match.group(1).replace('.', ''))
        satuan = match.group(2)
        total_chat = int(angka * 1000) if satuan and satuan.lower() in ['rb', 'ribu', 'k'] else int(angka)

    # Tentukan confidence
    if total_chat and total_prediksi == total_chat:
        confidence = "HIGH"      # total cocok → prediksi dapat dipercaya
    elif total_chat:
        confidence = "LOW"       # ada total di chat tapi tidak cocok → perlu konfirmasi
    else:
        confidence = "MEDIUM"    # tidak ada total di chat untuk diverifikasi

    return {**model_output, "total": total_prediksi, "confidence": confidence}
```

Format response JSON yang harus dikirim ke backend Reihan — **pastikan semua field
ini ada** karena Alfan membutuhkannya untuk dashboard:

```json
{
  "product":      "nasi goreng",
  "quantity":     2,
  "price_satuan": 10000,
  "total":        20000,
  "confidence":   "HIGH"
}
```

### Untuk FS-2: Reihan (Back-End)

Ada dua hal yang perlu diperhatikan dari sisi database dan API Contract. 
1. Pertama,
skema tabel `transaksi` perlu menyimpan `price_satuan` dan `total` sebagai kolom
terpisah, keduanya dalam satuan rupiah penuh sebagai integer. Jangan menyimpan dalam
ribuan karena akan membingungkan saat query agregasi laporan keuangan.
2. Kedua, tabel
`products` sebaiknya memiliki kolom `harga_satuan` untuk menyimpan harga historis per
produk per penjual — berguna sebagai fallback ketika harga tidak disebutkan di chat dan
`price_satuan` dari model bernilai `null`.

Yang paling penting: pastikan `API_CONTRACT.md` mencantumkan field `total` dan
`confidence` di response JSON dari AI-2, karena kedua field ini dibutuhkan Alfan untuk
menampilkan data di dashboard dan menentukan apakah transaksi perlu konfirmasi manual.

### Untuk FS-1: Alfan (Front-End)

Ada dua hal yang perlu diperhatikan dari sisi tampilan. 
1. Pertama, halaman copy-paste
perlu memberikan instruksi singkat kepada pengguna tentang cara meng-copy chat
WhatsApp — cukup pilih pesan pembeli dan balasan penjual lalu paste. Format timestamp
WhatsApp akan dibersihkan otomatis oleh sistem, jadi pengguna tidak perlu khawatir.

2. Kedua, dashboard perlu menangani nilai `confidence` dari API secara intuitif. 
   - Ketika
`confidence = "HIGH"`, transaksi bisa langsung ditampilkan dan disimpan. 
   - Ketika
`confidence = "LOW"`, tampilkan peringatan bahwa ada ketidaksesuaian harga dan minta
penjual mengkonfirmasi sebelum data disimpan.   
   - Ketika `confidence = "MEDIUM"`, tampilkan
data prediksi dengan opsi untuk mengedit jika penjual merasa angkanya tidak tepat.

4 kolom yang ditampilkan di dashboard transaksi sudah datang dalam format final
dari API — tidak perlu dihitung lagi di sisi frontend:

```
┌─────────────┬────────┬──────────────┬──────────┐
│ Produk      │ Jumlah │ Harga Satuan │ Total    │
├─────────────┼────────┼──────────────┼──────────┤
│ nasi goreng │ 2      │ Rp10.000     │ Rp20.000 │
│ es teh      │ 3      │ Rp5.000      │ Rp15.000 │
└─────────────┴────────┴──────────────┴──────────┘
```