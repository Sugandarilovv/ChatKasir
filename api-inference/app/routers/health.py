import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.model_loader import ModelLoader
from app.services.processing import get_slang_stats

# Inisialisasi Logger produksi untuk mencetak log sistem
logger = logging.getLogger("uvicorn.error")
router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Cek status kesehatan API, kesiapan model AI, dan ketersediaan kamus slang.
    Tidak membutuhkan autentikasi - dipakai monitoring.
    """
    try:
        # 1. Cek status apakah biner otak model AI sudah termuat di memori runtime
        model_loaded = ModelLoader.is_loaded()
        
        # 2. Cek status database slang dengan jaring pengaman internal
        try:
            slang_stats = get_slang_stats()
        except Exception as e:
            logger.error(f"Gagal membaca statistik kamus slang: {str(e)}")
            slang_stats = {"status": "error", "message": "Slang dictionary file missing or corrupted"}

        # 3. Penentuan HTTP Status Code secara Dinamis
        # Jika model gagal dimuat, wajib return 503 (Service Unavailable) agar sistem cloud tahu 
        # kontainer sedang tidak sehat dan harus memicu alert/restart otomatis.
        status_code = 200 if model_loaded else 503
        
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "ok" if model_loaded else "degraded",
                "model_loaded": model_loaded,
                "version": settings.APP_VERSION,
                "slang_dict": slang_stats,
            },
        )
        
    except Exception as exc:
        # Jaring pengaman utama jika terjadi kegagalan kritikal pada monitoring engine itu sendiri
        logger.error(f"Kritikal eror sistem pada health check: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "model_loaded": False,
                "version": settings.APP_VERSION,
                "message": "Internal infrastructure monitoring engine failure",
            },
        )