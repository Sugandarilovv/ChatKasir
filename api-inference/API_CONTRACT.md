# API Contract – AI-2 API ↔ FS-2 (Reihan)

> **Version**: 1.0.0
> **Base URL**: `https://<host>/`
> **Authentication**: `X-API-Key` header (wajib di semua endpoint kecuali `/health`)

---

## Authentication

Semua endpoint kecuali `GET /health` membutuhkan API key di header:

```
X-API-Key: <your-api-key>
```

Request tanpa key atau dengan key yang salah mendapat **HTTP 401**.

---

## Endpoints

### `GET /health`

Cek status API dan model. Tidak butuh autentikasi — dipakai monitoring & load balancer.

**Response `200 OK`**
```json
{
  "status": "ok",
  "model_loaded": true,
  "version": "1.0.0"
}
```

| Field | Tipe | Keterangan |
|---|---|---|
| `status` | `string` | `"ok"` jika model loaded, `"degraded"` jika tidak |
| `model_loaded` | `boolean` | Apakah model Keras sudah di-load ke memory |
| `version` | `string` | Versi API |

---

### `POST /predict`

Terima raw chat WhatsApp, kembalikan hasil prediksi transaksi.

**Request body** (`application/json`)
```json
{
  "raw_text": "[07.42, 22/4/2026] Pembeli: bang 2 nasi goreng ya\n[07.44, 22/4/2026] Penjual: oke kak 1 nasi goreng 10rb totalnya 20rb ya"
}
```

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `raw_text` | `string` | ✅ | Raw chat WhatsApp. Boleh mengandung timestamp — dibersihkan otomatis. Min. 5 karakter. |

**Response `200 OK`**
```json
{
  "results": [
    {
      "product":      "nasi goreng",
      "quantity":     2,
      "price_satuan": 10000,
      "total":        20000,
      "confidence":   "HIGH"
    }
  ],
  "clean_text": "bang 2 nasi goreng ya [SEP] oke kak 1 nasi goreng 10rb totalnya 20rb ya"
}
```

| Field | Tipe | Keterangan |
|---|---|---|
| `results` | `array[OrderItem]` | Satu item untuk 1 produk; lebih dari satu untuk multi-produk |
| `clean_text` | `string` | Teks setelah preprocessing (tanpa timestamp, sudah normalisasi slang) |

**OrderItem fields:**

| Field | Tipe | Keterangan |
|---|---|---|
| `product` | `string` | Nama produk lowercase, contoh: `"nasi goreng"` |
| `quantity` | `integer` | Jumlah pesanan (≥ 1) |
| `price_satuan` | `integer` | Harga SATUAN dalam rupiah penuh — **bukan ribuan, bukan total** |
| `total` | `integer` | `quantity × price_satuan` — dihitung deterministik oleh AI-2 |
| `confidence` | `"HIGH" \| "MEDIUM" \| "LOW"` | Tingkat kepercayaan prediksi (lihat tabel di bawah) |

**Confidence levels:**

| Nilai | Kondisi | Aksi yang Direkomendasikan (untuk Alfan) |
|---|---|---|
| `HIGH` | Total di chat cocok dengan prediksi model | Langsung simpan ke database |
| `MEDIUM` | Tidak ada total di chat untuk diverifikasi | Tampilkan dengan opsi edit |
| `LOW` | Ada total di chat tapi tidak cocok dengan prediksi | Tampilkan peringatan, minta konfirmasi penjual |

---

## Error Responses

Semua error mengikuti schema ini:

```json
{
  "error": true,
  "error_code": 1001,
  "message": "Deskripsi yang bisa dibaca manusia"
}
```

| HTTP Status | `error_code` | Keterangan |
|---|---|---|
| 401 | 4010 | API key tidak ada atau salah |
| 422 | 1001 | Input tidak valid / malformed |
| 503 | 1002 | Model belum di-load |
| 500 | 1003 | Inference gagal |
| 500 | 1000 | Error server tak terduga |

---

## Catatan untuk FS-2 (Reihan)

1. Simpan `price_satuan` dan `total` sebagai **integer rupiah penuh** — jangan dalam ribuan.
2. Untuk transaksi dengan `confidence = "LOW"`, sebaiknya simpan dengan status `"pending_confirmation"` dan tunggu konfirmasi penjual.
3. Tabel `products` sebaiknya memiliki kolom `harga_satuan` sebagai fallback ketika `price_satuan` dari model bernilai `0` (harga tidak disebutkan di chat).
