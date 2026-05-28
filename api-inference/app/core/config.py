from __future__ import annotations

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App meta ──────────────────────────────────────────────────────────────
    APP_NAME:    str  = "AI2 API - ChatKasir"
    APP_VERSION: str  = "2.0"
    DEBUG:       bool = False
    
    # Default ke port 7860 untuk Hugging Face Spaces
    PORT:        int  = int(os.getenv("PORT", 7860))

    # ── Security ──────────────────────────────────────────────────────────────
    API_KEY: str = "changeme"

    # ── Model — path lokal (hasil download dari GDrive) ───────────────────────
    # tf.keras.load_model() dan Tokenizer.from_file() hanya menerima path lokal,
    # BUKAN url. File didownload dulu oleh download_assets() di main.py.
    MODEL_PATH:       str = "models/model.keras"
    TOKENIZER_PATH:   str = "models/tokenizer.json"
    MAX_SEQUENCE_LEN: int = 128

    # ── Data ──────────────────────────────────────────────────────────────────
    SLANG_DICT_PATH: str = "data/final/slang_utama.csv"

    # ── GDrive URLs — sumber download asset ───────────────────────────────────
    # Format: https://drive.google.com/uc?id=<FILE_ID>
    GDRIVE_MODEL_URL:     str = "https://drive.google.com/uc?id=1xdVp5x48D-3WXhofRxUmjl6SRYh6EDyz"
    GDRIVE_TOKENIZER_URL: str = "https://drive.google.com/uc?id=1kkwRYlbHFDGXzVPMiYNx-j1Ktjv0wNHM"
    
    # Diselaraskan dengan ID file yang terbukti valid di Notebook 03
    GDRIVE_SLANG_URL:     str = "https://drive.google.com/uc?id=1Ov6cFYB_7J0lGfVYdvm7lByTI0-V36hI"

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["*"]

settings = Settings()