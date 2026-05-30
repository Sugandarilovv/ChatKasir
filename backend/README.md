# FS-2 Backend — Muhammad Reihan Ersa Putra

Repositori ini berisi seluruh kode sumber untuk **Back End (FS-2)** aplikasi ChatKasir. Proyek ini dibangun menggunakan framework Express.js dan terintegrasi dengan database PostgreSQL melalui Supabase, serta mendukung pemrosesan teks berbasis AI untuk pencatatan transaksi otomatis secara real-time.

Aplikasi ini telah berhasil di-deploy dan berjalan secara serverless di **Vercel**.

---

## Arsitektur Sistem & Integrasi

Sistem ChatKasir mengadopsi pendekatan terdistribusi yang memisahkan beban komputasi:

1. **Frontend (React/Vite):** Berjalan di sisi klien, mengonsumsi REST API dari repositori ini.
2. **Main Backend (Node.js/Express):** Repositori ini. Mengatur _routing_, validasi, CORS, autentikasi sesi, dan kalkulasi bisnis (laporan/dashboard).
3. **AI Service (Python/FastAPI):** _Microservice_ terpisah yang menerima teks chat mentah dari Backend ini dan mengembalikannya menjadi struktur JSON data produk yang dapat dibaca mesin.
4. **Database & Auth (Supabase):** PostgreSQL di _cloud_ untuk penyimpanan relasional dan manajemen sesi JWT.
5. **Custom SMTP (Brevo):** Terintegrasi di dalam Supabase Auth untuk menjamin pengiriman email OTP dan _Reset Password_ (_Magic Link_) dengan _deliverability_ tinggi dan bebas dari limitasi _rate-limit_.

---

## Tech Stack

| Teknologi             | Versi      | Kegunaan                                                      |
| :-------------------- | :--------- | :------------------------------------------------------------ |
| **Node.js**           | `>=18`     | Runtime environment JavaScript                                |
| **Express.js**        | `^5.2.1`   | Framework utama untuk pembuatan RESTful API                   |
| **Supabase JS**       | `^2.104.0` | Client untuk manajemen Database (PostgreSQL) & Authentication |
| **dotenv**            | `^17.4.2`  | Manajemen environment variables secara aman                   |
| **cors**              | `^2.8.6`   | Middleware pengatur izin akses cross-origin dari frontend     |
| **express-validator** | `^7.0.0`   | Validasi data input pada request body                         |

---

## Struktur Folder

```text
backend/
├── src/
│   ├── config/
│   │   └── supabase.js              ← Inisialisasi DB & Auth Supabase Client
│   ├── controllers/
│   │   ├── authController.js        ← Logika Auth (Register, Login, OTP, Password)
│   │   ├── transactionController.js ← Logika Transaksi & Integrasi AI (Hugging Face)
│   │   ├── reportController.js      ← Logika Kalkulasi Laporan Keuangan Bulanan
│   │   └── userController.js        ← Logika Manajemen Profil User
│   ├── middleware/
│   │   └── authMiddleware.js        ← Proteksi Route (JWT Verifier via Supabase)
│   └── routes/
│       ├── authRoutes.js            ← Routing endpoint kelompok Auth
│       ├── transactionRoutes.js     ← Routing endpoint kelompok Transaksi
│       ├── reportRoutes.js          ← Routing endpoint kelompok Laporan
│       └── userRoutes.js            ← Routing endpoint kelompok User
├── .env.example                     ← Contoh format environment variable
├── index.js                         ← Entry point utama aplikasi & Konfigurasi CORS
├── vercel.json                      ← Konfigurasi Deployment Serverless Vercel
└── package.json                     ← Daftar dependencies dan script running
```

---

## Memulai di Lokal (Local Development)

Ikuti langkah-langkah di bawah ini untuk menjalankan server backend ini di komputer lokal kamu:

1. **Clone Repositori:**

   ```bash
   git clone <url-repository-github-kamu>
   cd backend
   ```

2. **Install Dependencies:**

   ```bash
   npm install
   ```

3. **Setup Environment Variables:**
   Buat sebuah file baru bernama `.env` tepat di root folder backend, lalu isi parameternya dengan mengikuti struktur template dari `.env.example`:

   ```env
   PORT=3000
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_SECRET_KEY=your_supabase_service_role_key
   SUPABASE_PUBLISHABLE_KEY=your_supabase_anon_key
   AI_API_URL=https://achmadrifan-chatkasir.hf.space
   AI_API_KEY=your_huggingface_ai_api_key
   FRONTEND_URL=your_production_frontend_url
   ```

4. **Jalankan Server Lokal:**
   ```bash
   npm start
   ```
   Server backend akan otomatis berjalan aktif pada tautan `http://localhost:3000`.

---

## Skema Database

Backend ini memanipulasi data pada 4 tabel utama di klaster Supabase PostgreSQL:

| Tabel               | Fungsi Utama                                                 |
| ------------------- | ------------------------------------------------------------ |
| `users`             | Data profil penjual, tersinkronisasi dengan Supabase Auth    |
| `chat_extractions`  | Log histori teks chat mentah & status pemrosesan AI          |
| `transactions`      | Data master/induk setiap nota transaksi (menyimpan total)    |
| `transaction_items` | Data detail/rincian produk per transaksi (harga & kuantitas) |

_(Catatan: Skema lengkap ERD tersedia di `docs/supabase-schema-updated.png`)_

---

## Endpoint Utama API (Ringkasan)

- **Auth:** `POST /auth/register`, `POST /auth/login`, `POST /auth/forgot-password`, `PUT /auth/update-password`
- **Transaksi (AI):** - `POST /transactions/analyze` (Mengirim chat ke AI dan me-return JSON _preview_)
  - `POST /transactions` (Menyimpan data hasil konfirmasi ke tabel permanen)
- **Dashboard & Laporan:**
  - `GET /transactions` (Riwayat transaksi dengan _pagination_)
  - `GET /report/monthly` (Atau `/transactions/report` untuk kalkulasi pendapatan, item terjual, dan grafik chart)

---

## Skema Database

Backend ini terhubung ke Supabase PostgreSQL dengan 4 tabel utama:

| Tabel              | Fungsi                                           |
| ------------------ | ------------------------------------------------ |
| `users`            | Data profil penjual (terintegrasi Supabase Auth) |
| `products`         | Katalog produk milik penjual                     |
| `chat_extractions` | Teks chat mentah & status pemrosesan AI          |
| `transactions`     | Data transaksi hasil ekstraksi AI                |

Skema lengkap tersedia di `docs/supabase-schema-updated.png`.

---

## Informasi Deployment & Kebijakan CORS

- **Hosting Server Utama:** Vercel (Serverless Functions)
- **Database & Auth Provider:** Supabase Cloud (Region Asia Tenggara)
- **CORS Policy:** Akses lintas asal (CORS) telah dikonfigurasi secara dinamis untuk meloloskan _request_ secara eksklusif dari:
  - `http://localhost:3000` & `http://localhost:5173` (Local Development)
  - URL yang didaftarkan pada variabel _environment_ `FRONTEND_URL`
  - Semua domain _preview/production_ yang diakhiri dengan ekstensi `.vercel.app`.
