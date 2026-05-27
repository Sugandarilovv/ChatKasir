# UI Reference — ChatKasir Frontend

**Dikerjakan oleh:** Alfan Ramadhan (FS-1 - Front-End)
**Tanggal dibuat:** 21 April 2026

---

## Keputusan Stack UI

| Kebutuhan | Pilihan | Alasan |
|---|---|---|
| Komponen UI | DaisyUI v5 | Plugin Tailwind, tidak butuh import JS terpisah, 63+ komponen siap pakai, mudah dikustomisasi dengan class |
| Grafik | Recharts | Library React-first, ResponsiveContainer otomatis, dokumentasi lengkap |
| Form & validasi | react-hook-form | Ringan, validasi client-side mudah, tidak memerlukan state manual |
| Notifikasi | react-hot-toast | Ringan, API sederhana, animasi bawaan |
| HTTP request | Axios | Interceptor JWT otomatis, error handling terpusat |
| Routing | react-router-dom v6 | Standard React, ProtectedRoute mudah diimplementasikan |

---

## Tema Warna

Menggunakan tema default DaisyUI `light` dengan warna utama:

| Peran | Class DaisyUI | Keterangan |
|---|---|---|
| Primary | `btn-primary`, `text-primary` | Aksi utama (tombol Proses, Simpan) |
| Base content | `text-base-content` | Teks utama |
| Base 100/200 | `bg-base-100`, `bg-base-200` | Background kartu dan halaman |
| Error | `text-error`, `input-error` | Pesan error validasi form |
| Success | toast sukses | Konfirmasi aksi berhasil |

---

## Komponen yang Dibangun

### Layout
- `MainLayout.jsx` — wrapper dengan Navbar + Sidebar untuk halaman authenticated
- `Navbar.jsx` — logo, nama user, dropdown logout
- `Sidebar.jsx` — navigasi: Catat Transaksi, Dashboard, Laporan Bulanan

### Komponen UI Reusable
- `SummaryCard.jsx` — kartu ringkasan angka (total transaksi, pemasukan, rata-rata)
- `LoadingSkeleton.jsx` — skeleton loading untuk tabel
- `EmptyState.jsx` — tampilan data kosong dengan CTA

### Grafik
- `RevenueBarChart.jsx` — bar chart pemasukan harian menggunakan Recharts

---

## Halaman (Pages)

| Halaman | Route | Keterangan |
|---|---|---|
| Register | `/register` | Form daftar akun baru, validasi client-side |
| Login | `/login` | Form masuk, simpan JWT ke localStorage |
| Input Chat | `/input` | Copy-paste teks WhatsApp → kirim ke AI-2 |
| Konfirmasi | `/konfirmasi` | Tampilkan & edit hasil ekstraksi AI, simpan ke DB |
| Dashboard | `/dashboard` | Tabel transaksi harian + ringkasan |
| Laporan | `/laporan` | Grafik bar chart + top selling produk per bulan |

---

## Koneksi ke Anggota Tim

| Anggota | Bagian yang terhubung |
|---|---|
| FS-2 Reihan (Backend) | `services/authService.js` → POST /auth/register & login |
| FS-2 Reihan (Backend) | `services/transactionService.js` → GET/POST /transactions, GET /report/monthly |
| AI-2 Denny (FastAPI) | `services/aiService.js` → POST /predict |
| DS-2 Salman | Data yang diinput lewat frontend ini yang dianalisis di dashboard Streamlit-nya |

---

## Referensi UI

Inspirasi desain:
- Tampilan bersih seperti aplikasi kasir modern (Moka POS, Majoo)
- Warna netral dengan aksen primary yang jelas
- Tabel yang mudah dibaca di layar kecil (mobile-first)
