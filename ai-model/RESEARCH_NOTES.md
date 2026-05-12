# Research Notes - AI-1 Model Architect

Catatan studi referensi ilmiah yang memengaruhi keputusan desain arsitektur model ChatKasir (Update: Advanced Architecture).

---

## 1. NER & CRF - Lample et al. (2016)

**Judul:** Neural Architectures for Named Entity Recognition  
**Link:** https://arxiv.org/abs/1603.01360

### Insight utama
- Tugas ekstraksi entitas ChatKasir (product) pada dasarnya adalah NER (Named Entity Recognition). Model melabeli token dalam kalimat menggunakan skema BIO (Beginning, Inside, Outside).
- Menambahkan layer **CRF (Conditional Random Field)** di atas neural network sangat efektif untuk memodelkan aturan urutan label (misalnya, memastikan tag `I-PROD` tidak pernah muncul sebelum `B-PROD`).

### Keputusan desain yang diambil
- Cabang khusus *Product* di arsitektur kita mengadopsi sistem NER yang diakhiri dengan layer CRF untuk memastikan ekstraksi nama menu makanan selalu logis dan berurutan.

---

## 2. Transformer & Attention - Vaswani et al. (2017)

**Judul:** Attention Is All You Need  
**Link:** https://arxiv.org/abs/1706.03762

### Insight utama
- Arsitektur berbasis *Self-Attention* (Transformer) jauh lebih unggul dalam menangkap hubungan kata jarak jauh di dalam kalimat dibandingkan *Recurrent Neural Networks* (seperti LSTM), serta memproses seluruh kalimat secara paralel.

### Keputusan desain yang diambil
- Menggantikan *Shared Bi-LSTM* dengan **Transformer Encoder** sebagai tulang punggung (backbone) utama model untuk memahami konteks chat UMKM yang sering kali panjang dan tidak terstruktur.
- Model dilatih dari nol (*from scratch*) tanpa menggunakan bobot *pre-trained*.

---

## 3. Subword Tokenization (BPE) & Penanganan Slang - Wilie et al. (2020)

**Judul:** IndoNLU: Benchmark and Resources for Evaluating Indonesian Natural Language Understanding  
**Link:** https://arxiv.org/abs/2009.05387

### Insight utama
- Teks Bahasa Indonesia informal memiliki variasi morfologi tinggi, *code-mixing*, dan slang yang tidak ada di kamus baku.
- Model berbasis *word-level* tradisional akan sangat rentan terhadap masalah *Out-of-Vocabulary* (OOV) saat menghadapi salah ketik (*typo*).

### Keputusan desain yang diambil
- Preprocessing normalisasi menggunakan kamus (dari DS-1) tetap wajib.
- Menerapkan **Subword Tokenization (BPE/WordPiece)** agar model bisa memecah dan memahami kata-kata slang tak terduga (misal: "nasgorrrr" -> `["nas", "gor", "##rrr"]`) tanpa perlu memperbesar memori ukuran *vocabulary*.
- *Pre-trained* IndoBERT tidak digunakan langsung untuk menjaga model tetap ringan dan sangat spesifik pada domain UMKM.