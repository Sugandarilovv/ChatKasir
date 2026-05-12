"""
ModelLoader — singleton yang memuat model Keras AI-1 (Rifan) dan
mengekspos method predict_single untuk satu teks bersih.

Perubahan v1.1:
  - Custom Layer TransformerEncoder didaftarkan ke custom_objects saat load
  - Tokenizer diganti ke HuggingFace WordPiece (tokenizers>=0.15.0)
  - Pembulatan harga ke kelipatan Rp500 terdekat
  - avg_conf_softmax dihitung dari probabilitas NER token produk

Catatan implementasi:
  Import tensorflow dan tokenizers dilakukan LAZY (di dalam fungsi _load_model
  dan predict_single) agar module ini bisa diimport saat unit/integration test
  tanpa TensorFlow terinstal di environment CI.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.core.config import settings
from app.core.errors import InferenceFailedError, ModelNotLoadedError

logger = logging.getLogger(__name__)

# Indeks kelas NER (sesuai urutan training AI-1)
_TAG_O      = 0
_TAG_B_PROD = 1
_TAG_I_PROD = 2

# Jika output price model (sebelum x1000) <= nilai ini → harga tidak disebutkan
_PRICE_NULL_THRESHOLD = 0.5   # < Rp 500 setelah x1000

_UNKNOWN_PRODUCT = "unknown"


def _build_transformer_encoder_class():
    """
    Bangun class TransformerEncoder secara lazy agar TF tidak diimport
    saat module di-load (penting untuk testability tanpa TF).
    """
    import tensorflow as tf
    from tensorflow.keras.layers import (
        Dense, Dropout, LayerNormalization, MultiHeadAttention,
    )

    class TransformerEncoder(tf.keras.layers.Layer):
        """
        Custom Transformer Encoder Layer — didaftarkan ke custom_objects saat
        load_model karena tidak ada di built-in Keras.

        Arsitektur (sesuai spesifikasi AI-1 Rifan):
          Embed 128, Multi-Head Attention (4 head), FFN 256, Dropout 0.1
        """

        def __init__(self, embed_dim=128, num_heads=4, ff_dim=256, rate=0.1, **kwargs):
            super(TransformerEncoder, self).__init__(**kwargs)
            self.att        = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
            self.ffn        = tf.keras.Sequential([
                Dense(ff_dim, activation="relu"),
                Dense(embed_dim),
            ])
            self.layernorm1 = LayerNormalization(epsilon=1e-6)
            self.layernorm2 = LayerNormalization(epsilon=1e-6)
            self.dropout1   = Dropout(rate)
            self.dropout2   = Dropout(rate)

        def call(self, inputs, training=False, mask=None):
            padding_mask = (
                tf.cast(mask[:, tf.newaxis, :], dtype=tf.int32)
                if mask is not None else None
            )
            attn_output = self.att(inputs, inputs, attention_mask=padding_mask)
            attn_output = self.dropout1(attn_output, training=training)
            out1        = self.layernorm1(inputs + attn_output)
            ffn_output  = self.ffn(out1)
            ffn_output  = self.dropout2(ffn_output, training=training)
            return self.layernorm2(out1 + ffn_output)

        def get_config(self):
            config = super().get_config()
            config.update({
                "embed_dim": self.att.key_dim,
                "num_heads": self.att.num_heads,
                "ff_dim":    self.ffn.layers[0].units,
                "rate":      self.dropout1.rate,
            })
            return config

    return TransformerEncoder


# ── ModelLoader ───────────────────────────────────────────────────────────────

class ModelLoader:
    """
    Singleton yang memuat model Keras dan tokenizer satu kali saat startup.
    Dipakai via ModelLoader.get_instance().predict_single(teks_bersih).
    """

    _model:     Optional[Any] = None
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
        cls._model     = None
        cls._tokenizer = None

    # ── Internal load ─────────────────────────────────────────────────────────

    @classmethod
    def _load_model(cls) -> None:
        try:
            import os

            import tensorflow as tf
            from tokenizers import Tokenizer

            TransformerEncoder = _build_transformer_encoder_class()

            # ── Model Keras ───────────────────────────────────────────────────
            logger.info("Memuat model dari %s ...", settings.MODEL_PATH)
            cls._model = tf.keras.models.load_model(
                settings.MODEL_PATH,
                custom_objects={"TransformerEncoder": TransformerEncoder},
                compile=False,
            )
            logger.info("Model berhasil dimuat.")

            # ── HuggingFace WordPiece Tokenizer ───────────────────────────────
            if os.path.exists(settings.TOKENIZER_PATH):
                cls._tokenizer = Tokenizer.from_file(settings.TOKENIZER_PATH)
                logger.info("Tokenizer dimuat dari %s.", settings.TOKENIZER_PATH)
            else:
                logger.warning(
                    "Tokenizer tidak ditemukan di '%s'.", settings.TOKENIZER_PATH
                )

        except FileNotFoundError:
            logger.warning(
                "Model tidak ditemukan di '%s'.", settings.MODEL_PATH
            )
        except Exception as exc:
            logger.exception("Error saat memuat model: %s", exc)
            raise ModelNotLoadedError(str(exc)) from exc

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict_single(self, teks_bersih: str) -> dict:
        """
        Jalankan inferensi untuk satu teks bersih.

        Returns
        -------
        dict:
            {
              "product":          str,        # nama produk atau "unknown"
              "quantity":         int,        # minimal 1
              "price_satuan":     int | None, # None jika harga tidak disebutkan
              "avg_conf_softmax": float,      # rata-rata confidence NER (0-100)
            }

        Notes
        -----
        - price_satuan dibulatkan ke kelipatan Rp500 terdekat
        - avg_conf_softmax dipakai postprocess untuk confidence saat tidak ada
          total di chat (HIGH >= 90, MEDIUM >= 70, LOW < 70)
        """
        if self._model is None:
            raise ModelNotLoadedError()
        if self._tokenizer is None:
            raise ModelNotLoadedError(
                "Tokenizer belum dimuat — pastikan tokenizer.json tersedia."
            )

        try:
            import numpy as np

            # ── Tokenisasi & padding (HuggingFace WordPiece) ─────────────────
            encoded = self._tokenizer.encode(teks_bersih)
            ids     = encoded.ids

            if len(ids) > settings.MAX_SEQUENCE_LEN:
                ids = ids[:settings.MAX_SEQUENCE_LEN]
            else:
                ids = ids + [0] * (settings.MAX_SEQUENCE_LEN - len(ids))

            padded = np.array([ids])

            # ── Inferensi ─────────────────────────────────────────────────────
            raw = self._model.predict(padded, verbose=0)
            product_probs, quantity_raw, price_raw = raw

            # ── Product: NER per-token + Softmax confidence ───────────────────
            tag_ids = np.argmax(product_probs[0], axis=-1)   # shape: (seq_len,)
            probs   = np.max(product_probs[0], axis=-1)       # shape: (seq_len,)

            product_token_ids: list[int] = []
            confidences: list[float]     = []

            for i, tag in enumerate(tag_ids):
                if tag in (_TAG_B_PROD, _TAG_I_PROD):
                    product_token_ids.append(ids[i])
                    confidences.append(float(probs[i]))

            product_name     = (
                self._tokenizer.decode(product_token_ids)
                if product_token_ids
                else _UNKNOWN_PRODUCT
            )
            avg_conf_softmax = float(np.mean(confidences) * 100) if confidences else 0.0

            # ── Quantity ──────────────────────────────────────────────────────
            quantity = max(1, int(round(float(quantity_raw[0][0]))))

            # ── Price: denormalisasi x1000, bulatkan ke Rp500 terdekat ───────
            price_raw_val = float(price_raw[0][0])

            if price_raw_val <= _PRICE_NULL_THRESHOLD:
                price_satuan: Optional[int] = None
                logger.debug(
                    "Price output %.4f <= threshold → price_satuan=None",
                    price_raw_val,
                )
            else:
                price_mentah = price_raw_val * 1000
                price_satuan = max(0, int(round(price_mentah / 500.0) * 500))

            return {
                "product":          product_name,
                "quantity":         quantity,
                "price_satuan":     price_satuan,
                "avg_conf_softmax": avg_conf_softmax,
            }

        except ModelNotLoadedError:
            raise
        except Exception as exc:
            logger.exception("Inference error: %s", exc)
            raise InferenceFailedError(str(exc)) from exc
