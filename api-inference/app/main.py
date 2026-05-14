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
    import os
    import gdown
    import zipfile
    import json
    import shutil

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

            # === SCRIPT BEDAH MODEL (ANTI-BUG KERAS 3) ===
            if path.endswith(".keras"):
                print("Membedah file .keras untuk menghapus 'quantization_config'...")
                temp_dir = "temp_keras_unzip"
                with zipfile.ZipFile(path, 'r') as z:
                    z.extractall(temp_dir)
                
                config_path = os.path.join(temp_dir, "config.json")
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        config_data = json.load(f)
                        
                    # Fungsi rekursif untuk menghapus quantization_config di semua layer
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
                
                # Zip kembali model yang sudah bersih
                os.remove(path)
                with zipfile.ZipFile(path, 'w') as z:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            filepath = os.path.join(root, file)
                            arcname = os.path.relpath(filepath, temp_dir)
                            z.write(filepath, arcname)
                shutil.rmtree(temp_dir)
                print("Bedah model selesai, siap digunakan!")

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
