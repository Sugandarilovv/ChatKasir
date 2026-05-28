"""
ModelLoader — singleton yang memuat model Keras AI-1 (Rifan) dan
mengekspos method predict_single untuk satu teks bersih.

Perubahan v2.0 (Tahap 2 — Denny & Rifan Refactor):
  - Model V2 hanya mengeluarkan 1 Matriks Besar NER Output (bukan 3 output)
  - Tag diperluas dari 3 menjadi 7: O, B-PROD, I-PROD, B-QTY, I-QTY, B-PRICE, I-PRICE
  - predict_single mengembalikan List[dict] dengan key "product_name" untuk sinkronisasi API
  - Ditambahkan fungsi build() pada TransformerEncoder untuk kepatuhan Keras 3
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
        """

        def __init__(self, embed_dim=128, num_heads=4, ff_dim=256, rate=0.1, **kwargs):
            super(TransformerEncoder, self).__init__(**kwargs)
            
            # 🌟 Mengunci variabel internal ke self untuk standarisasi get_config
            self.embed_dim = embed_dim
            self.num_heads = num_heads
            self.ff_dim = ff_dim
            self.rate = rate
            self.supports_masking = True

            # Inisialisasi arsitektur internal sub-layer
            self.att        = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
            self.ffn        = tf.keras.Sequential([
                Dense(ff_dim, activation="relu"),
                Dense(embed_dim),
            ])
            self.layernorm1 = LayerNormalization(epsilon=1e-6)
            self.layernorm2 = LayerNormalization(epsilon=1e-6)
            self.dropout1   = Dropout(rate)
            self.dropout2   = Dropout(rate)

        # 🌟 [FIX KUNCI SINKRONISASI]: Wajib diimplementasikan agar Keras 3 bebas dari UserWarning
        def build(self, input_shape):
            self.att.build(input_shape, input_shape)
            self.ffn.build(input_shape)
            self.layernorm1.build(input_shape)
            self.layernorm2.build(input_shape)
            super(TransformerEncoder, self).build(input_shape)

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
                "embed_dim": self.embed_dim,
                "num_heads": self.num_heads,
                "ff_dim":    self.ff_dim,
                "rate":      self.rate,
            })
            return config

    return TransformerEncoder


# ── Helper: Parse Harga & Kuantitas dari Teks Token (Versi Robust V2) ─────────

def _parse_price_from_text(text: str) -> Optional[int]:
    """
    Parse nilai harga dari teks hasil decode token B-PRICE/I-PRICE.
    Mendukung konversi otomatis satuan ribuan (k/rb) hingga jutaan (jt/juta).
    """
    # Bersihkan tanda baca titik/koma pemisah ribuan agar tersisa karakter murni
    teks = text.lower().replace('.', '').replace(',', '').strip()
    
    # Mendukung multiplier nominal jutaan untuk paket katering besar
    if 'jt' in teks or 'juta' in teks:
        angka = re.sub(r'[^0-9]', '', teks)
        return int(angka) * 1000000 if angka else None
        
    if 'rb' in teks or 'ribu' in teks or 'k' in teks:
        angka = re.sub(r'[^0-9]', '', teks)
        return int(angka) * 1000 if angka else None
        
    # Ambil nilai angka murni (tanpa distorsi pembulatan paksa kelipatan 500)
    angka = re.sub(r'[^0-9]', '', teks)
    return int(angka) if angka and int(angka) > 0 else None


def _parse_qty_from_text(text: str) -> int:
    """
    Parse nilai kuantitas dari teks, mendukung penulisan angka murni,
    kombinasi ejaan teks pelengkap, hingga frase multi-kata (e.g., 'dua bungkus').
    """
    # Sinkronisasi komprehensif kosakata kuantitas dari Notebook 03
    kamus_kuantitas = {
        "satu": 1, "sebiji": 1, "seporsi": 1, "sebungkus": 1,
        "segelas": 1, "semangkok": 1, "sepiring": 1, "sebotol": 1,
        "secangkir": 1, "setusuk": 1, "sepotong": 1, "siji": 1, "sebox": 1, "sekotak": 1,
        "secup": 1, "satu cup": 1, "se-pack": 1, "semika": 1, "se-thinwall": 1, "sepaket": 1,
        "porsi gede": 1, "porsi jumbo": 1, "porsi kecil": 1, "setengah porsi": 1, "setengah": 1,
        "dua": 2, "loro": 2, "dua bungkus": 2, "dua porsi": 2, "dua mangkuk": 2, "dua pack": 2, "dua box": 2, "dua mika": 2, "dua thinwall": 2, "dua gelas": 2, "dua botol": 2, "dua cup": 2, "dua plastik": 2,
        "tiga": 3, "telu": 3, "tiga bungkus": 3, "tiga porsi": 3, "tiga piring": 3, "tiga gelas": 3, "tiga botol": 3, "tiga cup": 3,
        "empat": 4, "mpat": 4, "pat": 4, "papat": 4,
        "lima": 5, "limo": 5, "lima mangkuk": 5, "lima porsi": 5, "lima pack": 5, "lima box": 5, "lima cup": 5,
        "enam": 6, "enem": 6, "nam": 6, "tujuh": 7, "pitu": 7, "delapan": 8, "lapan": 8, "wolu": 8,
        "sembilan": 9, "sanga": 9, "songo": 9, "sepuluh": 10, "sepulu": 10,
        "sebelas": 11, "seblas": 11, "dua belas": 12, "selusin": 12
    }
    
    teks = text.lower().strip()
    if teks in kamus_kuantitas:
        return kamus_kuantitas[teks]
        
    # Fallback: Cari komponen digit jika pembeli menulis angka murni biasa (e.g., "10 pack" -> 10)
    angka = re.sub(r'[^0-9]', '', teks)
    return int(angka) if angka else 1


# ── ModelLoader ───────────────────────────────────────────────────────────────

class ModelLoader:
    """
    Singleton yang memuat model Keras dan tokenizer satu kali saat startup.
    """

    _model:     Optional[Any] = None
    _tokenizer: Optional[Any] = None

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
        cls._model     = None
        cls._tokenizer = None

    @classmethod
    def _load_model(cls) -> None:
        try:
            import os
            import tensorflow as tf
            from tokenizers import Tokenizer

            TransformerEncoder = _build_transformer_encoder_class()

            logger.info("Memuat model dari %s ...", settings.MODEL_PATH)
            cls._model = tf.keras.models.load_model(
                settings.MODEL_PATH,
                custom_objects={"TransformerEncoder": TransformerEncoder},
                compile=False,
            )
            logger.info("Model berhasil dimuat.")

            if os.path.exists(settings.TOKENIZER_PATH):
                cls._tokenizer = Tokenizer.from_file(settings.TOKENIZER_PATH)
                logger.info("Tokenizer dimuat dari %s.", settings.TOKENIZER_PATH)
            else:
                logger.warning("Tokenizer tidak ditemukan di '%s'.", settings.TOKENIZER_PATH)

        except FileNotFoundError:
            logger.warning("Model tidak ditemukan di '%s'.", settings.MODEL_PATH)
        except Exception as exc:
            logger.exception("Error saat memuat model: %s", exc)
            raise ModelNotLoadedError(str(exc)) from exc

    def predict_single(self, teks_bersih: str) -> List[dict]:
        """
        Jalankan inferensi untuk satu teks bersih.
        """
        if self._model is None or self._tokenizer is None:
            raise ModelNotLoadedError("Model atau Tokenizer belum dimuat sempurna.")

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

            # Inferensi Jaringan Saraf Model AI
            ner_probs = self._model.predict(padded, verbose=0)
            tag_ids = np.argmax(ner_probs[0], axis=-1)
            probs = np.max(ner_probs[0], axis=-1)

            list_produk, list_qty, list_harga = [], [], []
            list_conf = []

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

            if current_tag and temp_ids:
                _simpan_buffer(temp_ids, temp_confs, current_tag)

            # FASE 3: Relational Asosiasi (Mapping Berdasarkan Indeks)
            list_pesanan: List[dict] = []

            # 1. Bersihkan produk dari spasi kosong
            list_produk_bersih = [p for p in list_produk if p.strip()]
            list_conf_bersih = [c for p, c in zip(list_produk, list_conf) if p.strip()]
            
            # 2. Hapus nilai None dari list_harga agar harga yang gagal diparse tidak menggeser indeks
            list_harga_bersih = [h for h in list_harga if h is not None]

            # 3. Penentuan Acuan Baris (Base Length) yang AMAN
            # Selalu utamakan jumlah produk. JIKA DAN HANYA JIKA AI buta produk (0), baru pakai qty/harga
            if len(list_produk_bersih) > 0:
                base_len = len(list_produk_bersih)
            else:
                base_len = max(len(list_qty), len(list_harga_bersih))

            if base_len == 0:
                return [{
                    "product_name": _UNKNOWN_PRODUCT,
                    "quantity": 1,
                    "price_satuan": None,
                    "avg_conf_softmax": 0.0,
                }]

            # 4. Pasangkan data secara linier dan potong data berlebih (seperti Total Tagihan)
            for i in range(base_len):
                prod = list_produk_bersih[i] if i < len(list_produk_bersih) else _UNKNOWN_PRODUCT
                qty = list_qty[i] if i < len(list_qty) else 1
                price = list_harga_bersih[i] if i < len(list_harga_bersih) else None
                conf = list_conf_bersih[i] if i < len(list_conf_bersih) else 0.0

                list_pesanan.append({
                    "product_name": prod,
                    "quantity": qty,
                    "price_satuan": price,
                    "avg_conf_softmax": conf,
                })

            return list_pesanan
        
        except Exception as exc:
            logger.exception("Inference error: %s", exc)
            raise InferenceFailedError(str(exc)) from exc