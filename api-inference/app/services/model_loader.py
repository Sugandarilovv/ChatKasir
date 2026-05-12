"""
ModelLoader — singleton yang memuat model Keras AI-1 (Rifan) dan
mengekspos method predict_single untuk satu teks bersih.

Arsitektur model (dari AI-1 README — Transformer + Task-Specific Branches):
  - Shared Backbone  : Transformer Encoder (Embed 128, FFN 256)
  - Product Branch   : BiLSTM + Dense(Softmax) → per-token NER tags (O, B-PROD, I-PROD)
  - Quantity Branch  : Dense Regresi (ReLU) → angka desimal, dibulatkan ke int
  - Price Branch     : Dense Regresi (ReLU) → harga dinormalisasi ÷1000 saat training
                       → WAJIB dikalikan ×1000 saat inferensi untuk mendapatkan rupiah penuh

Output shape model:
  product_probs : (1, seq_len, 3)   — probabilitas per token untuk [O, B-PROD, I-PROD]
  quantity_raw  : (1, 1)            — nilai regresi quantity
  price_raw     : (1, 1)            — nilai regresi price (dalam ribuan, perlu ×1000)

Edge cases yang ditangani:
  - Produk tidak dikenal (semua tag = O)    → product = "unknown"
  - Harga tidak disebutkan (price_raw ≈ 0)  → price_satuan = None (sinyal ke postprocess)
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from app.core.config import settings
from app.core.errors import InferenceFailedError, ModelNotLoadedError

logger = logging.getLogger(__name__)

# Indeks kelas NER (sesuai urutan training AI-1)
_TAG_O      = 0
_TAG_B_PROD = 1
_TAG_I_PROD = 2

# Threshold harga: jika output model (sebelum ×1000) ≤ nilai ini,
# dianggap "harga tidak disebutkan" → price_satuan = None
_PRICE_NULL_THRESHOLD = 0.5   # artinya < Rp 500 setelah ×1000

# Nama fallback jika NER tidak berhasil menemukan produk
_UNKNOWN_PRODUCT = "unknown"


class ModelLoader:
    """
    Singleton yang memuat model Keras dan tokenizer satu kali saat startup.
    Dipakai via ModelLoader.get_instance().predict_single(teks_bersih).
    """

    _model: Optional[Any] = None
    _tokenizer: Optional[Any] = None

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

    # ── Internal ──────────────────────────────────────────────────────────────

    @classmethod
    def _load_model(cls) -> None:
        try:
            import tensorflow as tf  # type: ignore

            logger.info("Memuat model dari %s …", settings.MODEL_PATH)
            cls._model = tf.keras.models.load_model(settings.MODEL_PATH)
            logger.info("Model berhasil dimuat.")

            import os
            if os.path.exists(settings.TOKENIZER_PATH):
                with open(settings.TOKENIZER_PATH, encoding="utf-8") as f:
                    tokenizer_config = json.load(f)
                cls._tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(
                    json.dumps(tokenizer_config)
                )
                logger.info("Tokenizer berhasil dimuat dari %s.", settings.TOKENIZER_PATH)
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

    # ── NER Helper ────────────────────────────────────────────────────────────

    def _extract_product_from_tags(
        self,
        tag_ids: "list[int]",
        token_ids: "list[int]",
    ) -> str:
        """
        Konversi sequence tag NER + token IDs → nama produk sebagai string.

        Proses:
          1. Cari posisi token dengan tag B-PROD atau I-PROD.
          2. Untuk tiap posisi tersebut, lookup kata di tokenizer.index_word.
          3. Gabungkan kata-kata yang berdekatan (span) menjadi nama produk.
          4. Kembalikan "unknown" jika tidak ada token bertag produk.

        Parameters
        ----------
        tag_ids   : list[int]  — argmax per token, panjang = seq_len
        token_ids : list[int]  — ID token (sebelum padding zero-filtered)
        """
        if self._tokenizer is None:
            return _UNKNOWN_PRODUCT

        index_word = getattr(self._tokenizer, "index_word", {})
        product_tokens: list[str] = []

        for pos, (tag, tok_id) in enumerate(zip(tag_ids, token_ids)):
            if tok_id == 0:
                # Token padding — skip
                continue
            if tag in (_TAG_B_PROD, _TAG_I_PROD):
                word = index_word.get(tok_id, "")
                if word and word != "[SEP]":
                    product_tokens.append(word)

        if not product_tokens:
            logger.debug("NER: tidak ada token bertag B-PROD/I-PROD → fallback 'unknown'")
            return _UNKNOWN_PRODUCT

        return " ".join(product_tokens)

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
        dict: { "product": str, "quantity": int, "price_satuan": int | None }

        Notes
        -----
        - price_satuan = None  → harga tidak disebutkan di chat (bukan 0)
        - product = "unknown"  → NER gagal mengidentifikasi nama produk
        - total dan confidence belum ada — dihitung oleh postprocessing.postprocess()
        """
        if self._model is None:
            raise ModelNotLoadedError()
        if self._tokenizer is None:
            raise ModelNotLoadedError("Tokenizer belum dimuat — pastikan tokenizer.json tersedia.")

        try:
            import numpy as np
            import tensorflow as tf  # type: ignore

            # ── Tokenisasi & padding ──────────────────────────────────────
            seq = self._tokenizer.texts_to_sequences([teks_bersih])
            padded = tf.keras.preprocessing.sequence.pad_sequences(
                seq,
                maxlen=settings.MAX_SEQUENCE_LEN,
                padding="post",
                truncating="post",
            )
            token_ids: list[int] = padded[0].tolist()

            # ── Inferensi ─────────────────────────────────────────────────
            raw = self._model.predict(padded, verbose=0)

            if isinstance(raw, (list, tuple)) and len(raw) == 3:
                product_probs, quantity_raw, price_raw = raw

                # ── Product: NER per-token (shape: 1 × seq_len × 3) ──────
                # argmax per posisi token → [O=0, B-PROD=1, I-PROD=2]
                tag_ids: list[int] = np.argmax(product_probs[0], axis=-1).tolist()
                product_name = self._extract_product_from_tags(tag_ids, token_ids)

                # ── Quantity: regresi, minimal 1 ─────────────────────────
                quantity = max(1, round(float(quantity_raw[0][0])))

                # ── Price: regresi dinormalisasi ÷1000 saat training ──────
                # → kalikan ×1000 untuk mendapatkan rupiah penuh
                price_raw_val = float(price_raw[0][0])
                if price_raw_val <= _PRICE_NULL_THRESHOLD:
                    # Harga tidak disebutkan di chat (model belajar label -1 → output ≈ 0)
                    price_satuan: Optional[int] = None
                    logger.debug(
                        "Price output %.4f ≤ threshold %.4f → price_satuan=None",
                        price_raw_val, _PRICE_NULL_THRESHOLD,
                    )
                else:
                    price_satuan = max(0, round(price_raw_val * 1000))

            else:
                # Fallback: single output array (arsitektur non-standar)
                logger.warning(
                    "Output model tidak berformat 3-tuple. "
                    "Menggunakan fallback parser. Raw type: %s", type(raw)
                )
                arr = np.array(raw).flatten()
                product_name = _UNKNOWN_PRODUCT
                quantity     = max(1, round(float(arr[1]))) if len(arr) > 1 else 1
                raw_price    = float(arr[2]) if len(arr) > 2 else 0.0
                price_satuan = max(0, round(raw_price * 1000)) if raw_price > _PRICE_NULL_THRESHOLD else None

            return {
                "product":      product_name,
                "quantity":     quantity,
                "price_satuan": price_satuan,
            }

        except ModelNotLoadedError:
            raise
        except Exception as exc:
            logger.exception("Inference error: %s", exc)
            raise InferenceFailedError(str(exc)) from exc
