from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App meta ──────────────────────────────────────────────────────────────
    APP_NAME:    str  = "AI2 API – ChatKasir"
    APP_VERSION: str  = "1.1.0"
    DEBUG:       bool = False

    # ── Security ──────────────────────────────────────────────────────────────
    API_KEY: str = "changeme"

    # ── Model — path lokal (hasil download dari GDrive) ───────────────────────
    # tf.keras.load_model() dan Tokenizer.from_file() hanya menerima path lokal,
    # BUKAN url. File didownload dulu oleh download_assets() di main.py.
    MODEL_PATH:       str = "models/model.keras"
    TOKENIZER_PATH:   str = "models/tokenizer.json"
    MAX_SEQUENCE_LEN: int = 64

    # ── Data ──────────────────────────────────────────────────────────────────
    SLANG_DICT_PATH: str = "../data/final/slang_utama.csv"

    # ── GDrive URLs — sumber download asset ───────────────────────────────────
    # Ubah nilai ini jika AI-1 (Rifan) upload ulang model ke GDrive yang baru.
    # Format: https://drive.google.com/uc?id=<FILE_ID>
    GDRIVE_MODEL_URL:     str = "https://drive.google.com/uc?id=1NgbF_aslZebTiCyVW3No3U2ysH1NmDye"
    GDRIVE_TOKENIZER_URL: str = "https://drive.google.com/uc?id=1i1TIsmeAI3EsVawzqmdZRQmCr3gtBhOG"
    GDRIVE_SLANG_URL:     str = "https://drive.google.com/uc?id=1G14C1qcqOp06Xs1HFiorE3Us_LLtaBs7"

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["*"]


settings = Settings()
