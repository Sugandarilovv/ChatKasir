# API Contract – AI-2 API ↔ FS-2 (Reihan)

> **Version**: 1.1.0
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

Cek status API dan model. Tidak butuh autentikasi.

**Response `200 OK`**
```json
{
  "status": "ok",
  "model_loaded": true,
  "version": "1.1.0"
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
| `raw_text` | `string` | ✅ | Raw chat WhatsApp. Min. 5 karakter (setelah strip). |

**Response `200 OK` — sukses**
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

**Response `200 OK` — harga tidak disebutkan di chat**
```json
{
  "results": [
    {
      "product":      "es teh",
      "quantity":     2,
      "price_satuan": null,
      "total":        null,
      "confidence":   "MEDIUM"
    }
  ],
  "clean_text": "..."
}
```

**Response `200 OK` — produk tidak dikenal (NER fallback)**
```json
{
  "results": [
    {
      "product":      "unknown",
      "quantity":     1,
      "price_satuan": null,
      "total":        null,
      "confidence":   "MEDIUM"
    }
  ],
  "clean_text": "..."
}
```

**OrderItem fields:**

| Field | Tipe | Nullable | Keterangan |
|---|---|---|---|
| `product` | `string` | ❌ | Nama produk lowercase. `"unknown"` jika NER gagal. |
| `quantity` | `integer` | ❌ | Jumlah pesanan (≥ 1) |
| `price_satuan` | `integer \| null` | ✅ | Harga SATUAN rupiah penuh. `null` jika tidak disebutkan. |
| `total` | `integer \| null` | ✅ | `quantity × price_satuan`. `null` jika `price_satuan` null. |
| `confidence` | `"HIGH" \| "MEDIUM" \| "LOW"` | ❌ | Tingkat kepercayaan prediksi |

**Confidence levels:**

| Nilai | Kondisi | Aksi yang Direkomendasikan (Alfan) |
|---|---|---|
| `HIGH` | Total di chat cocok dengan prediksi model | Langsung simpan ke database |
| `MEDIUM` | Tidak ada total, atau harga/produk tidak dikenali | Tampilkan dengan opsi edit |
| `LOW` | Ada total di chat tapi tidak cocok prediksi | Tampilkan peringatan, minta konfirmasi |

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

| HTTP Status | `error_code` | Kondisi |
|---|---|---|
| 401 | 4010 | API key tidak ada atau salah |
| 422 | 1001 | `raw_text` kurang dari 5 karakter, atau field tidak ada |
| 503 | 1002 | Model belum di-load (startup belum selesai) |
| 500 | 1003 | Inference gagal |
| 500 | 1000 | Error server tak terduga |

---

## Changelog

### v1.1.0
- `price_satuan` dan `total` sekarang **nullable** (`integer | null`) untuk kasus harga tidak disebutkan
- `product` bernilai `"unknown"` jika NER model gagal mengidentifikasi nama produk
- Error 422 kini menggunakan format error standar `{ error, error_code, message }` (konsisten dengan error lain)
- Inferensi dijalankan secara **async** (`run_in_executor`) — API tidak lagi blocking saat model berjalan
- Ditambahkan `Dockerfile` untuk deploy ke Hugging Face Spaces

### v1.0.0
- Initial release

---

## Catatan untuk FS-2 (Reihan)

1. `price_satuan` dan `total` kini **nullable** — handle `null` di sisi backend sebelum insert ke database.
2. Untuk `price_satuan: null`, gunakan kolom `harga_satuan` dari tabel `products` sebagai fallback.
3. Untuk `product: "unknown"`, simpan dengan status `"needs_review"` dan tampilkan ke penjual untuk diisi manual.
4. Untuk `confidence: "LOW"`, simpan dengan status `"pending_confirmation"`.
