# =================================================================
# LOSS FUNCTION KUSTOM: MASKED CLASS-WEIGHTED NER LOSS
# =================================================================
import tensorflow as tf

@tf.keras.utils.register_keras_serializable()
class MaskedNERLoss(tf.keras.losses.Loss):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Reduction='none' agar nilai loss per token kata bisa dimanipulasi manual
        self.loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(
            reduction='none',
            from_logits=False
        )

    def call(self, y_true, y_pred, sample_weight=None):
        # 1. Hitung loss dasar cross-entropy untuk setiap kata
        raw_loss = self.loss_fn(y_true, y_pred)

        # 2. Ambil bobot default awal 1.0 untuk semua kata
        weights = tf.ones_like(tf.cast(y_true, tf.float32))

        # 3. Penerapan Hukum Bobot Dynamic (Menanggulangi Class Imbalance)
        # Tag PROD (ID 1, 2) diberikan hukuman 2.0x lipat lebih berat jika salah tebak
        is_prod = tf.logical_or(tf.equal(y_true, 1), tf.equal(y_true, 2))
        weights = tf.where(is_prod, 2.0, weights)

        # Tag QTY & PRICE (ID 3 s/d 6) diberikan hukuman 1.5x lipat lebih berat
        is_qty_price = tf.logical_and(tf.greater_equal(y_true, 3), tf.less_equal(y_true, 6))
        weights = tf.where(is_qty_price, 1.5, weights)

        # 4. Padding Masking (Hapus hukuman komputasi pada token kosong [PAD])
        if sample_weight is not None:
            weights = weights * tf.cast(sample_weight, tf.float32)

        # 5. Kalkulasi Akhir weighted loss
        weighted_loss = raw_loss * weights

        # Reduksi akhir: Total loss dibagi total bobot kata valid (ditambah epsilon 1e-7)
        final_loss = tf.reduce_sum(weighted_loss) / (tf.reduce_sum(weights) + 1e-7)
        return final_loss

# Instansiasi Objek Global Siap Pakai untuk Training/Fine-Tuning
ner_loss_function = MaskedNERLoss()

# Optimizer Adam dengan Learning Rate stabil standar pemrosesan NLP teks
optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)

print("Custom Loss 'MaskedNERLoss' dan Optimizer berhasil disiapkan.")