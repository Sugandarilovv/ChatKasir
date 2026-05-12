from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import ErrorCode, register_exception_handlers
from app.routers import health, predict


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: muat model sekali. Shutdown: lepas dari memory."""
    from app.services.model_loader import ModelLoader
    from app.services.preprocessing import load_slang_dict

    ModelLoader.get_instance()
    load_slang_dict()   # pre-load ke cache agar request pertama tidak lambat
    yield
    ModelLoader.reset()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-2 Inference API untuk ChatKasir.\n\n"
        "Menerima raw chat WhatsApp dari FS-2 (Reihan), menjalankan preprocessing, "
        "inferensi model AI-1 (Rifan), dan postprocessing, lalu mengembalikan "
        "hasil transaksi lengkap (product, quantity, price_satuan, total, confidence) "
        "ke backend untuk ditampilkan di dashboard FS-1 (Alfan).\n\n"
        "**Edge cases yang ditangani:**\n"
        "- `raw_text` < 5 karakter → 422 INVALID_INPUT\n"
        "- Harga tidak disebutkan di chat → `price_satuan: null`, `total: null`\n"
        "- Produk tidak dikenal (NER gagal) → `product: 'unknown'`, `confidence: MEDIUM`"
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

# ── Custom handler: Pydantic RequestValidationError → format INVALID_INPUT ────
# Pydantic mengembalikan format error berbeda dengan error handler kita.
# Handler ini memastikan response 422 selalu menggunakan schema:
# { "error": true, "error_code": 1001, "message": "..." }
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Ambil pesan error pertama yang bermakna
    errors = exc.errors()
    if errors:
        first = errors[0]
        loc   = " → ".join(str(x) for x in first.get("loc", []))
        msg   = first.get("msg", "Input tidak valid")
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

# ── Custom exception handlers (AI2BaseException, generic) ─────────────────────
register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(predict.router, prefix="/predict", tags=["Predict"])
