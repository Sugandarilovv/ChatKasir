from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ── Request ───────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    """Body yang dikirim FS-2 (Reihan) ke POST /predict."""

    raw_text: str = Field(
        ...,
        min_length=5,
        description=(
            "Teks mentah percakapan WhatsApp yang di-copy-paste pengguna. "
            "Boleh mengandung timestamp format WhatsApp — "
            "akan dibersihkan otomatis oleh preprocessing."
        ),
        examples=[
            "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya\n"
            "[07.44, 22/4/2026] Penjual: oke kak 1 nasi goreng 10rb totalnya 20rb ya"
        ],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "raw_text": (
                    "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya\n"
                    "[07.44, 22/4/2026] Penjual: oke kak 1 nasi goreng 10rb totalnya 20rb ya"
                )
            }
        }


# ── Per-produk result ─────────────────────────────────────────────────────────

class OrderItem(BaseModel):
    """
    Satu baris transaksi — satu produk.
    Untuk chat multi-produk, response berisi list dari OrderItem.
    """

    product: str = Field(
        ...,
        description="Nama produk dalam huruf kecil, konsisten dengan dataset food."
    )
    quantity: int = Field(
        ...,
        ge=1,
        description="Jumlah pesanan — hasil prediksi model, dibulatkan ke int."
    )
    price_satuan: int = Field(
        ...,
        ge=0,
        description="Harga SATUAN dalam rupiah penuh (bukan ribuan, bukan total)."
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total harga = quantity × price_satuan, dihitung oleh postprocessing."
    )
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        ...,
        description=(
            "HIGH: total dari chat cocok dengan prediksi model. "
            "LOW: ada total di chat tapi tidak cocok — perlu konfirmasi penjual. "
            "MEDIUM: tidak ada total di chat untuk diverifikasi."
        ),
    )


# ── Response ──────────────────────────────────────────────────────────────────

class PredictResponse(BaseModel):
    """Response POST /predict yang dikirim ke FS-2 (Reihan)."""

    results: List[OrderItem] = Field(
        ...,
        description=(
            "Satu item untuk chat 1 produk; "
            "lebih dari satu item untuk chat multi-produk."
        ),
    )
    clean_text: str = Field(
        ...,
        description="Teks yang sudah dibersihkan (tanpa timestamp, sudah dinormalisasi slang)."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "product": "nasi goreng",
                        "quantity": 2,
                        "price_satuan": 10000,
                        "total": 20000,
                        "confidence": "HIGH",
                    }
                ],
                "clean_text": "bang 2 nasi goreng ya [SEP] oke kak 1 nasi goreng 10rb totalnya 20rb ya",
            }
        }
