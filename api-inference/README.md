# AI2 API

FastAPI inference service that wraps a TensorFlow / Keras model behind a secure REST API.

## Quick Start

```bash
# 1. Clone & enter directory
git clone <repo-url> ai2-api && cd ai2-api

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env – set API_KEY and MODEL_PATH

# 4. Place your model
cp /path/to/your/model.keras models/model.keras

# 5. Run
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Running Tests

```bash
pytest tests/ -v
```

## Daftar Isi

1. [Arsitektur & Alur](#arsitektur--alur)
2. [Struktur Folder](#struktur-folder)
3. [Cara Menjalankan Lokal](#cara-menjalankan-lokal)
4. [Environment Variables](#environment-variables)
5. [Edge Cases yang Ditangani](#edge-cases-yang-ditangani)
6. [Testing](#testing)
7. [Deploy ke Hugging Face Spaces](#deploy-ke-hugging-face-spaces)

---

## Arsitektur & Alur

```
FS-2 (Reihan) → POST /predict
  │
  ├── [1] Validasi input (< 5 karakter → 422 INVALID_INPUT)
  ├── [2] Preprocessing  (hapus timestamp, lowercase, normalisasi slang, [SEP])
  ├── [3] Inferensi async (run_in_executor agar event loop tidak diblok TF)
  │         Model AI-1: Transformer Encoder + BiLSTM NER + 2 regresi head
  │         Output: product_tags (NER), quantity (float), price_raw (float ÷1000)
  ├── [4] Postprocessing (NER → string, price ×1000, total, confidence)
  └── [5] Response → FS-2 → Dashboard Alfan
```

---

## Struktur Folder

```
api-inference/
├── app/
│   ├── core/
│   │   ├── config.py       # Settings via pydantic-settings + .env
│   │   ├── errors.py       # Custom exceptions + handler registration
│   │   └── security.py     # API key dependency
│   ├── routers/
│   │   ├── health.py       # GET /health
│   │   └── predict.py      # POST /predict
│   ├── schemas/
│   │   └── predict.py      # PredictRequest, OrderItem, PredictResponse
│   ├── services/
│   │   ├── model_loader.py   # Singleton TF model + NER extraction
│   │   └── preprocessing.py  # Preprocessing + postprocessing pipeline
│   └── main.py             # FastAPI app, CORS, exception handlers
├── tests/
│   ├── tests_predict.py    # Integration tests (30+ skenario)
│   ├── test_stress.py      # Stress test 100 request paralel
│   └── teats_preprocessing.py
├── .env.example
├── requiments.txt
└── API_CONTRACT.md
```

---

## Cara Menjalankan Lokal

```bash
cd api-inference
pip install -r requiments.txt

# Salin dan edit konfigurasi
cp .env.example .env
# Edit MODEL_PATH, TOKENIZER_PATH, API_KEY di .env

uvicorn app.main:app --reload --port 8000
```

Dokumentasi interaktif: `http://localhost:8000/docs`

---

## Environment Variables

| Variabel | Default | Keterangan |
|---|---|---|
| `API_KEY` | `changeme` | **Wajib diganti** sebelum deploy |
| `MODEL_PATH` | `models/chatkasir_model.keras` | Path ke model Keras AI-1 |
| `TOKENIZER_PATH` | `models/tokenizer.json` | Path ke tokenizer JSON |
| `MAX_SEQUENCE_LEN` | `64` | Harus sama dengan saat training |
| `SLANG_DICT_PATH` | `../data/final/slang_utama.csv` | Kamus slang dari DS-1 (Faradi) |
| `ALLOWED_ORIGINS` | `["*"]` | CORS origins (ganti saat production) |
| `DEBUG` | `false` | Mode debug FastAPI |

---

## Edge Cases yang Ditangani

| Kondisi | Perilaku API |
|---|---|
| `raw_text` < 5 karakter | `422` `{ "error": true, "error_code": 1001, "message": "..." }` |
| Harga tidak disebutkan di chat | `price_satuan: null`, `total: null`, `confidence: "MEDIUM"` |
| Produk tidak dikenal (NER gagal) | `product: "unknown"`, `confidence: "MEDIUM"` |
| Model belum di-load | `503` `error_code: 1002` |
| Inferensi gagal | `500` `error_code: 1003` |
| API key salah / tidak ada | `401` `error_code: 4010` |

---

## Testing

```bash
# Unit + integration tests
pytest tests/tests_predict.py -v

# Semua tests termasuk preprocessing
pytest tests/ -v --ignore=tests/test_stress.py

# Stress test (butuh server aktif di localhost:8000)
pytest tests/test_stress.py -m stress -v

# Atau jalankan stress test langsung sebagai script
python tests/test_stress.py --url http://localhost:8000 --api-key changeme --n 100 --workers 10
```
## Project Structure

```
ai2-api/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── core/
│   │   ├── config.py        # Settings via pydantic-settings
│   │   ├── errors.py        # Custom exceptions & error codes
│   │   └── security.py      # API key auth dependency
│   ├── routers/
│   │   ├── predict.py       # POST /predict
│   │   └── health.py        # GET /health
│   ├── schemas/
│   │   └── predict.py       # Pydantic request/response models
│   └── services/
│       └── model_loader.py  # TF model singleton & inference
├── models/                  # Place your .keras file here
├── tests/
│   └── test_predict.py      # Pytest tests
├── docs/
├── API_CONTRACT.md
├── requirements.txt
├── .env.example
└── README.md
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `API_KEY` | `changeme` | Secret key for `X-API-Key` header |
| `MODEL_PATH` | `models/model.keras` | Path to the Keras model file |
| `DEBUG` | `false` | Enable debug mode |
| `ALLOWED_ORIGINS` | `["*"]` | CORS allowed origins |

# ── Security ──────────────────────────────────────────────────────────────────
# WAJIB diganti sebelum deploy. Set sebagai HF Spaces Secret (Settings → Secrets).
API_KEY=changeme

# ── Model (path relatif dari dalam container) ─────────────────────────────────
# Letakkan file model di folder models/ lalu commit ke repo HF Spaces
MODEL_PATH=models/chatkasir_model.keras
TOKENIZER_PATH=models/tokenizer.json
MAX_SEQUENCE_LEN=64

# ── Data ──────────────────────────────────────────────────────────────────────
SLANG_DICT_PATH=data/final/slang_utama.csv

# ── CORS ──────────────────────────────────────────────────────────────────────
# Ganti dengan domain frontend production (FS-1 Alfan)
# Contoh: ALLOWED_ORIGINS=["https://chatkasir.netlify.app"]
ALLOWED_ORIGINS=["*"]

# ── App ───────────────────────────────────────────────────────────────────────
DEBUG=false
