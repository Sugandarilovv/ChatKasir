import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, Dense, Dropout, LayerNormalization, MultiHeadAttention, Bidirectional, LSTM
from tensorflow.keras.models import Model

# Decorator agar Keras tetap mengenali layer "TransformerEncoder" saat model di-load
@tf.keras.utils.register_keras_serializable()
class TransformerEncoder(tf.keras.layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1, **kwargs):
        super(TransformerEncoder, self).__init__(**kwargs)
        self.supports_masking = True
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.rate = rate

        self.att = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential([Dense(ff_dim, activation="relu"), Dense(embed_dim)])
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(rate)
        self.dropout2 = Dropout(rate)

    def call(self, inputs, training=False, mask=None):
        # Masking untuk mengabaikan padding [PAD]
        padding_mask = tf.cast(mask[:, tf.newaxis, :], dtype=tf.int32) if mask is not None else None
        
        attn_output = self.att(inputs, inputs, attention_mask=padding_mask)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        
        return self.layernorm2(out1 + ffn_output)

    def get_config(self):
        config = super().get_config()
        config.update({
            "embed_dim": self.embed_dim,
            "num_heads": self.num_heads,
            "ff_dim": self.ff_dim,
            "rate": self.rate,
        })
        return config

def build_model(vocab_size, max_length, num_tags):
    """
    Fungsi opsional untuk membangun arsitektur model dari awal 
    (jika sewaktu-waktu ingin ditraining ulang dari skrip Python murni).
    """
    embed_dim = 128
    num_heads = 4
    ff_dim = 256

    inputs = Input(shape=(max_length,), name="input_ids")
    x = Embedding(input_dim=vocab_size, output_dim=embed_dim, mask_zero=True)(inputs)
    x = TransformerEncoder(embed_dim, num_heads, ff_dim)(x)
    x = TransformerEncoder(embed_dim, num_heads, ff_dim)(x)
    lstm_output = Bidirectional(LSTM(64, return_sequences=True))(x)
    ner_output = Dense(num_tags, activation='softmax', name="ner_output")(lstm_output)

    return Model(inputs=inputs, outputs=ner_output)