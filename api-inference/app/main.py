from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.routers import health, predict


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: muat model sekali. Shutdown: lepas dari memory."""
    from app.services.model_loader import ModelLoader
    from app.services.preprocessing import load_slang_dict

    # Warm-up: muat model + kamus slang saat startup
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
        "ke backend untuk ditampilkan di dashboard FS-1 (Alfan)."
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

# ── Exception handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(predict.router, prefix="/predict", tags=["Predict"])
