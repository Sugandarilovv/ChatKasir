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
MAX_SEQUENCE_LEN=128

# ── Data ──────────────────────────────────────────────────────────────────────
SLANG_DICT_PATH=data/final/slang_utama.csv

# ── CORS ──────────────────────────────────────────────────────────────────────
# Ganti dengan domain frontend production (FS-1 Alfan)
# Contoh: ALLOWED_ORIGINS=["https://chatkasir.vercel.app"]
ALLOWED_ORIGINS=["*"]

# ── App ───────────────────────────────────────────────────────────────────────
DEBUG=false
