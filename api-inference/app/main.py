import os
from contextlib import asynccontextmanager

import gdown
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import ErrorCode, register_exception_handlers
from app.routers import health, predict


# ── Auto-download assets dari Google Drive ────────────────────────────────────

def download_assets():
    """
    Download model, tokenizer, dan kamus slang dari Google Drive jika belum ada.
    Dipanggil sekali saat startup — aman di-skip jika file sudah tersedia lokal.

    URL diambil dari settings (config.py / .env) sehingga bisa diganti tanpa
    menyentuh kode — cukup ubah GDRIVE_MODEL_URL, GDRIVE_TOKENIZER_URL, atau
    GDRIVE_SLANG_URL di file .env.

    Kenapa tetap pakai path lokal?
      tf.keras.models.load_model() dan Tokenizer.from_file() hanya bisa
      membaca file dari disk, bukan URL. Jadi alurnya selalu:
        GDrive URL  →  download via gdown  →  simpan ke path lokal
                    →  load dari path lokal
    """
    os.makedirs("models", exist_ok=True)
    os.makedirs("data/final", exist_ok=True)

    links = {
        settings.MODEL_PATH:      settings.GDRIVE_MODEL_URL,
        settings.TOKENIZER_PATH:  settings.GDRIVE_TOKENIZER_URL,
        settings.SLANG_DICT_PATH: settings.GDRIVE_SLANG_URL,
    }
    for path, url in links.items():
        if not os.path.exists(path):
            print(f"Downloading {path} dari {url} ...")
            gdown.download(url, path, quiet=False)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: download assets → muat model → muat slang. Shutdown: lepas model."""
    from app.services.model_loader import ModelLoader
    from app.services.processing import load_slang_dict

    download_assets()
    ModelLoader.get_instance()
    load_slang_dict()
    yield
    ModelLoader.reset()


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-2 Inference API untuk ChatKasir.\n\n"
        "Menerima raw chat WhatsApp dari FS-2 (Reihan), menjalankan preprocessing, "
        "inferensi model AI-1 (Rifan), dan postprocessing, lalu mengembalikan "
        "hasil transaksi lengkap ke backend.\n\n"
        "**Edge cases yang ditangani:**\n"
        "- `raw_text` < 5 karakter → 422 INVALID_INPUT\n"
        "- Harga tidak disebutkan → `price_satuan: null`, `total: null`\n"
        "- Produk tidak dikenal → `product: 'unknown'`, `confidence: MEDIUM`"
    ),
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Handler: Pydantic RequestValidationError → format INVALID_INPUT ───────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if errors:
        first  = errors[0]
        loc    = " → ".join(str(x) for x in first.get("loc", []))
        msg    = first.get("msg", "Input tidak valid")
        detail = f"{loc}: {msg}" if loc else msg
    else:
        detail = "Input tidak valid"

    return JSONResponse(
        status_code=422,
        content={
            "error":      True,
            "error_code": int(ErrorCode.INVALID_INPUT),
            "message":    detail,
        },
    )

# ── Custom exception handlers ─────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router,   tags=["Health"])
app.include_router(predict.router,  prefix="/predict", tags=["Predict"])
