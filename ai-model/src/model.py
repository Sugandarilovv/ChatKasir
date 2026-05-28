# =================================================================
# UNIT UTAMA ARSITEKTUR: TRANSFORMER + BiLSTM + NER HEAD
# =================================================================
import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, Dense, MultiHeadAttention, LayerNormalization, Dropout, Bidirectional, LSTM
from tensorflow.keras.models import Model

# Decorator registrasi biner Keras agar file .keras mengenali layer kustom ini
@tf.keras.utils.register_keras_serializable()
class TransformerEncoder(tf.keras.layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1, **kwargs):
        super(TransformerEncoder, self).__init__(**kwargs)
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.rate = rate
        self.supports_masking = True

        # Inisialisasi arsitektur internal sub-layer
        self.att = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential([Dense(ff_dim, activation="relu"), Dense(embed_dim)])
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(rate)
        self.dropout2 = Dropout(rate)

    # Mencegah UserWarning Keras 3 saat proses load_model
    def build(self, input_shape):
        self.att.build(input_shape, input_shape)
        self.ffn.build(input_shape)
        self.layernorm1.build(input_shape)
        self.layernorm2.build(input_shape)
        super(TransformerEncoder, self).build(input_shape)

    def call(self, inputs, training=False, mask=None):
        padding_mask = tf.cast(mask[:, tf.newaxis, :], dtype=tf.int32) if mask is not None else None
        attn_output = self.att(inputs, inputs, attention_mask=padding_mask)
        attn_output = self.dropout1(attn_output, training=training)
        
        # Residual Connection 1
        out1 = self.layernorm1(inputs + attn_output)
        
        # Feed Forward Network
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        
        # Residual Connection 2
        return self.layernorm2(out1 + ffn_output)

    def get_config(self):
        config = super().get_config()
        config.update({
            "embed_dim": self.embed_dim,
            "num_heads": self.num_heads,
            "ff_dim": self.ff_dim,
            "rate": self.rate
        })
        return config

# Fungsi pembangun struktur arsitektur model
def build_model(vocab_size, max_length, num_tags, embed_dim=128, num_heads=4, ff_dim=256):
    inputs = Input(shape=(max_length,), name="input_ids")

    # Layer Embedding (mask_zero=True untuk otomatisasi penanganan padding)
    x = Embedding(input_dim=vocab_size, output_dim=embed_dim, mask_zero=True)(inputs)
    
    # 2x Transformer Encoder Block untuk penangkapan konteks global chat
    x = TransformerEncoder(embed_dim, num_heads, ff_dim)(x)
    x = TransformerEncoder(embed_dim, num_heads, ff_dim)(x)

    # Bidirectional LSTM untuk mengunci konsistensi urutan label BIO
    lstm_output = Bidirectional(LSTM(64, return_sequences=True))(x)

    # Output Head: Klasifikasi Softmax untuk 7 Tag kelas NER
    ner_output = Dense(num_tags, activation='softmax', name="ner_output")(lstm_output)

    return Model(inputs=inputs, outputs=ner_output)

# 🌟 [FIX PROTECTION]: Mencegah auto-running parameter kosong saat modul di-import
if __name__ == "__main__":
    # Contoh inisialisasi lokal untuk validasi testing arsitektur
    model_uji = build_model(vocab_size=10000, max_length=128, num_tags=7)
    model_uji.name = "chatkasir_model"
    model_uji.summary()