# AI-1 Model Architect — Achmad Rifan

Bagian ini berisi seluruh pekerjaan **AI-1 (Model Architect)**: perancangan arsitektur, pipeline pelatihan, dan evaluasi model Deep Learning NLP yang menjadi inti dari aplikasi ChatKasir.

---

## Tools & Environment

### Bahasa & Runtime

| Tool   | Versi    | Keterangan                                         |
| ------ | -------- | -------------------------------------------------- |
| Python | `>=3.12` | Versi runtime yang digunakan                       |
| uv     | Latest   | Package & environment manager pengganti pip + venv |

### Dependencies

| Library      | Versi      | Kegunaan                                                            |
| ------------ | ---------- | ------------------------------------------------------------------- |
| TensorFlow   | `>=2.21.0` | Framework utama untuk membangun dan melatih model Deep Learning NLP |
| NumPy        | `>=2.4.4`  | Operasi numerik dalam pipeline data dan preprocessing               |
| Pandas       | `>=3.0.2`  | Manipulasi dan loading dataset dari DS-1                            |
| scikit-learn | `>=1.8.0`  | Evaluasi model: precision, recall, dan F1-score per entitas         |
| Jupyter      | `>=1.1.1`  | Lingkungan eksplorasi dan dokumentasi proses eksperimen             |
| ipykernel    | `>=7.2.0`  | Menghubungkan environment uv ke kernel Jupyter di VS Code           |

### Cara Setup Environment

```bash
# Clone repo dan masuk ke folder ini
cd ai-model

# uv otomatis membaca pyproject.toml dan menginstall semua dependencies
uv sync

# Daftarkan kernel ke Jupyter / VS Code
uv run python -m ipykernel install --user --name chatkasir-ai --display-name "ChatKasir AI (uv)"
```

Setelah itu, buka file `.ipynb` di VS Code dan pilih kernel **"ChatKasir AI (uv)"** di pojok kanan atas.

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
├── pyproject.toml
├── uv.lock
├── .python-version
└── README.md
```

### `notebooks/`

Berisi seluruh proses eksperimen dalam format Jupyter Notebook. Diberi nomor urut agar alur kerja mudah diikuti.

| File                          | Keterangan                                                                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `01_model_architecture.ipynb` | Perancangan dan verifikasi arsitektur model. Mencakup eksplorasi awal dataset dari DS-1, definisi hyperparameter, dan `model.summary()`     |
| `02_training.ipynb`           | Pipeline pelatihan end-to-end: data loading, tokenisasi, padding, konfigurasi optimizer, dan iterasi eksperimen hingga akurasi ≥85%         |
| `03_evaluation.ipynb`         | Evaluasi model final pada test set: tabel metrik precision, recall, F1-score per entitas (product, quantity, price), dan analisis kesalahan |

### `src/`

Berisi kode Python bersih yang diekspor dari notebook setelah model final. Digunakan oleh **AI-2 API & Inference** untuk diintegrasikan ke dalam FastAPI.

| File       | Keterangan                                                                                                     |
| ---------- | -------------------------------------------------------------------------------------------------------------- |
| `model.py` | Definisi fungsi `build_model()` yang dapat diimport sebagai modul. Dibuat di Minggu 4 setelah arsitektur final |

### `logs/`

Berisi log TensorBoard yang dihasilkan selama proses pelatihan. Diisi mulai Minggu 4 saat training final dijalankan.

```bash
# Cara menjalankan TensorBoard
uv run tensorboard --logdir logs/
```

### File Konfigurasi

| File              | Keterangan                                                                                                                  |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `pyproject.toml`  | Daftar dependencies dan konfigurasi project yang dikelola oleh `uv`                                                         |
| `uv.lock`         | Lockfile otomatis dari `uv` — memastikan semua anggota tim menginstall versi library yang identik. **Jangan diedit manual** |
| `.python-version` | Menentukan versi Python yang digunakan `uv` di folder ini secara otomatis                                                   |
| `README.md`       | Dokumentasi ini                                                                                                             |

---

## Arsitektur Model

Model menggunakan pendekatan **Multi-Output dengan Shared Bidirectional LSTM Encoder** untuk mengekstrak tiga entitas sekaligus dari satu kalimat pesanan informal Bahasa Indonesia.

```
INPUT:
Kalimat pesanan yang sudah diubah menjadi array angka.
Contoh: "pesan nasi goreng 2 porsi 30rb" → [45, 17, 89, 302, 156, 78, 0, 0]
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
│  → Kiri ke kanan: "pesan nasi goreng 2 porsi 30rb"  │
│  ← Kanan ke kiri: "30rb porsi 2 goreng nasi pesan"  │
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
│              │ │              │ │              │
│  Klasifikasi │ │   Regresi    │ │   Regresi    │
│  (softmax)   │ │   (relu)     │ │   (relu)     │
│              │ │              │ │              │
│ Pilih 1 nama │ │ Prediksi     │ │ Prediksi     │
│ produk dari  │ │ angka jumlah │ │ angka harga  │
│ daftar yang  │ │ pesanan      │ │ dalam ribuan │
│ dikenal      │ │              │ │ rupiah       │
└──────────────┘ └──────────────┘ └──────────────┘
       │                │                │
       ▼                ▼                ▼

OUTPUT:
{
  "product":  "nasi goreng",   ← nama produk
  "quantity": 2,               ← jumlah pesanan
  "price":    30000            ← harga dalam rupiah
}
```

### Keputusan Desain

| Komponen      | Pilihan               | Alasan                                                   |
| ------------- | --------------------- | -------------------------------------------------------- |
| Encoder       | Bidirectional LSTM    | Konteks dua arah penting untuk NER (Lample et al., 2016) |
| Embedding     | Dilatih dari nol      | Kosakata domain ChatKasir sangat spesifik                |
| Product head  | Softmax (klasifikasi) | Memilih dari daftar produk yang dikenal di dataset       |
| Quantity head | ReLU (regresi)        | Angka kontinu, selalu positif                            |
| Price head    | ReLU (regresi)        | Dinormalisasi ÷1000 saat training untuk stabilitas       |
| Dropout       | 0.3                   | Mengurangi risiko overfitting pada dataset skala kecil   |

Detail lengkap, kode, dan hasil verifikasi ada di
`notebooks/01_model_architecture.ipynb`.

---

## Catatan untuk Anggota Tim Lain

**DS-1 (Faradi):** Dataset final yang sudah dibersihkan diletakkan di
folder `data/` pada root repo. Format yang diharapkan dan spesifikasi
kolom dikonfirmasi bersama di Weekly Sync Minggu 1.

**AI-2 (Denny):** File model final (`.keras` atau `SavedModel`)
diupload ke Google Drive. Link download publik dicantumkan di README
root repo. Script load model tersedia di `src/model.py`.

---

## Catatan untuk Anggota Tim Lain

- **DS-1 Data Engineer:** Dataset final yang sudah dibersihkan diletakkan di folder `data/` pada root repo. Format yang diharapkan dan spesifikasi kolom dikonfirmasi bersama di Weekly Sync Minggu 1.
- **AI-2 API & Inference:** File model final (`.keras` atau `SavedModel`) diupload ke Google Drive. Link download publik dicantumkan di README root repo. Script load model tersedia di `src/model.py`.
