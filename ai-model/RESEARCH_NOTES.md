# Research Notes - AI-1 Model Architect

Cattatan studi referensi ilmiah yang memengaruhi keputusan desain arsitektur model ChatKasir

---

## 1. NER - Lampe et al. (2016)

**Judul:** Neural Architectures for Named Entity Recognition  
**Link:** https://arxiv.org/abs/1603.

### Insight utama

- Tugas ekstraksi entitas ChatKasir (product, quantity, price) pada dasarnya adalah NER (Named Entity Recognition) - model melabeli token dalam kalimat
- Bidirectional LSTM terbukti lebih baik dari LSTM satu arah karena konteks kanan-kiri sama pentingnya
- Skema labeling BIO (Beginning, Inside, Outside) adalah standar untuk entitas multi-kata seperti "nasi goreng"

### Keputusan desain yang diambil

- Menggunakan Bidirectional LSTM sebagai shared encoder
- Embedding layer dilatih dari nol (bukan pretrained) karena kosakata domain untuk ChatKasir sangat spesifik

---

## 2. IndoBERT - Willie et al. (2020)

**Judul:** IndoNLU: Benchmark and Resources for Evaluating
Indonesian Natural Language Understanding  
**Link:** https://arxiv.org/abs/2009.05387

### Insight utama

- Teks Bahasa Indonesia informal memiliki variasi morfologi tinggi, code-mixing, dan slang yang tidak ada di kamus baku
- Dataset NLP Bahasa Indonesia jauh lebih sedikit dibanding Bahasa Inggris sehingga memotivasi penggunaan data sintetis

### Keputusan desain yang diambil

- Preprocessing wajib dilakukan sebelum teks masuk ke model seperti normalisasi slang (dataset kamus dari DS-1) dan standarisasi format harga (15rb -> 15000, 15k -> 15000)
- IndoBERT tidak digunakan langsung karena keterbatasan resource dan artsitektur custom lebih sesuai untuk skala proyek ChatKasir

---

## Referensi Lengkap

- Lample, G., Ballesteros, M., Subramanian, S., Kawakami, K.,
  & Dyer, C. (2016). Neural Architectures for Named Entity
  Recognition.
- Wilie, B., et al. (2020). IndoNLU: Benchmark and Resources
  for Evaluating Indonesian Natural Language Understanding.
