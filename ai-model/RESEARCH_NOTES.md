# Research Notes - AI-1 Model Architect

Catatan studi referensi ilmiah yang memengaruhi keputusan desain teoretis arsitektur akhir model ChatKasir (Update: V2 Unified Hybrid Architecture).

---

## 1. Sequence Labeling & NER - Lample et al. (2016)

**Judul:** Neural Architectures for Named Entity Recognition  
**Link:** https://arxiv.org/abs/1603.01360

### Insight Utama
- Tugas ekstraksi informasi pada aplikasi ChatKasir (menangkap entitas Produk, Qty, dan Price) merupakan implementasi dari tugas *Named Entity Recognition* (NER) tingkat lanjut.
- Pemetaan kalimat paling efektif dimodelkan menggunakan skema tokenisasi **BIO (Beginning, Inside, Outside)** untuk memisahkan posisi kata secara struktural.

### Keputusan Desain Akhir (V2 Update)
- Guna menghindari interferensi tugas (*Task Interference*) akibat pemisahan cabang regresi yang rawan *error*, seluruh ekstraksi entitas disatukan ke dalam satu jalur **Unified NER Head**. 
- Penggunaan layer CRF (V1) tidak dipakai demi menjaga efisiensi komputasi *runtime* API. Sebagai gantinya, aturan transisi sekuensial dipercayakan pada kombinasi layer BiLSTM dan proyeksi probabilitas **Softmax 7 Kelas** secara terpusat.

---

## 2. Arsitektur Hybrid: Transformer & BiLSTM - Vaswani et al. (2017)

**Judul:** Attention Is All You Need  
**Link:** https://arxiv.org/abs/1706.03762

### Insight Utama
- Arsitektur berbasis *Self-Attention* (Transformer) memiliki keunggulan mutlak dalam menangkap korelasi semantik jarak jauh (*long-range dependencies*) antar kata di dalam kalimat secara paralel tanpa terikat batasan arah.

### Keputusan Desain Akhir (V2 Update)
- Percakapan chat UMKM bersifat majemuk (*multi-item*) dan panjang, sehingga diintegrasikan layer **Transformer Encoder** sebagai *backbone* utama untuk menangkap konteks global pesanan.
- Untuk memperkuat akurasi transisi token BIO lokal (misalnya, memastikan tag `I-PROD` tidak pernah muncul sendirian tanpa didahului `B-PROD`), output Transformer dioper ke layer **Bidirectional LSTM (64 Units)**. Kombinasi *hybrid* ini melahirkan model yang ringan namun sangat sensitif terhadap urutan kata.
- Model dilatih sepenuhnya dari nol (*from scratch*) tanpa *pre-trained weights* pihak ketiga agar sangat spesifik pada domain korpus UMKM lokal.

---

## 3. Subword Tokenization & Robustness - Wilie et al. (2020)

**Judul:** IndoNLU: Benchmark and Resources for Evaluating Indonesian Natural Language Understanding  
**Link:** https://arxiv.org/abs/2009.05387

### Insight Utama
- Bahasa informal Indonesia pada percakapan digital memiliki variasi morfologi yang sangat acak, kaya akan *code-mixing*, kata *slang*, serta typo.
- Pemrosesan berbasis kamus kata (*word-level*) konvensional dipastikan gagal total akibat tingginya masalah *Out-of-Vocabulary* (OOV).

### Keputusan Desain Akhir (V2 Update)
- Mengadopsi metode **Subword Tokenization (WordPiece)** dengan kapasitas perluasan kosakata hingga **10.000 token**.
- Melalui WordPiece, kata-kata *slang* atau *typo* ekstrem dari WhatsApp pembeli akan dipecah secara objektif menjadi sub-token (misal: `"hrgny##a"` atau `"nasgorrrr"` -> `["nas", "gor", "##rrr"]`). Hal ini menjamin ketangguhan arsitektur model tanpa perlu membebani kapasitas memori server.

---

## 4. Penanganan Class Imbalance pada Sequence Labeling - Lin et al. (2017)

**Judul:** Focal Loss for Dense Object Detection (Focal Loss Concept for Imbalanced Classes)  
**Link:** https://arxiv.org/abs/1708.02002

### Insight Utama
- Pada domain pengenalan entitas sekuensial (NER), data akan selalu didominasi secara ekstrem oleh token latar belakang biasa (`O` / *Outside*). Kelas entitas penting (`PROD`, `QTY`, `PRICE`) umumnya hanya menempati porsi di bawah 30% dari keseluruhan teks kalimat.
- Jika dilatih menggunakan fungsi loss standar, model akan mengalami jalan buntu komputasi karena cenderung menebak kelas `O` demi mengamankan nilai akurasi semu.

### Keputusan Desain Akhir (V2 Update)
- Proses kompilasi meninggalkan fungsi standar bawaan Keras `.fit()` dan bermigrasi penuh menggunakan *Custom Training Loop* berbasis **`tf.GradientTape`**.
- Mengimplementasikan fungsi loss kustom **`MaskedNERLoss`** yang menggabungkan metode *Padding Masking* (mengabaikan token kosong `[PAD]`) dengan **Dynamic Class Weighting**. Bobot hukuman diberikan secara asimetris: kelas `O` dinilai normal (1.0), sedangkan kesalahan tebak pada entitas komersial dijatuhi hukuman penalti gradient jauh lebih berat (`PROD` = 2.0 dan `QTY`/`PRICE` = 1.5) untuk memaksa model tetap objektif mengenali entitas penting.