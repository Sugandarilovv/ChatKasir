# ChatKasir — Frontend

Repositori ini berisi kode sumber **Front-End** aplikasi **ChatKasir**, sebuah aplikasi pencatat keuangan berbasis AI untuk UMKM. Pengguna cukup *copy-paste* teks chat WhatsApp pesanan pelanggan, dan sistem AI akan mengekstrak nama produk, jumlah, serta harga secara otomatis.

---

## Daftar Isi

- [Tech Stack](#tech-stack)
- [Struktur Folder](#struktur-folder)
- [Konfigurasi Environment](#konfigurasi-environment)
- [Cara Menjalankan](#cara-menjalankan)
- [Halaman (Pages)](#halaman-pages)
- [Komponen (Components)](#komponen-components)
- [Services](#services)
- [Hooks](#hooks)
- [Context](#context)
- [Utils](#utils)
- [Deployment](#deployment)
- [Koneksi ke Anggota Tim](#koneksi-ke-anggota-tim)

---

## Tech Stack

| Kebutuhan | Library | Versi |
|---|---|---|
| Framework UI | React | ^18.3.1 |
| Build Tool | Vite | ^5.3.1 |
| Styling | Tailwind CSS | ^4.0.0 |
| Komponen UI | DaisyUI | ^5.0.0 |
| Routing | react-router-dom | ^6.23.1 |
| HTTP Client | Axios | ^1.7.2 |
| Auth & Storage | @supabase/supabase-js | ^2.106.0 |
| Form & Validasi | react-hook-form | ^7.51.5 |
| Grafik | Recharts | ^2.12.7 |
| Notifikasi Toast | react-hot-toast | ^2.4.1 |
| Date Picker | react-datepicker | ^9.1.0 |
| Format Tanggal | date-fns | ^4.1.0 |
| Render Markdown | react-markdown | ^10.1.0 |

---

## Struktur Folder

```
frontend/
├── .env                          # Variabel environment (tidak di-commit)
├── .env.example                  # Template .env untuk developer lain
├── index.html                    # Entry point HTML (SPA)
├── package.json                  # Dependensi dan script npm
├── vite.config.js                # Konfigurasi Vite
├── vercel.json                   # Konfigurasi deployment Vercel (SPA rewrite)
├── docs/
│   └── ui-reference.md           # Dokumentasi keputusan desain UI
├── public/
│   └── logo.png                  # Logo statis (favicon)
└── src/
    ├── main.jsx                  # Entry point React
    ├── App.jsx                   # Router utama + ProtectedRoute
    ├── index.css                 # Global CSS (Tailwind, DaisyUI, animasi)
    ├── assets/
    │   └── logo.png              # Logo untuk digunakan di dalam komponen
    ├── components/
    │   ├── charts/
    │   │   └── RevenueBarChart.jsx
    │   ├── layout/
    │   │   ├── MainLayout.jsx
    │   │   ├── Navbar.jsx
    │   │   └── Sidebar.jsx
    │   └── ui/
    │       ├── EmptyState.jsx
    │       ├── LoadingSkeleton.jsx
    │       ├── SummaryCard.jsx
    │       └── Toast.jsx
    ├── context/
    │   └── ThemeContext.jsx
    ├── hooks/
    │   ├── useAuth.js
    │   └── useTransactions.js
    ├── pages/
    │   ├── Login.jsx
    │   ├── Register.jsx
    │   ├── LupaPassword.jsx
    │   ├── InputChat.jsx
    │   ├── Konfirmasi.jsx
    │   ├── Dashboard.jsx
    │   ├── Laporan.jsx
    │   ├── TanyaAI.jsx
    │   ├── EditProfil.jsx
    │   └── Pengaturan.jsx
    ├── services/
    │   ├── axiosInstance.js
    │   ├── authService.js
    │   ├── aiService.js
    │   ├── transactionService.js
    │   └── supabaseClient.js
    └── utils/
        └── formatRupiah.js
```

---

## Konfigurasi Environment

Salin file `.env.example` menjadi `.env`, lalu sesuaikan nilainya:

```bash
cp .env.example .env
```

Isi file `.env`:

```env
# URL backend Express.js (FS-2 Reihan)
VITE_API_BASE_URL=http://localhost:3000

# URL API model AI FastAPI (AI-2 Denny)
VITE_AI_API_URL=http://localhost:8000
```

> **Catatan:** Jika `VITE_API_BASE_URL` tidak diset, aplikasi akan fallback ke `https://chat-kasir-backend.vercel.app`.

---

## Cara Menjalankan

```bash
# Install dependensi
npm install

# Jalankan development server
npm run dev

# Build untuk produksi
npm run build

# Preview hasil build
npm run preview
```

Aplikasi akan berjalan di `http://localhost:5173` secara default.

---

## Halaman (Pages)

### Alur Routing

```
/  →  /login (redirect)

Publik:
  /login
  /register
  /lupa-password

Protected (butuh token JWT):
  /input       →  InputChat
  /konfirmasi  →  Konfirmasi
  /dashboard   →  Dashboard
  /laporan     →  Laporan
  /tanya-ai    →  TanyaAI
  /profil      →  EditProfil
  /pengaturan  →  Pengaturan
```

Route yang tidak dikenal diarahkan ke `/login`.

---

### `Login.jsx` — `/login`

Halaman masuk akun. Menampilkan form email dan password dengan validasi client-side menggunakan `react-hook-form`. Memiliki panel kiri bergaya gelap (green-950) berisi statistik aplikasi (jumlah UMKM aktif, transaksi, akurasi AI).

Setelah login berhasil, token JWT dan data user disimpan ke `localStorage`, lalu pengguna diarahkan ke `/dashboard`.

---

### `Register.jsx` — `/register`

Halaman pendaftaran akun baru. Form berisi nama lengkap, email, password, dan konfirmasi password. Validasi client-side memastikan kedua password cocok. Desain dua panel serupa dengan Login, dilengkapi daftar fitur unggulan aplikasi.

---

### `LupaPassword.jsx` — `/lupa-password`

Alur reset password tiga langkah:
1. Masukkan email → kirim link reset via Supabase Auth
2. Verifikasi kode OTP dengan countdown timer 30 detik dan opsi kirim ulang
3. Buat password baru

Langkah 1 dan 3 terhubung ke Supabase secara langsung melalui `supabaseClient.js` (tidak melewati backend Express).

---

### `InputChat.jsx` — `/input` *(Protected)*

Halaman inti untuk memasukkan teks chat WhatsApp. Pengguna bisa:
- Mengetik teks secara manual
- Paste dari clipboard dengan satu klik
- Memilih dari dua contoh teks yang tersedia

Mendukung **simpan otomatis draft** ke `localStorage` (key `ck_draft_input`) yang dimuat kembali saat halaman dibuka ulang, selama fitur auto-save aktif di Pengaturan.

Setelah teks diproses oleh AI, hasilnya disimpan ke `sessionStorage` dan pengguna diarahkan ke `/konfirmasi`.

---

### `Konfirmasi.jsx` — `/konfirmasi` *(Protected)*

Menampilkan hasil ekstraksi AI berupa tabel item (nama produk, jumlah, harga satuan, subtotal). Pengguna dapat:
- Mengedit setiap field secara inline
- Menghapus item
- Menambah item baru secara manual

Data diambil dari `sessionStorage` yang diisi oleh `InputChat`. Setelah dikonfirmasi, data dikirim ke backend via `transactionService.saveTransactions()`.

---

### `Dashboard.jsx` — `/dashboard` *(Protected)*

Rekap transaksi harian dengan date picker untuk memilih tanggal. Menampilkan:
- Tiga `SummaryCard`: Total Pemasukan, Jumlah Transaksi, Rata-rata per Pesanan
- Tabel lengkap semua transaksi pada tanggal yang dipilih

Jumlah transaksi unik dihitung berdasarkan `extraction_id` yang berbeda (satu chat bisa menghasilkan beberapa item). Jika data kosong, ditampilkan `EmptyState` dengan tombol navigasi ke `/input`.

---

### `Laporan.jsx` — `/laporan` *(Protected)*

Laporan keuangan bulanan. Pengguna memilih bulan dan tahun untuk melihat:
- Ringkasan: total pemasukan, total transaksi, rata-rata harian
- Bar chart pemasukan harian (`RevenueBarChart`)
- Tabel 5 produk terlaris beserta total terjual dan total pendapatan

---

### `TanyaAI.jsx` — `/tanya-ai` *(Protected)*

Halaman chat interaktif untuk bertanya ke AI seputar bisnis. Fitur utama:
- Antarmuka chat bubble mirip WhatsApp (pesan user di kanan, AI di kiri)
- Riwayat percakapan dikirim ke API setiap pesan agar AI memiliki konteks
- Respons AI dirender sebagai Markdown menggunakan `react-markdown`
- Auto-scroll ke pesan terbaru
- Nama pengguna diambil dari `localStorage` untuk sapaan personal

Komunikasi dilakukan melalui `aiService.tanyaAI(history, message)` yang memanggil endpoint `POST /tanya-ai` di backend Express.

---

### `EditProfil.jsx` — `/profil` *(Protected)*

Form untuk mengubah nama dan foto profil. Foto dapat diunggah dari perangkat dan ditampilkan sebagai preview sebelum disimpan. Perubahan dikirim ke backend via `authService.updateProfile()` dan diperbarui di `localStorage`.

---

### `Pengaturan.jsx` — `/pengaturan` *(Protected)*

Halaman pengaturan akun dengan beberapa seksi:

| Seksi | Pengaturan | Keterangan |
|---|---|---|
| Tampilan | Mode Gelap | Toggle tema light/dark (sinkron dengan `ThemeContext`) |
| Notifikasi | Notifikasi Transaksi | Tampilkan toast saat transaksi tersimpan |
| Notifikasi | Notifikasi Laporan | Ingatkan saat laporan bulanan tersedia |
| Preferensi | Simpan Otomatis Draft | Simpan draft teks input ke `localStorage` |
| Akun | Ganti Password | — |
| Akun | Hapus Akun | Hapus permanen akun + semua data (dengan konfirmasi ketik "HAPUS") |

Semua preferensi toggle disimpan ke `localStorage` dengan key `ck_*`.

---

## Komponen (Components)

### Layout

#### `MainLayout.jsx`
Wrapper layout untuk semua halaman yang memerlukan autentikasi. Menyusun `Navbar` di atas dan `Sidebar` di samping kiri, lalu merender `children` di area konten utama. Mendukung toggle sidebar mobile melalui state `isMobileOpen`.

#### `Navbar.jsx`
Header aplikasi yang sticky di bagian atas. Berisi:
- Tombol hamburger (khusus mobile) untuk membuka/menutup sidebar
- Logo dan nama "ChatKasir"
- Tombol toggle tema (light/dark)
- Info nama dan email user
- Avatar dengan dropdown: Ubah Profil, Pengaturan Akun, dan tombol Keluar

#### `Sidebar.jsx`
Navigasi samping dengan tiga menu utama:

| Menu | Route |
|---|---|
| Catat Transaksi | `/input` |
| Dashboard | `/dashboard` |
| Laporan | `/laporan` |

Di desktop dapat di-*collapse* menjadi mode ikon-saja. Di mobile tampil sebagai overlay dengan backdrop blur. Menu aktif ditandai dengan highlight hijau dan indikator garis vertikal.

---

### UI Reusable

#### `SummaryCard.jsx`
Kartu statistik ringkasan. Props:

| Prop | Tipe | Keterangan |
|---|---|---|
| `title` | string | Label kartu |
| `value` | number | Nilai yang ditampilkan |
| `type` | `'number'` \| `'rupiah'` | Format tampilan nilai |
| `icon` | string | Emoji ikon |
| `loading` | boolean | Tampilkan skeleton jika `true` |

#### `Toast.jsx`
Sistem notifikasi toast custom berbasis React Context. Menyediakan fungsi global `showToast(msg, type)` yang dapat dipanggil dari mana saja tanpa hook. Mendukung empat tipe: `success`, `error`, `info`, `warning`. Toast otomatis hilang setelah 1,8 detik dengan animasi masuk dan keluar.

#### `EmptyState.jsx`
Tampilan saat tidak ada data. Menampilkan ikon 📭, pesan teks, dan opsional tombol aksi melalui props `action: { label, onClick }`.

#### `LoadingSkeleton.jsx`
Skeleton loading berupa baris animasi pulse untuk tabel transaksi. Menerima props `rows` (default 5) untuk mengatur jumlah baris skeleton.

---

### Charts

#### `RevenueBarChart.jsx`
Bar chart pemasukan harian menggunakan Recharts (`BarChart` + `ResponsiveContainer`). Menerima props `data` berupa array `{ tanggal, total }`. Mendukung mode gelap dan terang, dengan tooltip yang memformat nilai ke Rupiah.

---

## Services

### `axiosInstance.js`
Instance Axios terpusat dengan `baseURL` dari `VITE_API_BASE_URL`. Dilengkapi dua interceptor:

- **Request interceptor:** Otomatis menyisipkan token JWT dari `localStorage` ke header `Authorization: Bearer <token>`.
- **Response interceptor:** Jika respons `401 Unauthorized` dan bukan di halaman `/login`, otomatis hapus token dari `localStorage` dan redirect ke `/login`.

---

### `authService.js`

| Fungsi | Metode | Endpoint | Keterangan |
|---|---|---|---|
| `register(nama, email, password)` | POST | `/auth/register` | Daftar akun baru |
| `login(email, password)` | POST | `/auth/login` | Login, simpan token & user ke `localStorage` |
| `logout()` | — | — | Hapus token & user dari `localStorage` |
| `getCurrentUser()` | — | — | Baca data user dari `localStorage` |
| `forgotPassword(email)` | — | Supabase Auth | Kirim link reset password ke email |
| `updatePassword(accessToken, refreshToken, newPassword)` | — | Supabase Auth | Perbarui password via token recovery |
| `updateProfile(nama, foto)` | PUT | `/users/profile` | Update nama dan avatar URL |
| `deleteAccount()` | DELETE | `/users/account` | Hapus akun permanen |

---

### `aiService.js`

| Fungsi | Metode | Endpoint | Keterangan |
|---|---|---|---|
| `predictFromChat(teks)` | POST | `/transactions/analyze` | Kirim teks chat WhatsApp ke AI untuk diekstrak |
| `tanyaAI(history, message)` | POST | `/tanya-ai` | Kirim pesan + riwayat chat ke AI (Google Gemini via backend) |

Error `predictFromChat` ditangani dengan pesan user-friendly berdasarkan status HTTP (422, 401, 500).

---

### `transactionService.js`

| Fungsi | Metode | Endpoint | Keterangan |
|---|---|---|---|
| `saveTransactions(extractionId, products)` | POST | `/transactions` | Simpan hasil konfirmasi AI |
| `getTransactions({ tanggal })` | GET | `/transactions/report` | Data transaksi harian untuk Dashboard |
| `getMonthlyReport(bulan, tahun)` | GET | `/report/monthly` | Data laporan bulanan + kalkulasi top products |

`getMonthlyReport` melakukan transformasi data di sisi klien: menghitung `daily_summary` per tanggal, agregasi `top_products` 5 terbesar, dan `rata_rata_harian` berdasarkan jumlah hari yang memiliki transaksi.

---

### `supabaseClient.js`
Inisialisasi Supabase JS client menggunakan `VITE_SUPABASE_URL` dan `VITE_SUPABASE_ANON_KEY`. Digunakan oleh `authService.js` khusus untuk alur reset dan update password yang melewati Supabase Auth secara langsung.

---

## Hooks

### `useAuth.js`

Custom hook yang membungkus logika autentikasi untuk digunakan di komponen:

| Fungsi/State | Keterangan |
|---|---|
| `handleLogin(email, password)` | Panggil `authService.login`, tampilkan toast, redirect ke `/dashboard` |
| `handleRegister(nama, email, password)` | Panggil `authService.register`, tampilkan toast, redirect ke `/login` |
| `handleLogout()` | Panggil `authService.logout`, redirect ke `/login` |
| `loading` | Boolean untuk menonaktifkan tombol saat proses berlangsung |

---

### `useTransactions.js`

Custom hook untuk mengambil data transaksi harian dari backend. Menerima parameter `tanggal` (string `YYYY-MM-DD`) dan otomatis re-fetch setiap kali tanggal berubah via `useEffect`.

**Return value:** `{ data, loading, error }`

---

## Context

### `ThemeContext.jsx`

Context global untuk tema aplikasi (light/dark). Preferensi disimpan ke `localStorage` dengan key `ck_theme` dan diaplikasikan sebagai atribut `data-theme` pada elemen `<html>`, sehingga DaisyUI dapat menerapkan tema yang sesuai secara global.

**Nilai yang disediakan:**

| Nilai | Tipe | Keterangan |
|---|---|---|
| `theme` | `'light'` \| `'dark'` | Tema aktif saat ini |
| `toggleTheme()` | function | Beralih antara light dan dark |

---

## Utils

### `formatRupiah.js`

Fungsi helper `formatRupiah(angka)` untuk memformat angka ke format mata uang Rupiah Indonesia menggunakan `Intl.NumberFormat('id-ID')`.

Contoh: `formatRupiah(15000)` → `"Rp 15.000"`

Menangani nilai `null`, `undefined`, dan `NaN` dengan mengembalikan `"Rp 0"`.

---

## Deployment

Frontend di-deploy ke **Vercel**. File `vercel.json` dikonfigurasi dengan rewrite catch-all agar semua path diarahkan ke `index.html`, sesuai kebutuhan React Router SPA:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

Build command: `npm run build` — output folder: `dist/`.

---

## Koneksi ke Anggota Tim

| Anggota | Bagian yang Terhubung |
|---|---|
| **FS-2 Reihan** (Backend Express.js) | `authService.js` → `POST /auth/register`, `POST /auth/login`, `PUT /users/profile`, `DELETE /users/account` |
| **FS-2 Reihan** (Backend Express.js) | `transactionService.js` → `POST /transactions`, `GET /transactions/report`, `GET /report/monthly` |
| **FS-2 Reihan** (Backend Express.js) | `aiService.js` → `POST /transactions/analyze`, `POST /tanya-ai` |
| **AI-2 Denny** (FastAPI) | Endpoint `/transactions/analyze` di backend meneruskan request ke model AI FastAPI |
| **DS-2 Salman** | Data transaksi yang diinput melalui frontend ini menjadi sumber analisis di dashboard Streamlit |
