from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

# ── Request Schema ────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    """Body payload yang dikirim oleh backend Express.js ke POST /predict."""

    raw_text: str = Field(
        ...,
        min_length=5,
        description=(
            "Teks mentah obrolan WhatsApp hasil copy-paste kasir. "
            "Mendukung segala format timestamp lintas OS yang akan dicuci otomatis."
        ),
        examples=[
            "[28/05, 05:26] Rifan: order paket ayam bakar madu 10 pack\n"
            "[28/05, 06:01] Alfan: siap harganya 35k"
        ],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "raw_text": (
                    "[28/05, 05:26] Rifan: order paket ayam bakar madu 10 pack\n"
                    "[28/05, 06:01] Alfan: siap harganya 35k"
                )
            }
        }
    }

# ── Per-Item Result Schema ────────────────────────────────────────────────────
class OrderItem(BaseModel):
    """
    Satu baris item transaksi hasil ekstraksi AI setelah post-processing.
    """

    # 🌟 [SINKRONISASI KEY]: Bermigrasi ke product_name sesuai Notebook 03
    product_name: str = Field(
        ...,
        description="Nama produk/menu kuliner. Bernilai 'unknown' jika gagal diidentifikasi.",
    )
    quantity: int = Field(
        ...,
        ge=1,
        description="Jumlah pesanan murni dalam bentuk integer.",
    )
    price_satuan: Optional[int] = Field(
        None,
        ge=0,
        description="Harga satuan item dalam rupiah. null jika tidak disebutkan.",
    )
    # 🌟 [SINKRONISASI KEY]: Bermigrasi ke subtotal sesuai Notebook 03
    subtotal: Optional[int] = Field(
        None,
        ge=0,
        description="Subtotal hasil perkalian quantity x price_satuan.",
    )
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = Field(
        ...,
        description=(
            "HIGH: Sinkron dengan nota chat. "
            "MEDIUM: Tidak ada pembanding harga total di chat. "
            "LOW: Hasil hitung AI berselisih dengan klaim nota chat penjual."
        ),
    )

# ── Response Schema ───────────────────────────────────────────────────────────
class PredictResponse(BaseModel):
    """Struktur response final yang dikembalikan ke Express.js & Frontend."""

    status: str = "success"
    results: List[OrderItem] = Field(
        ...,
        description="Daftar item pesanan kuliner yang berhasil diurai model AI.",
    )
    # 🌟 [FITUR TAMBAHAN]: Total akumulasi belanja langsung saji untuk kasir toko
    total_akumulasi: int = Field(
        ...,
        ge=0,
        description="Total nilai nominal keseluruhan belanja pada satu nota chat.",
    )
    clean_text: str = Field(
        ...,
        description="Teks korpus bersih setelah pembuangan timestamp, noise, dan normalisasi slang.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "success",
                "results": [
                    {
                        "product_name": "Ayam Bakar Madu",
                        "quantity": 10,
                        "price_satuan": 35000,
                        "subtotal": 350000,
                        "confidence": "HIGH",
                    }
                ],
                "total_akumulasi": 350000,
                "clean_text": "pesan paket ayam bakar madu 10 bungkus [SEP] siap harga 35000",
            }
        }
    }