# API Contract — ChatKasir

**Version**: 2.0.0
**Tanggal**: 29 Mei 2026
**Disusun oleh**: FS-2 (Reihan) & AI-2 (Denny/Rifan)

## Changelog (Riwayat Perubahan)

- **v2.0.0 (Current)**:
  - Migrasi penuh ke **AI Model V2**. Perubahan penamaan field di dalam array dari `product` menjadi `product_name`.
  - Mengubah field akumulasi harga per barang dari `total` menjadi `subtotal`.
  - Penambahan field `total_akumulasi` (Grand Total kalkulasi otomatis dari server) dan `confidence` score (`HIGH`/`LOW`) per barang.
  - Sinkronisasi skema autentikasi Supabase Auth kustom (Brevo SMTP).

---

## Kebijakan Global & Header

1. **Base URL Backend**: `https://chat-kasir-backend.vercel.app` (atau `http://localhost:3000` di lokal).
2. **Autentikasi**: Semua endpoint kecuali grup `/auth` wajib menyertakan header:
   ```http
   Authorization: Bearer <your_supabase_jwt_token>
   Content-Type: application/json
   ```

---

## A. Grup Endpoint: Autentikasi (/auth)

### 1. Register Akun Baru

**`POST /auth/register`**

**Request Body:**

```json
{
  "email": "penjual@gmail.com",
  "password": "password123",
  "full_name": "penjual baik"
}
```

**Response sukses `201`:**

```json
{
  "message": "Registrasi berhasil! Silakan cek email untuk verifikasi lebih lanjut."
}
```

---

### 2. Login

**`POST /auth/login`**

Dipakai ketika penjual masuk ke aplikasi. Setelah login, frontend akan menyimpan `token` dan mengirimkannya di setiap request berikutnya.

**Request Body:**

```json
{
  "email": "penjual@gmail.com",
  "password": "password123"
}
```

**Response sukses `200`:**

```json
{
  "message": "Login berhasil",
  "token": "eyJhbGciOiJIUzI1NiIsIn...",
  "user": {
    "id": "uuid-dari-supabase",
    "email": "penjual@gmail.com",
    "full_name": "Budi Kasir"
  }
}
```

---

### 3. Verifikasi Magic Link(Aktivasi Akun)

**`POST /auth/verify-otp`**

**Request Body:**

```json
{
  "email": "penjual@gmail.com",
  "password": "password123"
}
```

**Response sukses `200 OK`:**

```json
{
  "message": "Verifikasi berhasil, akun Anda sudah aktif!"
}
```

---

### 4. Lupa Password (Minta Link Recovery via Email)

**`POST /auth/forgot-password`**

**Request Body:**

```json
{
  "email": "penjual@gmail.com"
}
```

**Response sukses `200 OK`:**

```json
JSON
{
  "message": "Link reset password sudah dikirim ke email kamu"
}
```

---

### 5. Update Password Baru (Menggunakan Sesi Token Email)

**`PUT /auth/update-password`**

**Request Body:**

```json
{
  "access_token": "token_dari_url_recovery",
  "refresh_token": "refresh_token_dari_url_recovery",
  "new_password": "passwordBaru123"
}
```

**Response sukses `200 OK`:**

```json
{
  "message": "Password berhasil diperbarui"
}
```

---

## B. Grup Endpoint: Transaksi & Pemrosesan AI (/transactions)

### 1. Analisis Chat Transaksi (Nembak AI)

Endpoint ini digunakan ketika pengguna mengirimkan teks pesanan di kolom chat. Backend akan meneruskan ke server AI dan mengembalikan hasil ekstraksi terstruktur untuk ditampilkan sebagai preview confirmation block di Frontend

**`POST /transactions/analyze`**

**Request Body:**

```json
{
  "text": "pesan paket ayam bakar madu 10 bungkus sama es kopi susu gula aren 5"
}
```

**Response sukses `200 OK `:**

```json
{
  "status": "success",
  "results": [
    {
      "product_name": "Ayam Bakar Madu",
      "quantity": 10,
      "price_satuan": 35000,
      "subtotal": 350000,
      "confidence": "HIGH"
    },
    {
      "product_name": "Es Kopi Susu Gula Aren",
      "quantity": 5,
      "price_satuan": 18000,
      "subtotal": 90000,
      "confidence": "HIGH"
    }
  ],
  "total_akumulasi": 440000,
  "clean_text": "pesan paket ayam bakar madu 10 bungkus sama es kopi susu gula aren 5"
}
```

---

### 2. Simpan Transaksi Permanen (Konfirmasi Selesai)

Dipanggil ketika pengguna menekan tombol "Simpan/Konfirmasi" di frontend setelah memeriksa data hasil analisis AI.

**`POST /transactions`**

**Request Body:**

```json
{
  "total_price": 440000,
  "items": [
    {
      "product_name": "Ayam Bakar Madu",
      "quantity": 10,
      "price_satuan": 35000,
      "subtotal": 350000
    },
    {
      "product_name": "Es Kopi Susu Gula Aren",
      "quantity": 5,
      "price_satuan": 18000,
      "subtotal": 90000
    }
  ]
}
```

**Response Sukses `201 Created`:**

```json
{
  "message": "Transaksi berhasil disimpan permanen",
  "transaction_id": "uuid-transaksi-baru"
}
```

---

## C. Grup Endpoint: Dashboard & Laporan (/report)

### 1. Ambil Laporan Bulanan & Data Grafik

Digunakan untuk menyuplai seluruh data angka ringkasan (widgets) dan grafik batang/garis di halaman Dashboard Utama.

**`GET /report/monthly`**

**Query params: `?month=5&year=2026`**

**Response `200 OK`:**

```json
{
  "message": "Data laporan dashboard berhasil di-generate",
  "summary": {
    "total_revenue": 12500000,
    "total_transactions": 45,
    "total_items_sold": 180,
    "average_order_value": 277777,
    "average_revenue_per_day": 403225
  },
  "chart_data": [
    { "date": "2026-05-01", "revenue": 450000 },
    { "date": "2026-05-02", "revenue": 620000 }
  ],
  "top_products": [
    {
      "name": "Ayam Bakar Madu",
      "total_sold": 92,
      "total_revenue_generated": 3220000
    }
  ],
  "transactions": [
    {
      "id": "uuid-tx-1",
      "total_price": 440000,
      "created_at": "2026-05-29T12:00:00Z"
    }
  ]
}
```

---

## D. Endpoint Milik AI-2 (Denny/Rifan)

> Base URL: `https://achmadrifan-chatkasir.hf.space`
> Semua endpoint menggunakan header: `X-API-Key: <api-key>`
> API key disimpan di file `.env` backend FS-2, tidak boleh di-push ke GitHub.

---

### 1. Health Check

**`GET /health`**

Dipakai backend untuk memastikan AI API sedang berjalan sebelum mengirim teks.

**Response `200 OK` (Sistem Siap):**

```json
{
  "status": "ok",
  "model_loaded": true,
  "version": "2.0.0"
}
```

**Response `503 Service Unavailable` (Sistem Degraded / Gagal Muat Model):**

```json
{
  "status": "degraded",
  "model_loaded": false,
  "version": "2.0.0"
}
```

---

### 2. Ekstraksi Teks (Endpoint Utama AI)

**`POST /predict`**

Backend FS-2 mengirim teks mentah ke sini, dan AI akan mengembalikan hasil ekstrasi JSON terstruktur.

#### Skenario 1: Input 1 Produk

**Request:**

```json
{
  "raw_text": "[28/05, 05:26] Rifan: order paket ayam bakar madu 10 pack\n[28/05, 06:01] Alfan: siap harganya 35k"
}
```

**Response `200 OK`:**

```json
{
  "status": "success",
  "results": [
    {
      "product_name": "Ayam Bakar Madu",
      "quantity": 10,
      "price_satuan": 35000,
      "subtotal": 350000,
      "confidence": "HIGH"
    }
  ],
  "total_akumulasi": 350000,
  "clean_text": "pesan paket ayam bakar madu 10 bungkus [SEP] siap harga 35000"
}
```

#### Skenario 2: Input 2 Produk atau Lebih

**Request:**

```json
{
  "raw_text": "[28/05, 05:26] Rifan: order paket ayam bakar madu 10 pack sama es kopi susu gula aren 5 cup\n[28/05, 06:01] Alfan: siap paket ayam bakar madu harganya 35k dan es kopi susu gula aren harganya 18k jadi total tagihan katering semuanya 440k"
}
```

**Response `200 OK`:**

```json
{
  "status": "success",
  "results": [
    {
      "product_name": "Ayam Bakar Madu",
      "quantity": 10,
      "price_satuan": 35000,
      "subtotal": 350000,
      "confidence": "HIGH"
    },
    {
      "product_name": "Es Kopi Susu Gula Aren",
      "quantity": 5,
      "price_satuan": 18000,
      "subtotal": 90000,
      "confidence": "HIGH"
    }
  ],
  "total_akumulasi": 440000,
  "clean_text": "pesan paket ayam bakar madu 10 bungkus sama es kopi susu gula aren 5 cup [SEP] siap paket ayam bakar madu harga 35000 es kopi susu gula aren harga 18000 jadi total tagihan katering semua 440000"
}
```

---

## E. Kode Error Standar

| HTTP Status | Arti                                       |
| ----------- | ------------------------------------------ |
| `200`       | Sukses                                     |
| `201`       | Data berhasil dibuat                       |
| `400`       | Request tidak valid (misal: field kurang)  |
| `401`       | Tidak terautentikasi (token/API key salah) |
| `422`       | Data tidak bisa diproses                   |
| `500`       | Server error tak terduga                   |
| `503`       | Model AI belum siap                        |

---

## F. Catatan Integrasi V2

**1. Mapping Kunci (Key Mapping):** Backend FS-2 saat memanggil API AI harus merubah payload dari `{ "text": "..." }` menjadi `{ "raw_text": "..." }`.

**2. Agregasi Otomatis:** Backend tidak perlu lagi me-looping perhitungan tagihan satu per satu. Cukup baca variabel `"total_akumulasi"` dari JSON AI untuk mendapatkan grand total nilai pesanan.

**3. Penanganan Harga Kosong:** Jika chat pembeli/penjual tidak menyertakan harga, AI akan me-return `price_satuan: null` dan `subtotal: null`. Backend FS-2 wajib mengecek nilai `null` ini dan memberikan fallback (misal: query harga master di DB backend) sebelum menyimpan ke tabel `transactions`.

**4. Penanganan Produk Tidak Dikenali:** Jika NER gagal mendeteksi produk, AI akan me-return `"product_name": "unknown"` dan otomatis mengeset `"confidence": "MEDIUM"`. Backend dapat menyimpan `chat_extractions` dengan status `"needs_review"` atau `"pending"`.

**5. Supabase Auth:** Register dan login menggunakan Supabase Auth bawaan — token JWT dihandle otomatis oleh Supabase. Frontend (FS-1) menyimpan token dan mengirimkannya di header setiap request ke backend.
