# API Contract — ChatKasir

**Version**: 1.1.0
**Tanggal**: 26 April 2026
**Disusun oleh**: FS-2 (Reihan) & AI-2 (Denny)
**Changelog**: v1.1.0 — Refactor skema database (issue #24 by Rifan): rename `price` → `price_satuan`, tambah field `total`, `confidence`, `is_manual` di transactions; update tabel users pakai Supabase Auth.

---

## Gambaran Alur Kerja

Ini urutan kerja antar bagian di ChatKasir:

```
PENJUAL
  ↓ copy-paste teks chat WhatsApp
FRONTEND — Alfan (FS-1)
  ↓ kirim teks ke backend
BACKEND — Reihan (FS-2)      ←→     DATABASE Supabase
  ↓ forward teks ke AI
AI API — Denny (AI-2)
  ↓ kembalikan hasil ekstraksi
BACKEND — Reihan (FS-2)
  ↓ simpan ke database, kirim response
FRONTEND — Alfan (FS-1)
  ↓ tampilkan ke penjual
PENJUAL 🎉
```

---

## A. Endpoint Milik Backend FS-2

> Base URL: `http://localhost:3000`
> Semua endpoint kecuali Auth menggunakan header: `Authorization: Bearer <token>`

---

### 1. Register

**`POST /auth/register`**

Dipakai ketika penjual buat akun baru.

Request:

```json
{
  "email": "penjual@gmail.com",
  "password": "password123"
}
```

Response sukses `201`:

```json
{
  "message": "Register berhasil",
  "user_id": "uuid-user"
}
```

Response gagal `400`:

```json
{
  "error": "Email sudah terdaftar"
}
```

---

### 2. Login

**`POST /auth/login`**

Dipakai ketika penjual masuk ke aplikasi. Setelah login, frontend akan menyimpan `token` dan mengirimkannya di setiap request berikutnya.

Request:

```json
{
  "email": "penjual@gmail.com",
  "password": "password123"
}
```

Response sukses `200`:

```json
{
  "token": "jwt-token-panjang-disini",
  "user_id": "uuid-user"
}
```

---

### 3. Kirim Teks Chat (Endpoint Utama)

**`POST /transactions`**

Ini endpoint paling penting. Penjual paste teks chat, frontend kirim ke sini, lalu backend akan otomatis minta AI untuk mengekstrak datanya, dan menyimpan hasilnya ke database.

Request:

```json
{
  "raw_text": "Budi beli 2 nasi goreng 15rb sama 3 es teh 5rb"
}
```

Response sukses `201`:

```json
{
  "message": "Transaksi berhasil disimpan",
  "extraction_id": "uuid-extraction",
  "items": [
    { "product_name": "nasi goreng", "quantity": 2, "price": 15000 },
    { "product_name": "es teh", "quantity": 3, "price": 5000 }
  ]
}
```

Response gagal ekstraksi `422`:

```json
{
  "error": "Teks tidak dapat diekstrak oleh AI"
}
```

---

### 4. Lihat Daftar Transaksi

**`GET /transactions`**

Dipakai frontend untuk menampilkan riwayat transaksi. Bisa difilter berdasarkan tanggal.

Query params (opsional): `?date=2026-04-23`

Response `200`:

```json
{
  "data": [
    {
      "id": "uuid-transaksi",
      "product_name": "nasi goreng",
      "quantity": 2,
      "price_satuan": 15000,
      "total": 30000,
      "confidence": "HIGH",
      "is_manual": false,
      "transaction_date": "2026-04-23"
    }
  ]
}
```

---

### 5. Laporan Bulanan

**`GET /report/monthly`**

Dipakai frontend/dashboard untuk menampilkan total pendapatan per hari dalam satu bulan.

Query params: `?month=4&year=2026`

Response `200`:

```json
{
  "month": "April 2026",
  "total_revenue": 250000,
  "daily": [
    {
      "date": "2026-04-23",
      "revenue": 45000,
      "total_transactions": 3
    }
  ]
}
```

---

## B. Endpoint Milik AI-2 (Denny)

> Base URL: `http://localhost:8000`
> Semua endpoint menggunakan header: `X-API-Key: <api-key>`
> API key disimpan di file `.env` backend FS-2, tidak boleh di-push ke GitHub.

---

### 1. Health Check

**`GET /health`**

Dipakai backend untuk memastikan AI API sedang berjalan sebelum mengirim teks.

Response `200`:

```json
{
  "status": "ok",
  "model_loaded": true,
  "version": "1.0.0"
}
```

---

### 2. Ekstraksi Teks (Endpoint Utama AI)

**`POST /predict`**

Backend FS-2 mengirim teks mentah ke sini, dan AI akan mengembalikan hasil ekstrasinya.

Request:

```json
{
  "text": "Budi beli 2 nasi goreng 15rb sama 3 es teh 5rb"
}
```

Response sukses `200`:

```json
{
  "status": "success",
  "predictions": [
    {
      "product_name": "nasi goreng",
      "quantity": 2,
      "price_satuan": 15000,
      "confidence": "HIGH"
    },
    {
      "product_name": "es teh",
      "quantity": 3,
      "price_satuan": 5000,
      "confidence": "MEDIUM"
    }
  ]
}
```

Response gagal `200`:

```json
{
  "status": "failed",
  "predictions": []
}
```

---

## C. Kode Error Standar

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

## D. Catatan Penting untuk Integrasi

**FS-2 (Reihan):** Sebelum memanggil `/predict`, harus manggil `/health` dulu untuk memastikan model sudah loaded.

**AI-2 (Denny):** Endpoint `/predict` perlu diubah agar menerima `{ "text": "..." }` bukan array of numbers. Output harus berupa array of objects dengan field `product_name`, `quantity`, `price_satuan`, dan `confidence` (`"HIGH"`, `"MEDIUM"`, `"LOW"`).

**Disepakati bersama:** Jika AI gagal mengekstrak (predictions kosong), backend akan menyimpan `chat_extractions` dengan status `"failed"` dan tidak membuat record di tabel `transactions`. Nilai valid untuk kolom `status` di `chat_extractions` adalah: `"pending"`, `"processed"`, `"failed"`.

**Supabase Auth:** Register dan login menggunakan Supabase Auth bawaan — token JWT dihandle otomatis oleh Supabase. Frontend (FS-1) menyimpan token dan mengirimkannya di header setiap request ke backend.
