# AI-2 Inference API — ChatKasir

FastAPI service yang menerima raw chat WhatsApp dari backend (FS-2), menjalankan pipeline preprocessing → inferensi model AI → postprocessing, lalu mengembalikan data transaksi terstruktur dalam format JSON.

---

## Daftar Isi

- [Arsitektur \& Alur](#arsitektur--alur)
- [Struktur Folder](#struktur-folder)
- [Cara Menjalankan Lokal](#cara-menjalankan-lokal)
- [Environment Variables](#environment-variables)
- [Endpoint API](#endpoint-api)
  - [GET /health](#get-health)
  - [POST /predict](#post-predict)
- [Skema Request \& Response](#skema-request--response)
- [Error Codes](#error-codes)
- [Edge Cases yang Ditangani](#edge-cases-yang-ditangani)
- [Pipeline Preprocessing](#pipeline-preprocessing)
- [Arsitektur Model AI](#arsitektur-model-ai)
- [Sistem Confidence](#sistem-confidence)
- [Testing](#testing)
- [Deploy ke Hugging Face Spaces](#deploy-ke-hugging-face-spaces)
- [Keamanan](#keamanan)

---

## Arsitektur & Alur

```
FS-2 (Backend Express.js) → POST /predict
  │
  ├── [1] Autentikasi      Header X-API-Key divalidasi via secrets.compare_digest
  ├── [2] Validasi Input   Teks < 5 karakter → 422 INVALID_INPUT
  ├── [3] Preprocessing    Hapus timestamp, strip nama pengirim, lowercase,
  │                        normalisasi slang & mata uang, sisipkan token [SEP]
  ├── [4] Inferensi Async  run_in_executor → model.predict() tidak memblokir event loop
  │         Model AI-1: Transformer Encoder + BiLSTM + NER Head (7 tag BIO)
  │         Tag: O, B-PROD, I-PROD, B-QTY, I-QTY, B-PRICE, I-PRICE
  │         Output: product_name (string), quantity (int), price_satuan (int|null)
  ├── [5] Postprocessing   Kalkulasi subtotal, fallback regex produk, scoring confidence
  └── [6] Response 200     JSON ke FS-2 → Dashboard Frontend
```

**Stack Utama:** FastAPI · TensorFlow 2.20 · HuggingFace Tokenizers · Pydantic v2 · Uvicorn

---

## Struktur Folder

```
api-inference/
├── app/
│   ├── core/
│   │   ├── config.py           # Settings via pydantic-settings + .env
│   │   ├── errors.py           # Custom exceptions (AI2BaseException) + handler registration
│   │   └── security.py         # Dependency require_api_key (timing-attack safe)
│   ├── routers/
│   │   ├── health.py           # GET /health — monitoring tanpa auth
│   │   └── predict.py          # POST /predict — endpoint inferensi utama
│   ├── schemas/
│   │   └── predict.py          # PredictRequest, OrderItem, PredictResponse (Pydantic)
│   ├── services/
│   │   ├── model_loader.py     # Singleton ModelLoader + TransformerEncoder custom layer
│   │   └── processing.py       # Preprocessing & postprocessing pipeline
│   └── main.py                 # Inisialisasi FastAPI, CORS, lifespan, auto-download aset
├── tests/
│   ├── tests_predict.py        # Integration tests endpoint (30+ skenario)
│   ├── tests_processing.py     # Unit tests pipeline teks
│   ├── tests_slang.py          # Unit tests kamus slang
│   └── tests_stress.py         # Stress test 100 request paralel
├── static/
│   └── index.html              # UI demo untuk Hugging Face Spaces
├── Dockerfile                  # Image untuk deploy ke Hugging Face Spaces
├── requirements.txt            # Dependency Python yang dikunci versinya
└── .env.example                # Template konfigurasi environment
```

---

## Cara Menjalankan Lokal

### Prasyarat

- Python 3.10+
- pip

### Instalasi

```bash
# 1. Masuk ke direktori
cd api-inference

# 2. (Opsional) Buat virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# 3. Install semua dependency
pip install -r requirements.txt

# 4. Salin dan konfigurasi file environment
cp .env.example .env
```

### Konfigurasi `.env`

Edit file `.env` dan sesuaikan nilai-nilai berikut sebelum menjalankan:

```env
API_KEY=rahasia_kamu_ganti_ini
MODEL_PATH=models/model.keras
TOKENIZER_PATH=models/tokenizer.json
GDRIVE_MODEL_URL=https://drive.google.com/uc?id=<FILE_ID_MODEL>
GDRIVE_TOKENIZER_URL=https://drive.google.com/uc?id=<FILE_ID_TOKENIZER>
GDRIVE_SLANG_URL=https://drive.google.com/uc?id=<FILE_ID_SLANG>
```

> **Catatan:** Saat server pertama kali dijalankan, model, tokenizer, dan kamus slang akan **otomatis diunduh** dari Google Drive jika belum ada di lokal.

### Jalankan Server

```bash
uvicorn app.main:app --reload --port 8000
```

Server aktif di `http://localhost:8000`. Dokumentasi interaktif Swagger tersedia di `http://localhost:8000/docs`.

---

## Environment Variables

| Variabel | Default | Keterangan |
|---|---|---|
| `API_KEY` | `changeme` | **Wajib diganti** sebelum deploy. Digunakan di header `X-API-Key`. |
| `MODEL_PATH` | `models/model.keras` | Path lokal file model Keras AI-1. |
| `TOKENIZER_PATH` | `models/tokenizer.json` | Path lokal file tokenizer WordPiece (HuggingFace). |
| `MAX_SEQUENCE_LEN` | `128` | Panjang sekuens token. Harus sesuai dengan konfigurasi saat training. |
| `SLANG_DICT_PATH` | `data/final/slang_utama.csv` | Path kamus slang CSV (header: `slang,baku`). |
| `GDRIVE_MODEL_URL` | *(lihat config.py)* | URL Google Drive untuk auto-download file model. |
| `GDRIVE_TOKENIZER_URL` | *(lihat config.py)* | URL Google Drive untuk auto-download tokenizer. |
| `GDRIVE_SLANG_URL` | *(lihat config.py)* | URL Google Drive untuk auto-download kamus slang. |
| `ALLOWED_ORIGINS` | `["*"]` | Daftar CORS origins. Ganti dengan domain spesifik saat production. |
| `DEBUG` | `false` | Jika `true`, autentikasi API key dinonaktifkan (untuk demo publik). |
| `PORT` | `7860` | Port server. Default 7860 untuk Hugging Face Spaces. |

---

## Endpoint API

### `GET /health`

Cek status kesehatan service. Tidak memerlukan autentikasi. Cocok untuk digunakan sebagai health check probe pada container orchestration (Docker, Kubernetes).

**Response `200 OK` — Model siap:**

```json
{
  "status": "ok",
  "model_loaded": true,
  "version": "2.0",
  "slang_dict": {
    "total": 1250,
    "single_word": 980,
    "multi_word": 270,
    "loaded": true,
    "path": "data/final/slang_utama.csv"
  }
}
```

**Response `503 Service Unavailable` — Model belum termuat:**

```json
{
  "status": "degraded",
  "model_loaded": false,
  "version": "2.0",
  "slang_dict": { ... }
}
```

---

### `POST /predict`

Endpoint inferensi utama. Menerima teks chat WhatsApp mentah dan mengembalikan daftar item transaksi terstruktur.

**Header yang Dibutuhkan:**

```
X-API-Key: <api_key_kamu>
Content-Type: application/json
```

**Contoh Request:**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: changeme" \
  -d '{
    "raw_text": "[28/05, 05:26] Rifan: order paket ayam bakar madu 10 pack\n[28/05, 06:01] Alfan: siap harganya 35k totalnya 350000 ya"
  }'
```

**Contoh Response `200 OK`:**

```json
{
  "status": "success",
  "results": [
    {
      "product_name": "Ayam Bakar Madu",
      "quantity": 10,
      "price_satuan": 35000,
      "subtotal": 350000,
      "confidence": "HIGH"
    }
  ],
  "total_akumulasi": 350000,
  "clean_text": "order paket ayam bakar madu 10 pack [SEP] siap harga 35000 total 350000"
}
```

---

## Skema Request & Response

### `PredictRequest`

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `raw_text` | `string` | ✅ | Teks mentah copy-paste dari WhatsApp. Minimal 5 karakter. Semua format timestamp didukung. |

### `OrderItem` (tiap item dalam `results`)

| Field | Tipe | Nullable | Keterangan |
|---|---|---|---|
| `product_name` | `string` | ❌ | Nama produk hasil ekstraksi NER. Bernilai `"unknown"` jika gagal dideteksi. |
| `quantity` | `integer` | ❌ | Jumlah pesanan. Selalu ≥ 1. |
| `price_satuan` | `integer` | ✅ | Harga per satuan dalam rupiah. `null` jika tidak disebutkan di chat. |
| `subtotal` | `integer` | ✅ | Hasil `quantity × price_satuan`. `null` jika `price_satuan` tidak ada. |
| `confidence` | `"HIGH"` \| `"MEDIUM"` \| `"LOW"` | ❌ | Tingkat kepercayaan hasil ekstraksi AI. |

### `PredictResponse`

| Field | Tipe | Keterangan |
|---|---|---|
| `status` | `string` | Selalu `"success"` pada response 200. |
| `results` | `OrderItem[]` | Daftar item transaksi yang diekstrak. |
| `total_akumulasi` | `integer` | Jumlah semua `subtotal` yang ada (non-null). |
| `clean_text` | `string` | Teks bersih setelah preprocessing, untuk keperluan audit/debug. |

---

## Error Codes

Semua response error menggunakan format yang seragam:

```json
{
  "error": true,
  "error_code": 1001,
  "message": "Deskripsi error"
}
```

| HTTP Status | `error_code` | Nama | Penyebab |
|---|---|---|---|
| `401` | `4010` | `UNAUTHORIZED` | Header `X-API-Key` tidak ada atau salah. |
| `422` | `1001` | `INVALID_INPUT` | `raw_text` terlalu pendek (< 5 karakter) atau gagal validasi Pydantic. |
| `500` | `1003` | `INFERENCE_FAILED` | Model gagal memproses input (error TensorFlow internal). |
| `500` | `1000` | `UNKNOWN` | Error tak terduga pada server. |
| `503` | `1002` | `MODEL_NOT_LOADED` | Model belum selesai diinisialisasi saat request masuk. |

---

## Edge Cases yang Ditangani

| Kondisi Input | Perilaku API |
|---|---|
| `raw_text` kosong atau < 5 karakter | `422` `error_code: 1001` |
| Teks hanya berisi timestamp/nama pengirim | `422` setelah preprocessing menghasilkan konten kosong |
| Harga tidak disebutkan di chat | `price_satuan: null`, `subtotal: null`, `confidence: "MEDIUM"` |
| Produk tidak dikenal oleh NER | `product_name: "unknown"`, sistem fallback regex mencoba mengekstrak dari konteks |
| Model belum selesai loading | `503` `error_code: 1002` |
| Gagal inferensi TF | `500` `error_code: 1003` |
| API key tidak ada atau salah | `401` `error_code: 4010` |
| Format timestamp beragam (iOS, Android, WhatsApp Web) | Semua dibersihkan otomatis oleh regex universal di preprocessing |
| Angka ribuan dengan format `35k`, `35rb`, `35ribu` | Dinormalisasi ke `35000` sebelum diumpankan ke model |

---

## Pipeline Preprocessing

Fungsi `prepare_model_input()` di `services/processing.py` menjalankan 7 langkah berurutan:

1. **Hapus timestamp universal** — Regex yang mendukung semua format tanggal/jam lintas OS (kurung siku, garis miring, titik, AM/PM, dll.)
2. **Strip nama pengirim** — Bagian sebelum `:` pertama dipotong secara dinamis
3. **Gabungkan baris dengan `[SEP]`** — Token pemisah domain percakapan untuk model
4. **Reduksi noise sapaan** — Kata-kata pengisi (mas, kak, om, halo, dll.) dibuang
5. **Normalisasi mata uang** — `Rp`, titik pemisah ribuan, `k/rb/ribu`, `jt/juta` → angka bulat
6. **Substitusi slang** — Kata slang dicocokan satu per satu dengan kamus CSV, over-correction dicegah
7. **Bersihkan sisa simbol** — Karakter non-alfanumerik dibuang, whitespace dirapikan

---

## Arsitektur Model AI

Model AI-1 (`chatkasir_model.keras`) adalah arsitektur **Transformer Encoder + BiLSTM** dengan **NER Head** multi-tag:

| Komponen | Detail |
|---|---|
| Tokenizer | HuggingFace WordPiece, vocab custom Bahasa Indonesia |
| Embedding | Dense embedding layer |
| Encoder | Custom `TransformerEncoder` (Multi-Head Attention + FFN + LayerNorm) |
| Sekuensial | Bidirectional LSTM |
| Output Head | Dense softmax — 7 tag BIO: `O`, `B-PROD`, `I-PROD`, `B-QTY`, `I-QTY`, `B-PRICE`, `I-PRICE` |
| Max Sequence | 128 token |

Model dimuat sebagai **singleton** (`ModelLoader.get_instance()`) agar tidak di-reload setiap request. Inferensi dijalankan via `run_in_executor` untuk menjaga event loop FastAPI tetap non-blocking.

---

## Sistem Confidence

Setiap item hasil prediksi mendapatkan label `confidence` yang dihitung di postprocessing:

| Kondisi | Confidence |
|---|---|
| `price_satuan` adalah `null` atau produk adalah `"unknown"` | `MEDIUM` |
| Ada total klaim di chat dan `grand_total_prediksi == total_chat` | `HIGH` |
| Ada total klaim di chat dan nilai berbeda | `LOW` |
| Tidak ada total klaim, softmax avg ≥ 90% | `HIGH` |
| Tidak ada total klaim, softmax avg ≥ 70% | `MEDIUM` |
| Tidak ada total klaim, softmax avg < 70% | `LOW` |

---

## Testing

### Jalankan semua test (tanpa stress test)

```bash
pytest tests/ -v --ignore=tests/tests_stress.py
```

### Integration tests endpoint `/predict` dan `/health`

```bash
pytest tests/tests_predict.py -v
```

### Unit tests pipeline preprocessing

```bash
pytest tests/tests_processing.py -v
```

### Unit tests kamus slang

```bash
pytest tests/tests_slang.py -v
```

### Stress test (memerlukan server aktif)

```bash
# Pastikan server sudah berjalan di port 8000 terlebih dahulu
pytest tests/tests_stress.py -m stress -v

# Atau jalankan langsung sebagai script Python
python tests/tests_stress.py --url http://localhost:8000 --api-key changeme --n 100 --workers 10
```

> **Catatan:** Test integration menggunakan `unittest.mock` untuk mem-patch TensorFlow dan `ModelLoader`, sehingga bisa berjalan di CI tanpa GPU atau instalasi TensorFlow penuh.

---

## Deploy ke Hugging Face Spaces

1. **Buat Space baru** di [huggingface.co/spaces](https://huggingface.co/spaces) dengan SDK **Docker**.

2. **Push repo ke Space:**

   ```bash
   git remote add space https://huggingface.co/spaces/<username>/chatkasir-ai-api
   git subtree push --prefix api-inference space main
   ```

3. **Model akan diunduh otomatis** dari Google Drive saat Space pertama kali start. Pastikan URL berikut sudah benar di `config.py` atau via environment variable:
   - `GDRIVE_MODEL_URL`
   - `GDRIVE_TOKENIZER_URL`
   - `GDRIVE_SLANG_URL`

   Alternatif — upload manual via Git LFS:

   ```bash
   git lfs install
   git lfs track "*.keras"
   cp ../../ai-model/assets/models/chatkasir_model.keras models/
   cp ../../ai-model/assets/tokenizers/tokenizer.json models/
   git add models/ .gitattributes
   git commit -m "add model files"
   git push space main
   ```

4. **Set secrets** di **Space Settings → Repository Secrets**:
   - `API_KEY` → key rahasia untuk autentikasi FS-2

5. Space otomatis build via `Dockerfile` dan tersedia di:
   `https://<username>-chatkasir-ai.hf.space`

---

## Keamanan

- **API Key Authentication** — Semua request ke `/predict` memerlukan header `X-API-Key`. Validasi dilakukan menggunakan `secrets.compare_digest()` untuk mencegah *timing attack*.
- **CORS** — Dikonfigurasi via `ALLOWED_ORIGINS`. Ganti dari `["*"]` ke domain spesifik saat production.
- **DEBUG Mode** — Jika `DEBUG=true`, autentikasi API key dinonaktifkan. **Jangan gunakan di production.**
- **Container Security** — Dockerfile menjalankan proses sebagai user ID `1000` (non-root) sesuai standar Hugging Face Spaces.
