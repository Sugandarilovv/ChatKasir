# API Contract — ChatKasir

**Version**: 1.2.0
**Tanggal**: 4 Mei 2026
**Disusun oleh**: FS-2 (Reihan) & AI-2 (Denny)
**Changelog**: v1.2.0 — Penambahan endpoint GET /report/monthly dan sinkronisasi field /predict (kembali ke product_name sesuai kesepakatan tim AI).

---

## A. Endpoint Milik Backend FS-2

Base URL: `http://localhost:3000`

Semua endpoint kecuali Auth menggunakan header: `Authorization: Bearer <token>`

---

### 1. Register

**`POST /auth/register`**

Dipakai ketika penjual buat akun baru.

Request:

```json
{
  "email": "penjual@gmail.com",
  "password": "password123",
  "full_name": "penjual baik"
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

### 3. Create Transaction

**`POST /transactions`**

Menerima teks mentah dari frontend, meneruskannya ke AI, lalu menyimpan hasilnya ke
database.

Request Body:

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
  "message": "Laporan bulanan berhasil diambil",
  "period": "5-2026",
  "summary": {
    "total_revenue": 1500000,
    "total_items_sold": 45,
    "total_transactions": 20
  },
  "data": [
    {
      "product_name": "nasi goreng",
      "quantity": 2,
      "total": 30000,
      "transaction_date": "2026-05-04"
    }
  ]
}
```

---

## B. Endpoint Milik AI-2 (Denny)

> Base URL: `https://<ai-api-host>/`
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

**Response `200 OK`**

```json
{
  "status": "success",
  "results": [
    {
      "product": "nasi goreng",
      "quantity": 2,
      "price_satuan": 10000,
      "total": 20000,
      "confidence": "HIGH"
    }
  ]
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

## D. Catatan

**Disepakati bersama:** Jika AI gagal mengekstrak (predictions kosong), backend akan menyimpan `chat_extractions` dengan status `"failed"` dan tidak membuat record di tabel `transactions`. Nilai valid untuk kolom `status` di `chat_extractions` adalah: `"pending"`, `"processed"`, `"failed"`.

**Supabase Auth:** Register dan login menggunakan Supabase Auth bawaan — token JWT dihandle otomatis oleh Supabase. Frontend (FS-1) menyimpan token dan mengirimkannya di header setiap request ke backend.

**Field product_name:** Berdasarkan diskusi tanggal 4 Mei, tim AI (Denny/Rifan) setuju untuk mengubah output model/API dari product menjadi product_name agar konsisten dengan database backend.

**Field status:** Denny (AI-2) akan menambahkan root field status di response /predict.
