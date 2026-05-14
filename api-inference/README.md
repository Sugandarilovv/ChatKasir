---
title: Chatkasir Ai
emoji: 📊
colorFrom: blue
colorTo: gray
sdk: docker
pinned: false
license: mit
short_description: AI model for transaction chat extraction
---

# AI-2 Inference API — ChatKasir

FastAPI yang menerima raw chat WhatsApp dari FS-2 (Reihan), menjalankan preprocessing, inferensi model AI-1 (Rifan), dan postprocessing, lalu mengembalikan hasil transaksi ke backend.

---

## Daftar Isi

- [AI-2 Inference API — ChatKasir](#ai-2-inference-api--chatkasir)
  - [Daftar Isi](#daftar-isi)
  - [Arsitektur \& Alur](#arsitektur--alur)
  - [Struktur Folder](#struktur-folder)
  - [Cara Menjalankan Lokal](#cara-menjalankan-lokal)
  - [Environment Variables](#environment-variables)
  - [Edge Cases yang Ditangani](#edge-cases-yang-ditangani)
  - [Testing](#testing)
  - [Deploy ke Hugging Face Spaces](#deploy-ke-hugging-face-spaces)

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
│   │   └── processing.py  # Preprocessing + postprocessing pipeline
│   └── main.py             # FastAPI app, CORS, exception handlers
├── tests/
│   ├── tests_predict.py    # Integration tests (30+ skenario)
│   ├── test_stress.py      # Stress test 100 request paralel
│   └── tests_processing.py
├── Dockerfile              # Untuk deploy ke Hugging Face Spaces
├── .env.example
├── requirements.txt
└── API_CONTRACT.md
```

---

## Cara Menjalankan Lokal

```bash
cd api-inference
pip install -r requirements.txt

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
| `MODEL_PATH` | `models/model.keras` | Path ke model Keras AI-1 |
| `TOKENIZER_PATH` | `models/tokenizer.json` | Path ke tokenizer JSON |
| `MAX_SEQUENCE_LEN` | `64` | Harus sama dengan saat training |
| `SLANG_DICT_PATH` | `data/final/slang_utama.csv` | Kamus slang dari DS-1 (Faradi) |
| `GDRIVE_MODEL_URL` | *(lihat config.py)* | URL Google Drive untuk auto-download model |
| `GDRIVE_TOKENIZER_URL` | *(lihat config.py)* | URL Google Drive untuk auto-download tokenizer |
| `GDRIVE_SLANG_URL` | *(lihat config.py)* | URL Google Drive untuk auto-download slang dict |
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

---

## Deploy ke Hugging Face Spaces

1. Buat Space baru di [huggingface.co/spaces](https://huggingface.co/spaces), pilih **Docker** sebagai SDK.

2. Push repo ke Space:
   ```bash
   git remote add space https://huggingface.co/spaces/<username>/chatkasir-ai-api
   git subtree push --prefix api-inference space main
   ```

3. Model & tokenizer akan **otomatis didownload** dari Google Drive saat Space pertama kali start (via `download_assets()` di `main.py`). Pastikan URL di `config.py` atau environment variable sudah benar:
   - `GDRIVE_MODEL_URL`
   - `GDRIVE_TOKENIZER_URL`
   - `GDRIVE_SLANG_URL`

   Atau, upload manual via Git LFS:
   ```bash
   git lfs install
   git lfs track "*.keras"
   cp ../../ai-model/assets/models/chatkasir_model.keras models/
   cp ../../ai-model/assets/tokenizers/tokenizer.json models/
   git add models/ .gitattributes
   git commit -m "add model files"
   git push space main
   ```

4. Set secrets di **Space Settings → Repository Secrets**:
   - `API_KEY` → key rahasia untuk autentikasi FS-2

5. Space akan otomatis build menggunakan `Dockerfile` dan tersedia di:
   `https://<username>-chatkasir-ai.hf.space`
