"""
ModelLoader — singleton yang memuat model Keras AI-1 (Rifan) dan
mengekspos method predict_single untuk satu teks bersih.

Perubahan v2.0 (Tahap 2 — Denny):
  - Model V2 hanya mengeluarkan 1 Matriks Besar NER Output (bukan 3 output)
  - Tag diperluas dari 3 menjadi 7: O, B-PROD, I-PROD, B-QTY, I-QTY,
    B-PRICE, I-PRICE
  - predict_single sekarang mengembalikan List[dict] (list_pesanan) untuk
    mendukung multi-item dalam satu chat
  - Algoritma Grouping/Pairing otomatis mengelompokkan token per produk

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
import re
from typing import Any, List, Optional

from app.core.config import settings
from app.core.errors import InferenceFailedError, ModelNotLoadedError

logger = logging.getLogger(__name__)

# ── Indeks Tag NER V2 (7 tag, sesuai desain training AI-1 Rifan) ──────────────
_TAG_O       = 0   # Outside — bukan entitas
_TAG_B_PROD  = 1   # Begin  — awal nama produk
_TAG_I_PROD  = 2   # Inside — lanjutan nama produk
_TAG_B_QTY   = 3   # Begin  — awal kuantitas
_TAG_I_QTY   = 4   # Inside — lanjutan kuantitas (angka multi-token)
_TAG_B_PRICE = 5   # Begin  — awal harga
_TAG_I_PRICE = 6   # Inside — lanjutan harga

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

    @tf.keras.utils.register_keras_serializable()
    class TransformerEncoder(tf.keras.layers.Layer):
        """
        Custom Transformer Encoder Layer — didaftarkan ke custom_objects saat
        load_model karena tidak ada di built-in Keras.

        Arsitektur (sesuai spesifikasi AI-1 Rifan):
          Embed 128, Multi-Head Attention (4 head), FFN 256, Dropout 0.1
        """

        def __init__(self, embed_dim=128, num_heads=4, ff_dim=256, rate=0.1, **kwargs):
            super(TransformerEncoder, self).__init__(**kwargs)
            self.supports_masking = True
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


# ── Helper: Parse Harga dari Teks Token ──────────────────────────────────────

def _parse_price_from_text(text: str) -> Optional[int]:
    """
    Parse nilai harga dari teks hasil decode token B-PRICE/I-PRICE.

    Menangani variasi:
        "10rb" -> 10000, "25000" -> 25000, "15k" -> 15000, "5 ribu" -> 5000

    Returns
    -------
    Harga dalam rupiah penuh (dibulatkan ke Rp500 terdekat), atau None
    jika tidak dapat di-parse atau nilainya 0.
    """
    match = re.search(r'(\d+)\s*(rb|ribu|k)?', text.strip(), re.IGNORECASE)
    if not match:
        return None
    angka  = int(match.group(1))
    satuan = match.group(2)
    if satuan and satuan.lower() in ('rb', 'ribu', 'k'):
        angka *= 1000
    if angka <= 0:
        return None
    # Bulatkan ke kelipatan Rp500 terdekat
    return max(0, int(round(angka / 500.0) * 500))


def _parse_qty_from_text(text: str) -> int:
    """Parse nilai kuantitas dari teks, mendukung angka dan ejaan huruf."""
    kamus_huruf = {
        "satu": 1, "sebiji": 1, "seporsi": 1, "sebungkus": 1, "segelas": 1, "sebotol": 1,
        "dua": 2, "loro": 2, "tiga": 3, "telu": 3, "empat": 4, "papat": 4, "lima": 5, "limo": 5,
        "setengah": 1
    }
    teks_bersih = text.lower().strip()
    if teks_bersih in kamus_huruf:
        return kamus_huruf[teks_bersih]

    match = re.search(r'\d+', teks_bersih)
    return max(1, int(match.group())) if match else 1


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

    def predict_single(self, teks_bersih: str) -> List[dict]:
        """
        Jalankan inferensi untuk satu teks bersih.

        Model V2 mengeluarkan 1 Matriks NER besar (shape: (1, seq_len, 7)).
        Menggunakan teknik Independent Extraction 3-Fase: panen entitas ke list
        terpisah, lalu mapping berdasarkan indeks.

        Returns
        -------
        List[dict]: list_pesanan, setiap elemen berisi:
            {
              "product":          str,        # nama produk atau "unknown"
              "quantity":         int,        # minimal 1
              "price_satuan":     int | None, # None jika harga tidak disebutkan
              "avg_conf_softmax": float,      # rata-rata confidence NER (0-100)
            }
        """
        if self._model is None:
            raise ModelNotLoadedError()
        if self._tokenizer is None:
            raise ModelNotLoadedError("Tokenizer belum dimuat.")

        try:
            import numpy as np

            # Tokenisasi (HuggingFace WordPiece)
            encoded = self._tokenizer.encode(teks_bersih)
            ids = encoded.ids
            if len(ids) > settings.MAX_SEQUENCE_LEN:
                ids = ids[:settings.MAX_SEQUENCE_LEN]
            else:
                ids = ids + [0] * (settings.MAX_SEQUENCE_LEN - len(ids))
            padded = np.array([ids])

            # Inferensi Model
            ner_probs = self._model.predict(padded, verbose=0)
            tag_ids = np.argmax(ner_probs[0], axis=-1)
            probs = np.max(ner_probs[0], axis=-1)

            # FASE 1 & 2: Ekstraksi Independen ke List Terpisah
            list_produk, list_qty, list_harga = [], [], []
            list_conf = []  # Menyimpan confidence rata-rata per produk

            temp_ids, temp_confs = [], []
            current_tag = None

            def _simpan_buffer(ids_array, conf_array, tag_jenis):
                if not ids_array: return
                decoded_text = self._tokenizer.decode(ids_array).strip()
                avg_conf = float(np.mean(conf_array) * 100) if conf_array else 0.0

                if tag_jenis == "PROD":
                    list_produk.append(decoded_text.title())
                    list_conf.append(avg_conf)
                elif tag_jenis == "QTY":
                    list_qty.append(_parse_qty_from_text(decoded_text))
                elif tag_jenis == "PRICE":
                    list_harga.append(_parse_price_from_text(decoded_text))

            for i, tag in enumerate(tag_ids):
                token_id = ids[i]
                if tag == _TAG_O:
                    if current_tag:
                        _simpan_buffer(temp_ids, temp_confs, current_tag)
                        temp_ids, temp_confs, current_tag = [], [], None
                    continue

                if tag in (_TAG_B_PROD, _TAG_B_QTY, _TAG_B_PRICE):
                    if current_tag:
                        _simpan_buffer(temp_ids, temp_confs, current_tag)
                    temp_ids = [token_id]
                    temp_confs = [float(probs[i])]

                    if tag == _TAG_B_PROD: current_tag = "PROD"
                    elif tag == _TAG_B_QTY: current_tag = "QTY"
                    elif tag == _TAG_B_PRICE: current_tag = "PRICE"

                elif tag in (_TAG_I_PROD, _TAG_I_QTY, _TAG_I_PRICE):
                    expected_current = None
                    if tag == _TAG_I_PROD: expected_current = "PROD"
                    elif tag == _TAG_I_QTY: expected_current = "QTY"
                    elif tag == _TAG_I_PRICE: expected_current = "PRICE"

                    if current_tag == expected_current:
                        temp_ids.append(token_id)
                        temp_confs.append(float(probs[i]))
                    else:
                        if current_tag:
                            _simpan_buffer(temp_ids, temp_confs, current_tag)
                        temp_ids = [token_id]
                        temp_confs = [float(probs[i])]
                        current_tag = expected_current

            # Flush sisa buffer di akhir kalimat
            if current_tag and temp_ids:
                _simpan_buffer(temp_ids, temp_confs, current_tag)

            # FASE 3: Relational Asosiasi (Mapping Berdasarkan Indeks)
            list_pesanan: List[dict] = []

            # Jika user tidak memasukkan produk sama sekali
            if not list_produk:
                return [{
                    "product": _UNKNOWN_PRODUCT,
                    "quantity": 1,
                    "price_satuan": None,
                    "avg_conf_softmax": 0.0,
                }]

            for i in range(len(list_produk)):
                # Mapping QTY & PRICE ke produk berdasarkan index.
                # Total harga akhir dari penjual misal "55rb" otomatis tersaring
                # karena elemen list_harga ke-3 tidak punya pasangan di list_produk.
                qty = list_qty[i] if i < len(list_qty) else 1
                price = list_harga[i] if i < len(list_harga) else None
                conf = list_conf[i]

                list_pesanan.append({
                    "product": list_produk[i] if list_produk[i] else _UNKNOWN_PRODUCT,
                    "quantity": qty,
                    "price_satuan": price,
                    "avg_conf_softmax": conf,
                })

            logger.debug(
                "[predict_single] %d item terdeteksi: %s",
                len(list_pesanan),
                [p["product"] for p in list_pesanan],
            )
            return list_pesanan

        except Exception as exc:
            logger.exception("Inference error: %s", exc)
            raise InferenceFailedError(str(exc)) from exc
