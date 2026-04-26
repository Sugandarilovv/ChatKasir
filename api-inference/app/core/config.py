from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App meta ─────────────────────────────────────────────────────────────
    APP_NAME: str = "AI2 API – ChatKasir"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Security ─────────────────────────────────────────────────────────────
    API_KEY: str = "changeme"

    # ── Model ────────────────────────────────────────────────────────────────
    # Path ke file model Keras (.keras) yang dihasilkan AI-1 (Rifan)
    MODEL_PATH: str = "models/model.keras"

    # Path ke tokenizer yang disimpan bersama model (JSON format)
    TOKENIZER_PATH: str = "models/tokenizer.json"

    # Panjang sequence maksimum (harus sama dengan saat training)
    MAX_SEQUENCE_LEN: int = 128

    # ── Data ─────────────────────────────────────────────────────────────────
    # Path ke kamus slang dari DS-1 (Faradi)
    SLANG_DICT_PATH: str = "../data/final/slang_utama.csv"

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["*"]


settings = Settings()
