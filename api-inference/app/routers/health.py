from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.model_loader import ModelLoader

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Cek status API dan model.
    Tidak membutuhkan autentikasi — dipakai oleh monitoring dan load balancer.
    """
    loaded = ModelLoader.is_loaded()
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok" if loaded else "degraded",
            "model_loaded": loaded,
            "version": settings.APP_VERSION,
        },
    )
