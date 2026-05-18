from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.model_loader import ModelLoader
from app.services.processing import get_slang_stats

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Cek status API, model, dan kamus slang.
    Tidak membutuhkan autentikasi — dipakai oleh monitoring dan load balancer.
    """
    loaded = ModelLoader.is_loaded()
    slang  = get_slang_stats()
    return JSONResponse(
        status_code=200,
        content={
            "status":       "ok" if loaded else "degraded",
            "model_loaded": loaded,
            "version":      settings.APP_VERSION,
            "slang_dict":   slang,
        },
    )
