# 🧾 ChatKasir - Asisten Kasir Cerdas Berbasis AI

![ChatKasir Banner](frontend/public/logo.png) 

**ChatKasir** adalah sistem aplikasi pencatatan transaksi kasir cerdas yang dirancang khusus untuk UMKM Indonesia. Aplikasi ini memanfaatkan **Artificial Intelligence (AI) - Named Entity Recognition (NER)** untuk membaca, mengekstrak, dan menghitung pesanan secara otomatis langsung dari teks obrolan (seperti dari WhatsApp).

Selain itu, ChatKasir dilengkapi dengan asisten chatbot **TanyaAI** (berbasis Google Gemini) untuk mengedukasi pemilik UMKM seputar bisnis, serta **Dashboard Analitik** untuk memantau performa penjualan.

---

## ✨ Fitur Utama

1. **AI Order Extraction**: Salin teks chat pembeli, dan AI akan otomatis mengekstrak _Nama Produk, Kuantitas, dan Harga_, lalu menghitung totalnya.
2. **Smart Fallback & Confidence Score**: Sistem mendeteksi otomatis jika AI kurang yakin (Confidence: LOW/MEDIUM) atau jika ada harga yang tidak disebutkan di chat, untuk dikonfirmasi ulang oleh kasir.
3. **TanyaAI (Asisten Bisnis UMKM)**: Chatbot terintegrasi berbasis Gemini 1.5 Flash yang dibatasi khusus untuk menjawab seputar strategi bisnis, keuangan, dan UMKM.
4. **Dashboard Analitik (Data Science)**: Visualisasi tren penjualan, performa produk, dan segmentasi harga menggunakan Streamlit.
5. **Aman & Cepat**: Arsitektur dipisah antara Frontend, Backend (Proxy), dan API AI agar rahasia kunci API dan keandalan sistem tetap terjaga.

---

## 🏗️ Arsitektur Sistem & Struktur Repositori

Proyek ini dibangun menggunakan arsitektur *microservices* dengan pembagian direktori sebagai berikut:

- 📂 **`frontend/`** — Antarmuka Web (UI) menggunakan **React, Vite, & Tailwind CSS v4**.
- 📂 **`backend/`** — Server REST API menggunakan **Node.js & Express**. Terhubung dengan **Supabase (PostgreSQL)** untuk database & autentikasi, serta bertindak sebagai _proxy_ aman untuk Gemini API.
- 📂 **`api-inference/`** — Server AI menggunakan **Python & FastAPI**. Bertugas memuat model AI (Keras) dan mengekstrak entitas dari teks. (Didesain untuk di-deploy ke Hugging Face Spaces).
- 📂 **`ai-model/`** — Ruang kerja Data Scientist. Berisi Jupyter Notebooks untuk proses _Training_, _Evaluation_, dan arsitektur model Neural Network.
- 📂 **`dashboard/`** — Dashboard analitik interaktif menggunakan **Streamlit** untuk visualisasi dataset dan simulasi model.
- 📂 **`data/`** & 📂 **`docs/`** — Berisi pipeline pengolahan data mentah/sintetis dan dokumen referensi seperti API Contract, Skema Database, dan Postman Collection.

---

## 🛠️ Teknologi yang Digunakan

* **Frontend**: React, Vite, Tailwind CSS, Axios, React-Markdown.
* **Backend**: Node.js, Express, Supabase JS Client, Google Generative AI SDK (Gemini).
* **AI & Data Science**: Python, TensorFlow/Keras, FastAPI, Streamlit, Pandas, Scikit-Learn.
* **Database & Auth**: Supabase (PostgreSQL).
* **Deployment**: Vercel (Frontend & Backend), Hugging Face Spaces (API Inference).

---

## 🚀 Cara Menjalankan Proyek Secara Lokal

Karena proyek ini bersifat modular, Anda harus menjalankan _Frontend_, _Backend_, dan _API Inference_ secara terpisah.

### Persyaratan Awal (Prerequisites)
- [Node.js](https://nodejs.org/) (v18 atau terbaru)
- [Python](https://www.python.org/) (v3.9 atau terbaru)
- Akun [Supabase](https://supabase.com/) (Untuk Database & Auth)
- Akun [Google AI Studio](https://aistudio.google.com/) (Untuk Gemini API Key)

### 1. Setup Backend (Node.js)
```bash
cd backend
npm install

```

Buat file `.env` di folder `backend/` (lihat `backend/.env.example`) dan isi:

```env
PORT=3000
SUPABASE_URL=url_supabase_anda
SUPABASE_ANON_KEY=key_supabase_anda
GEMINI_API_KEY=key_gemini_anda
FRONTEND_URL=http://localhost:5173

```

Jalankan server:

```bash
npm run dev
# Backend berjalan di http://localhost:3000

```

### 2. Setup API Inference (Python/FastAPI)

```bash
cd api-inference
# Disarankan menggunakan virtual environment (venv)
python -m venv venv
source venv/bin/activate  # Untuk Windows: venv\Scripts\activate

pip install -r requirements.txt

```

Buat file `.env` di folder `api-inference/` (lihat `api-inference/.env.example`) dan atur `API_KEY` untuk pengamanan endpoint:

```env
API_KEY=rahasia123

```

Jalankan server AI:

```bash
uvicorn app.main:app --reload --port 8000
# API AI berjalan di http://localhost:8000

```

### 3. Setup Frontend (React/Vite)

```bash
cd frontend
npm install

```

Buat file `.env` di folder `frontend/` (lihat `frontend/.env.example`):

```env
VITE_API_URL=http://localhost:3000
VITE_AI_INFERENCE_URL=http://localhost:8000
VITE_AI_API_KEY=rahasia123

```

Jalankan frontend:

```bash
npm run dev
# Frontend berjalan di http://localhost:5173

```

---

## 📊 Cara Menjalankan Dashboard Analitik (Streamlit)

Dashboard digunakan untuk memvisualisasikan data wawasan bisnis dari dataset.

```bash
cd dashboard
pip install -r requirements.txt # (Jika ada) atau instal streamlit pandas plotly
streamlit run app.py
# Dashboard berjalan di http://localhost:8501

```

---

## 📚 Dokumentasi API

Tim kami telah menyediakan dokumen **API Contract** yang mengatur alur komunikasi JSON antara Frontend, Backend, dan API Inference.

* Lihat detailnya di: [`docs/API_CONTRACT.md`](https://www.google.com/search?q=./docs/API_CONTRACT.md) atau [`api-inference/API_CONTRACT.md`](https://www.google.com/search?q=./api-inference/API_CONTRACT.md).
* Untuk pengujian endpoint dengan mudah, import file **Postman Collection** yang ada di folder [`docs/`](https://www.google.com/search?q=./docs/).

---

## 🤝 Pedoman Kontribusi (Contributing)

Kami menyambut kontribusi dari siapa saja! Jika Anda ingin mengembangkan fitur baru atau memperbaiki bug:

1. Lakukan *Fork* pada repositori ini.
2. Buat *branch* fitur Anda (`git checkout -b feature/FiturKeren`).
3. Lakukan *Commit* perubahan Anda (`git commit -m 'Menambahkan fitur keren'`).
4. *Push* ke *branch* tersebut (`git push origin feature/FiturKeren`).
5. Buka sebuah *Pull Request* baru.

---

## 👥 Tim Pengembang

Proyek ini dibangun secara kolaboratif sebagai bagian dari program **Coding Camp 2026 by DBS Foundation & Dicoding Indonesia**:

* **Alfan Ramadhan** - Full Stack Web Developer
* **Muhammad Reihan Ersa Putra** - Full Stack Web Developer
* **Muhammad Faradi Eka Damara** - Data Science
* **Salman Pandu Pandiya** - Data Science
* **Achmad Rif’an** - AI Engineer
* **Denny Yoan Hendrawan** - AI Engineer

---

**© 2026 ChatKasir Team.** Dilisensikan di bawah MIT License.