"""
Router POST /predict — Menerima korpus teks WhatsApp dan mengembalikan response JSON komersial.
"""

import asyncio
from functools import partial
from fastapi import APIRouter, Depends

from app.core.errors import InvalidInputError
from app.core.security import require_api_key
from app.schemas.predict import OrderItem, PredictRequest, PredictResponse
from app.services.model_loader import ModelLoader
from app.services.processing import (
    postprocess,
    prepare_model_input,
    validate_input_length,
)

router = APIRouter()


@router.post("", response_model=PredictResponse)
async def predict(
    body: PredictRequest,
    _: str = Depends(require_api_key),
) -> PredictResponse:
    """
    Menerima raw chat teks kotor WhatsApp kasir, mengembalikan JSON restuful terstruktur bersih.
    """
    # 1. Validasi panjang batas karakter input awal
    validate_input_length(body.raw_text)

    # 2. Jalankan pipa pencucian teks cerdas universal regex
    teks_bersih = prepare_model_input(body.raw_text)

    if not teks_bersih.replace("[SEP]", "").strip():
        raise InvalidInputError(
            "Teks tidak mengandung konten informatif setelah dibersihkan dari timestamp."
        )

    # 3. Eksekusi model saraf (Jalur Non-Blocking Thread Pool Executor)
    # Menjaga event-loop FastAPI tetap responsif melayani klien lain saat TensorFlow memproses matrix
    loader = ModelLoader.get_instance()
    loop   = asyncio.get_event_loop()
    raw_output = await loop.run_in_executor(
        None,
        partial(loader.predict_single, teks_bersih),
    )

    # 4. Ambil hasil pengayaan nilai subtotal dan penentuan bendera confidence
    enriched_list = postprocess(raw_output, teks_bersih)

    # 5. Konversi data ke dalam baris skema OrderItem Pydantic
    items = [OrderItem(**pesanan) for pesanan in enriched_list]
    
    # Hitung nilai total transaksi riil keseluruhan belanja katering
    total_akumulasi = sum(item.subtotal for item in items if item.subtotal is not None)

    # 6. Kembalikan response final sukses dengan status 200 ke Express.js Backend
    return PredictResponse(
        status="success",
        results=items,
        total_akumulasi=total_akumulasi,
        clean_text=teks_bersih
    )