"""
Router POST /predict — menerima raw chat WhatsApp, mengembalikan hasil prediksi.

Alur per request:
  1. Validasi API key (security dependency)
  2. Preprocess: hapus timestamp, normalisasi slang, gabung [SEP]
  3. Inferensi: model_loader.predict_single(teks_bersih)
     - Untuk multi-produk, model dipanggil sekali per produk yang terdeteksi
     - Saat ini: satu prediksi per request (AI-1 Rifan akan update jika ada perubahan)
  4. Postprocess: hitung total + confidence
  5. Kembalikan PredictResponse ke FS-2 (Reihan)
"""

from fastapi import APIRouter, Depends

from app.core.security import require_api_key
from app.schemas.predict import OrderItem, PredictRequest, PredictResponse
from app.services.model_loader import ModelLoader
from app.services.preprocessing import postprocess, prepare_model_input

router = APIRouter()


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

    **Response**
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

    **Confidence levels:**
    - `HIGH`   — total dari chat cocok dengan prediksi model, dapat langsung disimpan
    - `MEDIUM` — tidak ada total di chat untuk diverifikasi, tampilkan dengan opsi edit
    - `LOW`    — total di chat tidak cocok dengan prediksi, minta konfirmasi penjual
    """
    # ── Step 1: Preprocessing ─────────────────────────────────────────────
    teks_bersih = prepare_model_input(body.raw_text)

    # ── Step 2: Inferensi ─────────────────────────────────────────────────
    loader = ModelLoader.get_instance()
    raw_output = loader.predict_single(teks_bersih)

    # ── Step 3: Postprocessing ────────────────────────────────────────────
    # Hitung total dan tentukan confidence berdasarkan total di chat
    enriched = postprocess(raw_output, teks_bersih)

    # ── Step 4: Build response ────────────────────────────────────────────
    item = OrderItem(**enriched)
    return PredictResponse(results=[item], clean_text=teks_bersih)
