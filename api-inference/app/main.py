import os
import logging
import zipfile
import json
import shutil
from contextlib import asynccontextmanager

import gdown
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import ErrorCode, register_exception_handlers
from app.routers import health, predict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse # <-- Tambahkan FileResponse
from fastapi.staticfiles import StaticFiles # <-- Tambahkan StaticFiles

# ── 1. INISIALISASI LOGGING PRODUKSI ──────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

# ── 2. AUTO-DOWNLOAD & HOTFIX PATCHER ─────────────────────────────────────────
def download_assets():
    """Mengunduh otomatis aset dan membedah biner Keras 3 dari atribut toksik."""
    os.makedirs("models", exist_ok=True)
    os.makedirs(os.path.dirname(settings.SLANG_DICT_PATH), exist_ok=True)

    links = {
        settings.MODEL_PATH:       settings.GDRIVE_MODEL_URL,
        settings.TOKENIZER_PATH:   settings.GDRIVE_TOKENIZER_URL,
        settings.SLANG_DICT_PATH:  settings.GDRIVE_SLANG_URL,
    }
    
    for path, url in links.items():
        if not os.path.exists(path):
            logger.info(f"[Startup] Mengunduh aset penting: {path} dari Google Drive...")
            try:
                gdown.download(url, path, quiet=False)
                logger.info(f"[Startup] Sukses mengamankan file lokal: {path}")
                
                # SCRIPT BEDAH MODEL KERAS 3
                # Mengekstrak metadata JSON dalam biner .keras dan menghapus quantization_config
                if path.endswith(".keras"):
                    logger.info("[Patcher] Memulai prosedur bedah biner model Keras...")
                    temp_dir = "temp_keras_unzip"
                    with zipfile.ZipFile(path, 'r') as z:
                        z.extractall(temp_dir)
                    
                    config_path = os.path.join(temp_dir, "config.json")
                    if os.path.exists(config_path):
                        with open(config_path, "r") as f:
                            config_data = json.load(f)
                            
                        # Fungsi rekursif pencari dan penghancur atribut toksik
                        def clean_config(d):
                            if isinstance(d, dict):
                                d.pop("quantization_config", None)
                                for k, v in d.items():
                                    clean_config(v)
                            elif isinstance(d, list):
                                for item in d:
                                    clean_config(item)
                                    
                        clean_config(config_data)
                        
                        with open(config_path, "w") as f:
                            json.dump(config_data, f)
                    
                    # Repackage / Zip kembali biner model yang sudah steril
                    os.remove(path)
                    with zipfile.ZipFile(path, 'w') as z:
                        for root, _, files in os.walk(temp_dir):
                            for file in files:
                                filepath = os.path.join(root, file)
                                arcname = os.path.relpath(filepath, temp_dir)
                                z.write(filepath, arcname)
                    
                    shutil.rmtree(temp_dir)
                    logger.info("[Patcher] Operasi bedah metadata sukses! Model siap dilahap RAM.")
            
            except Exception as e:
                logger.critical(f"[Startup Fatal] Gagal mengunduh/membedah aset dari {url}. Eror: {str(e)}")
                raise e

# ── 3. LIFESPAN MANAGEMENT ────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.model_loader import ModelLoader
    from app.services.processing import load_slang_dict

    download_assets()
    ModelLoader.get_instance()
    load_slang_dict()
    
    yield
    ModelLoader.reset()
    logger.info("[Shutdown] Memori model AI berhasil dilepas dengan aman.")

# ── 4. APP CONFIGURATION ──────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-2 Inference API - Mesin Utama ChatKasir.",
    lifespan=lifespan,
)

# ── 5. MIDDLEWARE CORS ────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 6. HANDLER VALIDASI PYDANTIC ──────────────────────────────────────────────
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
            "message":    f"Input validation failed: {detail}",
        },
    )

# ── 7. EXCEPTION HANDLERS ─────────────────────────────────────────────────────
register_exception_handlers(app)

# ── 8. API ROUTERS ENDPOINT ───────────────────────────────────────────────────
app.include_router(health.router, tags=["Monitoring"])
app.include_router(predict.router, prefix="/predict", tags=["Inference"])

# ── 9. MOUNTING STATIC HTML UI UNTUK HUGGING FACE SPACES ──────────────────────
# Cek apakah folder static ada. Jika ada, mount folder tersebut.
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", tags=["UI"])
async def serve_ui():
    """
    Jika folder static/index.html ada, render halamannya. 
    Jika tidak, kembalikan JSON info standar.
    """
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # Fallback JSON jika UI HTML tidak ditemukan
    return {
        "message": f"Welcome to {settings.APP_NAME} API v{settings.APP_VERSION}",
        "docs_url": "/docs",
        "status": "active"
    }