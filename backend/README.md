# FS-2 Backend — Muhammad Reihan Ersa Putra

Repositori ini berisi seluruh kode sumber untuk **Back End (FS-2)** aplikasi ChatKasir. Proyek ini dibangun menggunakan framework Express.js dan terintegrasi dengan database PostgreSQL melalui Supabase, serta mendukung pemrosesan teks berbasis AI untuk pencatatan transaksi otomatis secara real-time.

Aplikasi ini telah berhasil di-deploy dan berjalan secara serverless di **Vercel**.

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

## Fitur & Dokumentasi Endpoint (RESTful API)

Semua endpoint di bawah ini proteksinya telah diatur menggunakan **Auth Middleware**. Kecuali endpoint registrasi dan login, request wajib menyertakan header berikut:
`Authorization: Bearer <your_supabase_jwt_token>`

### 1. Autentikasi (`/auth`)

- `POST /auth/register` : Mendaftarkan akun kasir baru (wajib mengisi `email`, `password`, dan `full_name`). Sistem otomatis mengirimkan **Email Verification Link** ke email pendaftar.
- `POST /auth/login` : Masuk ke aplikasi menggunakan email terverifikasi. Mengembalikan JWT Token valid serta data profil user.
- `POST /auth/forgot-password` : Mengirimkan **Magic Link Reset Password** ke email milik user yang terdaftar untuk dialihkan ke halaman pembaruan sandi di frontend.
- `PUT /auth/update-password` : Memperbarui password lama milik user menggunakan token verifikasi sesi baru.

### 2. Manajemen Pengguna (`/users`)

- `PUT /users/profile` : Memperbarui data nama lengkap (`full_name`) dan URL foto profil (`avatar_url`) milik user aktif saat ini di dalam database Supabase.

### 3. Transaksi & Integrasi AI (`/transactions`)

- `POST /transactions` : Menerima teks kasir mentah (_raw text_), meneruskannya ke model AI NLP (Hugging Face) milik tim AI untuk diekstrak menjadi item produk, kuantitas, harga, total, lalu menyimpannya otomatis ke database.
- `GET /transactions` : Mengambil data seluruh riwayat transaksi kasir. Endpoint ini mendukung fitur query parameter untuk **Paginasi** (`page`, `limit`) dan **Filter Rentang Tanggal** (`startDate`, `endDate`).
  - _Contoh Request:_ `GET /transactions?page=1&limit=10&startDate=2026-05-01&endDate=2026-05-31`

### 4. Laporan Keuangan (`/report`)

- `GET /report/monthly` : Menghasilkan kalkulasi total pendapatan bulanan, kuantitas item terjual, serta daftar rincian data transaksi pada periode tertentu berdasarkan filter query params `month` (bulan) dan `year` (tahun). Digunakan untuk menyuplai data grafik di frontend.
  - _Contoh Request:_ `GET /report/monthly?month=5&year=2026`

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

- **Hosting Server:** Vercel (Serverless Functions)
- **Database Target:** Supabase PostgreSQL Database
- **CORS Policy:** Akses lintas asal (CORS) telah dikonfigurasi secara dinamis untuk meloloskan request dari `http://localhost:3000`, `http://localhost:5173`, domain utama yang didaftarkan pada variabel `FRONTEND_URL`, serta seluruh tautan otomatis _preview deployment_ berakhiran domain `*.vercel.app` milik tim frontend.
