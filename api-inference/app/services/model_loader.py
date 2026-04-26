"""
ModelLoader — singleton yang memuat model Keras AI-1 (Rifan) dan
mengekspos method predict_single untuk satu teks bersih.

Arsitektur model (dari AI-1 README):
  - Embedding → Bidirectional LSTM → tiga output head
  - Product head  : Softmax (klasifikasi produk)
  - Quantity head : ReLU (regresi, dibulatkan ke int)
  - Price head    : ReLU (rupiah penuh, hasil denormalisasi ÷1000 saat training)

Input ke ModelLoader sudah berupa teks bersih (setelah preprocessing.prepare_model_input).
Tokenisasi dan padding dilakukan di sini menggunakan tokenizer yang disimpan bersama model.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from app.core.config import settings
from app.core.errors import InferenceFailedError, ModelNotLoadedError

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Singleton yang memuat model Keras dan tokenizer satu kali saat startup.
    Dipakai via ModelLoader.get_instance().predict_single(teks_bersih).
    """

    _model: Optional[Any] = None        # tf.keras.Model
    _tokenizer: Optional[Any] = None    # tf.keras.preprocessing.text.Tokenizer
    _product_classes: Optional[list] = None  # daftar nama produk (label encoder)

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    @classmethod
    def get_instance(cls) -> "ModelLoader":
        if cls._model is None:
            cls._load_model()
        return cls()

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._model is not None

    @classmethod
    def reset(cls) -> None:
        """Lepas model dari memory (untuk testing atau graceful shutdown)."""
        cls._model = None
        cls._tokenizer = None
        cls._product_classes = None

    # ── Internal ──────────────────────────────────────────────────────────────

    @classmethod
    def _load_model(cls) -> None:
        try:
            import tensorflow as tf  # type: ignore

            # 1. Load model Keras
            logger.info("Memuat model dari %s …", settings.MODEL_PATH)
            cls._model = tf.keras.models.load_model(settings.MODEL_PATH)
            logger.info("Model berhasil dimuat.")

            # 2. Load tokenizer (JSON) — disimpan AI-1 bersama model
            import os
            if os.path.exists(settings.TOKENIZER_PATH):
                with open(settings.TOKENIZER_PATH, encoding="utf-8") as f:
                    tokenizer_config = json.load(f)
                cls._tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(
                    json.dumps(tokenizer_config)
                )
                logger.info("Tokenizer berhasil dimuat dari %s.", settings.TOKENIZER_PATH)

                # 3. Muat daftar produk (label classes) jika ada
                classes_path = settings.TOKENIZER_PATH.replace("tokenizer.json", "product_classes.json")
                if os.path.exists(classes_path):
                    with open(classes_path, encoding="utf-8") as f:
                        cls._product_classes = json.load(f)
                    logger.info("Product classes dimuat: %d kelas.", len(cls._product_classes))
            else:
                logger.warning(
                    "Tokenizer tidak ditemukan di '%s'. "
                    "Inferensi akan gagal sampai tokenizer tersedia.",
                    settings.TOKENIZER_PATH,
                )

        except FileNotFoundError:
            logger.warning(
                "Model tidak ditemukan di '%s'. "
                "Inferensi akan gagal sampai model ditempatkan di sana.",
                settings.MODEL_PATH,
            )
        except Exception as exc:
            logger.exception("Error tak terduga saat memuat model: %s", exc)
            raise ModelNotLoadedError(str(exc)) from exc

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict_single(self, teks_bersih: str) -> dict:
        """
        Jalankan inferensi untuk satu teks bersih.

        Parameters
        ----------
        teks_bersih:
            Teks sudah dipreprocess — tanpa timestamp, sudah dinormalisasi slang,
            format: "bang 2 nasi goreng ya [SEP] oke kak 1 nasi goreng 10rb total 20rb"

        Returns
        -------
        dict:  { "product": str, "quantity": int, "price_satuan": int }
        Nilai total dan confidence BELUM ada — dihitung oleh postprocessing.postprocess().
        """
        if self._model is None:
            raise ModelNotLoadedError()
        if self._tokenizer is None:
            raise ModelNotLoadedError("Tokenizer belum dimuat — pastikan tokenizer.json tersedia.")

        try:
            import numpy as np
            import tensorflow as tf  # type: ignore

            # Tokenisasi & padding
            seq = self._tokenizer.texts_to_sequences([teks_bersih])
            padded = tf.keras.preprocessing.sequence.pad_sequences(
                seq,
                maxlen=settings.MAX_SEQUENCE_LEN,
                padding="post",
                truncating="post",
            )

            # Prediksi — model memiliki tiga output head
            raw = self._model.predict(padded, verbose=0)

            # raw bisa berupa list [product_probs, quantity_val, price_val]
            # atau single array tergantung arsitektur final AI-1
            if isinstance(raw, (list, tuple)) and len(raw) == 3:
                product_probs, quantity_raw, price_raw = raw

                # Product: argmax → nama produk
                product_idx = int(np.argmax(product_probs[0]))
                product_name = (
                    self._product_classes[product_idx]
                    if self._product_classes and product_idx < len(self._product_classes)
                    else str(product_idx)
                )

                # Quantity: ReLU regression → bulatkan ke int, minimal 1
                quantity = max(1, round(float(quantity_raw[0][0])))

                # Price satuan: ReLU regression, sudah dalam rupiah penuh
                price_satuan = max(0, round(float(price_raw[0][0])))

            else:
                # Fallback: single output array (arsitektur sederhana)
                arr = np.array(raw).flatten()
                product_name = str(int(arr[0])) if len(arr) > 0 else "unknown"
                quantity = max(1, round(float(arr[1]))) if len(arr) > 1 else 1
                price_satuan = max(0, round(float(arr[2]))) if len(arr) > 2 else 0

            return {
                "product": product_name,
                "quantity": quantity,
                "price_satuan": price_satuan,
            }

        except ModelNotLoadedError:
            raise
        except Exception as exc:
            logger.exception("Inference error: %s", exc)
            raise InferenceFailedError(str(exc)) from exc
