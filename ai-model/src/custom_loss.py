import tensorflow as tf

class MaskedNERLoss(tf.keras.losses.Loss):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(
            reduction='none',
            from_logits=False 
        )

    def call(self, y_true, y_pred, sample_weight=None):
        # 1. Hitung error mentah untuk setiap token/kata
        raw_loss = self.loss_fn(y_true, y_pred)

        # 2. Sistem Hukuman (Class Weighting)
        weights = tf.ones_like(tf.cast(y_true, tf.float32))

        # Tag PROD (ID: 1, 2) dihukum 5.0x lipat
        is_prod = tf.logical_or(tf.equal(y_true, 1), tf.equal(y_true, 2))
        weights = tf.where(is_prod, 5.0, weights) 

        # Tag QTY & PRICE (ID: 3 sampai 6) dihukum 3.0x lipat
        is_qty_price = tf.logical_and(tf.greater_equal(y_true, 3), tf.less_equal(y_true, 6))
        weights = tf.where(is_qty_price, 3.0, weights) 

        # 3. Padding Masking
        if sample_weight is not None:
            # Token [PAD] (0) akan memiliki bobot hukuman dikalikan 0 (Hukuman hangus/dibatalkan)
            weights = weights * tf.cast(sample_weight, tf.float32)

        # 4. Kalkulasi Final
        weighted_loss = raw_loss * weights
        
        # Hitung rata-rata error (+ 1e-7 mencegah error dibagi dengan nol)
        final_loss = tf.reduce_sum(weighted_loss) / (tf.reduce_sum(weights) + 1e-7)

        return final_loss