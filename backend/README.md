# FS-2 Backend — Muhammad Reihan Ersa Putra

Bagian ini berisi seluruh pekerjaan **FS-2 (Full Stack - Back End)**: REST API berbasis Express.js yang menjadi jembatan antara frontend, AI model, dan database Supabase PostgreSQL.

---

## Tech Stack

| Tool        | Versi      | Kegunaan                             |
| ----------- | ---------- | ------------------------------------ |
| Node.js     | `>=18`     | Runtime JavaScript                   |
| Express.js  | `^5.2.1`   | Framework REST API                   |
| Supabase JS | `^2.104.0` | Client untuk database & auth         |
| dotenv      | `^17.4.2`  | Manajemen environment variables      |
| cors        | `^2.8.6`   | Mengizinkan request dari frontend    |
| nodemon     | `^3.1.14`  | Auto-restart server saat development |

---

## Struktur Folder

```
backend/
├── src/
│   ├── config/
│   │   └── supabase.js              ← Koneksi ke Supabase
│   ├── controllers/
│   │   ├── authController.js        ← Logika register & login
│   │   └── transactionController.js ← Logika transaksi & ekstraksi AI
│   ├── middleware/
│   │   └── authMiddleware.js        ← Cek token JWT sebelum akses endpoint
│   └── routes/
│       ├── authRoutes.js            ← Daftar endpoint /auth
│       └── transactionRoutes.js     ← Daftar endpoint /transactions
├── .env                             ← Environment variables (tidak di-push ke GitHub)
├── .env.example                     ← Template .env untuk anggota lain
├── index.js                         ← Entry point server
├── package.json
└── README-fs2.md                    ← Dokumentasi ini
```

---

## Cara Setup Environment

### 1. Pastikan Node.js sudah terinstall
```bash
node -v   # harus >= v18
npm -v
```

### 2. Clone repo dan masuk ke folder backend
```bash
git clone https://github.com/reihanersaa/ChatKasir.git
cd ChatKasir/backend
```

### 3. Install dependencies
```bash
npm install
```

### 4. Buat file `.env`
Copy dari template:
```bash
cp .env.example .env
```

Minta nilai aslinya ke Reihan, lalu isi:
```
PORT=3000
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_SECRET_KEY=sb_secret_...
AI_API_URL=http://localhost:8000
AI_API_KEY=
```

### 5. Jalankan server
```bash
npm run dev
```

Kalau berhasil akan muncul:
```
Server running on port 3000
```

---

## Daftar Endpoint

> Base URL: `http://localhost:3000`
> Semua endpoint selain Auth membutuhkan header: `Authorization: Bearer <token>`

### Auth

| Method | Endpoint         | Deskripsi              | Auth |
| ------ | ---------------- | ---------------------- | ---- |
| POST   | `/auth/register` | Daftar akun baru       | ✗    |
| POST   | `/auth/login`    | Login & dapatkan token | ✗    |

### Transaksi

| Method | Endpoint        | Deskripsi                                     | Auth |
| ------ | --------------- | --------------------------------------------- | ---- |
| POST   | `/transactions` | Kirim teks chat, ekstrak via AI, simpan ke DB | ✓    |
| GET    | `/transactions` | Ambil daftar transaksi (filter + paginasi)    | ✓    |

Query params GET `/transactions` (semua opsional):
- `?startDate=2026-04-01` — filter dari tanggal
- `?endDate=2026-04-30` — filter sampai tanggal
- `?page=1` — halaman (default: 1)
- `?limit=10` — jumlah data per halaman (default: 10)

### Laporan *(dalam pengerjaan)*

| Method | Endpoint          | Deskripsi                  | Auth |
| ------ | ----------------- | -------------------------- | ---- |
| GET    | `/report/monthly` | Laporan pendapatan bulanan | ✓    |

---

## Contoh Penggunaan Endpoint

### Register
```
POST http://localhost:3000/auth/register
Content-Type: application/json

{
  "email": "penjual@gmail.com",
  "password": "123456",
  "full_name": "Nama Penjual"
}
```
Response sukses `201`:
```json
{
  "message": "Registrasi berhasil!",
  "user": {
    "id": "uuid-...",
    "email": "penjual@gmail.com"
  }
}
```

---

### Login
```
POST http://localhost:3000/auth/login
Content-Type: application/json

{
  "email": "penjual@gmail.com",
  "password": "123456"
}
```
Response sukses `200`:
```json
{
  "message": "Login berhasil",
  "token": "eyJhbGci...",
  "user_id": "uuid-..."
}
```
> **Penting:** Simpan `token` dari response login. Token ini dipakai sebagai header `Authorization: Bearer <token>` untuk semua endpoint yang membutuhkan autentikasi.

---

### Kirim Teks Chat
```
POST http://localhost:3000/transactions
Authorization: Bearer <token>
Content-Type: application/json

{
  "raw_text": "Budi beli 2 nasi goreng 15rb sama 3 es teh 5rb"
}
```
Response sukses `201`:
```json
{
  "message": "Transaksi berhasil diekstrak dan disimpan",
  "data": [
    {
      "product_name": "nasi goreng",
      "quantity": 2,
      "price_satuan": 15000,
      "total": 30000,
      "confidence": "HIGH",
      "is_manual": false,
      "transaction_date": "2026-05-07"
    }
  ]
}
```

---

### Ambil Daftar Transaksi
```
GET http://localhost:3000/transactions?startDate=2026-05-01&page=1&limit=10
Authorization: Bearer <token>
```
Response sukses `200`:
```json
{
  "message": "Data transaksi berhasil diambil",
  "pagination": {
    "total_items": 25,
    "current_page": 1,
    "total_pages": 3,
    "limit": 10
  },
  "data": [...]
}
```

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

## Status Integrasi AI

> **Per 7 Mei 2026** — Integrasi ke AI-2 API (Denny) masih menggunakan **mock response** sementara karena model AI masih dalam tahap development. Kode integrasi nyata sudah disiapkan dan akan diaktifkan setelah AI-2 siap. Lihat issue terkait di GitHub repo untuk detail penyesuaian yang dibutuhkan.

---

## Catatan untuk Anggota Tim

**FS-1 (Alfan):**
- Base URL backend: `http://localhost:3000` saat development, URL production menyusul setelah deploy
- Gunakan token dari response `POST /auth/login` sebagai `Bearer token` di setiap request yang butuh auth
- Format lengkap request & response ada di `docs/API_CONTRACT.md`
- Untuk GET `/transactions`, gunakan query params `startDate`, `endDate`, `page`, dan `limit`

**AI-2 (Denny):**
- Backend memanggil `POST /predict` milik kamu setiap ada request `POST /transactions`
- Format request & response yang diharapkan ada di `docs/API_CONTRACT.md` — pastikan schema Pydantic kamu sudah sesuai kontrak
- Lihat issue yang sudah dibuat di repo kamu untuk detail field yang perlu disesuaikan
- Saat ini backend masih pakai mock, akan langsung diswitch ke API kamu begitu siap

**DS-1 & DS-2 (Faradi & Salman):**
- Data transaksi tersimpan di tabel `transactions` Supabase
- Data teks mentah & status pemrosesan tersimpan di tabel `chat_extractions`
- Akses langsung ke Supabase bisa diminta ke Reihan
