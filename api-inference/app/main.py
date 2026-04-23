from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.routers import predict, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown events."""
    from app.services.model_loader import ModelLoader
    ModelLoader.get_instance()          # warm-up: load model once at startup
    yield
    # (optional) cleanup on shutdown
    ModelLoader.reset()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI2 Inference API – powered by TensorFlow / Keras",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
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
