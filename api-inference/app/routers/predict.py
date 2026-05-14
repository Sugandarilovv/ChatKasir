"""
Router POST /predict — menerima raw chat WhatsApp, mengembalikan hasil prediksi.

Alur per request:
  1. Validasi API key (security dependency)
  2. Validasi panjang input (< 5 karakter → INVALID_INPUT error_code 1001)
  3. Preprocess: hapus timestamp, normalisasi slang, gabung [SEP]
  4. Inferensi async: model_loader.predict_single(teks_bersih) via run_in_executor
     agar event loop FastAPI tidak diblokir oleh komputasi TensorFlow
  5. Postprocess: hitung total + confidence (handle price=null, product=unknown)
  6. Kembalikan PredictResponse ke FS-2 (Reihan)

Edge cases yang ditangani:
  - raw_text < 5 karakter  → 422 INVALID_INPUT (error_code 1001)
  - price tidak disebutkan → price_satuan: null, total: null, confidence: MEDIUM
  - produk tidak dikenal   → product: "unknown", confidence: MEDIUM
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

_MIN_TEXT_LEN = 5


@router.post("", response_model=PredictResponse)
async def predict(
    body: PredictRequest,
    _: str = Depends(require_api_key),
) -> PredictResponse:
    """
    Terima raw chat WhatsApp, kembalikan list transaksi yang diprediksi.

    **Request body**
    ```json
    {
      "raw_text": "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya\\n[07.44, 22/4/2026] Penjual: oke kak 1 nasi goreng 10rb totalnya 20rb ya"
    }
    ```

    **Response sukses**
    ```json
    {
      "results": [
        {
          "product": "nasi goreng",
          "quantity": 2,
          "price_satuan": 10000,
          "total": 20000,
          "confidence": "HIGH"
        }
      ],
      "clean_text": "bang 2 nasi goreng ya [SEP] oke kak 1 nasi goreng 10rb totalnya 20rb ya"
    }
    ```

    **Response — harga tidak disebutkan**
    ```json
    {
      "results": [{"product": "es teh", "quantity": 2, "price_satuan": null, "total": null, "confidence": "MEDIUM"}],
      "clean_text": "..."
    }
    ```

    **Response — produk tidak dikenal**
    ```json
    {
      "results": [{"product": "unknown", "quantity": 1, "price_satuan": null, "total": null, "confidence": "MEDIUM"}],
      "clean_text": "..."
    }
    ```

    **Confidence levels:**
    - `HIGH`   — total dari chat cocok dengan prediksi model
    - `MEDIUM` — harga/produk tidak dikenali, atau tidak ada total di chat
    - `LOW`    — total di chat tidak cocok dengan prediksi model
    """
    # ── Step 1: Validasi panjang input ────────────────────────────────────────
    # Dilakukan eksplisit di sini agar error_code = 1001 (INVALID_INPUT) konsisten,
    # bukan format default Pydantic 422 yang berbeda strukturnya.
    validate_input_length(body.raw_text)

    # ── Step 2: Preprocessing ─────────────────────────────────────────────────
    teks_bersih = prepare_model_input(body.raw_text)

    # Jika setelah preprocessing teks kosong (misal: hanya timestamp tanpa isi)
    if not teks_bersih.strip():
        raise InvalidInputError(
            "Teks tidak mengandung konten setelah preprocessing. "
            "Pastikan chat berisi pesan dari Pembeli dan/atau Penjual."
        )

    # ── Step 3: Inferensi (async — tidak memblokir event loop) ───────────────
    # TensorFlow predict() bersifat CPU-bound/blocking. Jalankan di thread pool
    # agar FastAPI dapat melayani request lain selagi model berjalan.
    loader = ModelLoader.get_instance()
    loop   = asyncio.get_event_loop()
    raw_output = await loop.run_in_executor(
        None,
        partial(loader.predict_single, teks_bersih),
    )

    # ── Step 4: Postprocessing ────────────────────────────────────────────────
    enriched = postprocess(raw_output, teks_bersih)

    # ── Step 5: Build response ────────────────────────────────────────────────
    item = OrderItem(**enriched)
    return PredictResponse(results=[item], clean_text=teks_bersih)
