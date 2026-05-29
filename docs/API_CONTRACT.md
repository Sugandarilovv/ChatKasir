# API Contract — ChatKasir

**Version**: 2.0.0
**Tanggal**: 29 Mei 2026
**Disusun oleh**: FS-2 (Reihan) & AI-2 (Denny/Rifan)
**Changelog**: 
- v2.0.0 - Migrasi struktur JSON AI V2: Perubahan field `product` menjadi `product_name`, `total` menjadi `subtotal`, penambahan field `total_akumulasi` dan `clean_text`. 
- Penyesuaian skema request AI dari `text` menjadi `raw_text`.


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

Menerima teks mentah dari frontend, meneruskannya ke AI, lalu menyimpan hasilnya ke database.

Request Body:

```json
{
  "raw_text": "[28/05, 05:26] Rifan: order paket ayam bakar madu 10 pack\n[28/05, 06:01] Alfan: siap harganya 35k"
}

```

Response sukses `201`:

```json
{
  "message": "Transaksi berhasil disimpan",
  "extraction_id": "uuid-extraction",
  "total_akumulasi": 350000,
  "items": [
    { 
      "product_name": "Ayam Bakar Madu", 
      "quantity": 10, 
      "price_satuan": 35000,
      "subtotal": 350000
    }
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
      "product_name": "Ayam Bakar Madu",
      "quantity": 10,
      "price_satuan": 35000,
      "subtotal": 350000,
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
      "product_name": "Ayam Bakar Madu",
      "quantity": 10,
      "subtotal": 350000,
      "transaction_date": "2026-05-04"
    }
  ]
}

```

---

## B. Endpoint Milik AI-2 (Denny/Rifan)

> Base URL: `https://achmadrifan-chatkasir.hf.space`
> Semua endpoint menggunakan header: `X-API-Key: <api-key>`
> API key disimpan di file `.env` backend FS-2, tidak boleh di-push ke GitHub.

---

### 1. Health Check

**`GET /health`**

Dipakai backend untuk memastikan AI API sedang berjalan sebelum mengirim teks.

Response `200 OK` (Sistem Siap):

```json
{
  "status": "ok",
  "model_loaded": true,
  "version": "2.0.0"
}

```

Response `503 Service Unavailable` (Sistem Degraded / Gagal Muat Model):

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

## C. Kode Error Standar

| HTTP Status | Arti |
| --- | --- |
| `200` | Sukses |
| `201` | Data berhasil dibuat |
| `400` | Request tidak valid (misal: field kurang) |
| `401` | Tidak terautentikasi (token/API key salah) |
| `422` | Data tidak bisa diproses |
| `500` | Server error tak terduga |
| `503` | Model AI belum siap |

---

## D. Catatan Integrasi V2

**1. Mapping Kunci (Key Mapping):** Backend FS-2 saat memanggil API AI harus merubah payload dari `{ "text": "..." }` menjadi `{ "raw_text": "..." }`.

**2. Agregasi Otomatis:** Backend tidak perlu lagi me-looping perhitungan tagihan satu per satu. Cukup baca variabel `"total_akumulasi"` dari JSON AI untuk mendapatkan grand total nilai pesanan.

**3. Penanganan Harga Kosong:** Jika chat pembeli/penjual tidak menyertakan harga, AI akan me-return `price_satuan: null` dan `subtotal: null`. Backend FS-2 wajib mengecek nilai `null` ini dan memberikan fallback (misal: query harga master di DB backend) sebelum menyimpan ke tabel `transactions`.

**4. Penanganan Produk Tidak Dikenali:** Jika NER gagal mendeteksi produk, AI akan me-return `"product_name": "unknown"` dan otomatis mengeset `"confidence": "MEDIUM"`. Backend dapat menyimpan `chat_extractions` dengan status `"needs_review"` atau `"pending"`.

**5. Supabase Auth:** Register dan login menggunakan Supabase Auth bawaan — token JWT dihandle otomatis oleh Supabase. Frontend (FS-1) menyimpan token dan mengirimkannya di header setiap request ke backend.