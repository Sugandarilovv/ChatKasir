# Frontend - Alfan Ramadhan

Repositori ini berisi kode sumber **Front-End** aplikasi **ChatKasir** — aplikasi pencatat keuangan berbasis AI untuk UMKM. Pengguna cukup *copy-paste* teks chat WhatsApp pesanan pelanggan, lalu sistem AI akan mengekstrak item, jumlah, dan harga secara otomatis.

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
- [Assets & Public](#assets--public)
- [Dokumentasi Tambahan](#dokumentasi-tambahan)
- [Koneksi ke Anggota Tim](#koneksi-ke-anggota-tim)

---

## Tech Stack

| Kebutuhan | Library | Versi |
|---|---|---|
| Framework UI | React | ^18.3.1 |
| Build Tool | Vite | ^5.3.1 |
| Styling | Tailwind CSS + DaisyUI | ^4.0.0 / ^5.0.0 |
| Routing | react-router-dom | ^6.23.1 |
| HTTP Client | Axios | ^1.7.2 |
| Form & Validasi | react-hook-form | ^7.51.5 |
| Grafik | Recharts | ^2.12.7 |
| Notifikasi Toast | react-hot-toast | ^2.4.1 |
| Date Picker | react-datepicker | ^9.1.0 |
| Format Tanggal | date-fns | ^4.1.0 |

---

## Struktur Folder

```
frontend/
├── .env                     # Konfigurasi URL environment (tidak di-commit ke git)
├── .env.example             # Template .env untuk developer lain
├── .gitkeep                 # Menjaga folder tetap ada di git walau kosong
├── index.html               # Entry point HTML aplikasi
├── package.json             # Dependensi dan script npm
├── package-lock.json        # Lock file dependensi
├── vite.config.js           # Konfigurasi Vite (plugin React + Tailwind)
├── docs/
│   └── ui-reference.md      # Dokumentasi keputusan desain UI
├── public/
│   └── logo.png             # Logo aplikasi (ikon browser/favicon)
└── src/
    ├── main.jsx             # Entry point React (render ke #root)
    ├── App.jsx              # Router utama + ProtectedRoute
    ├── index.css            # Global CSS (Tailwind, DaisyUI, animasi)
    ├── assets/
    │   └── logo.png         # Logo yang dipakai di dalam komponen React
    ├── components/
    │   ├── charts/
    │   │   └── RevenueBarChart.jsx   # Bar chart pemasukan harian
    │   ├── layout/
    │   │   ├── MainLayout.jsx        # Wrapper layout utama (Navbar + Sidebar)
    │   │   ├── Navbar.jsx            # Header navigasi atas
    │   │   └── Sidebar.jsx           # Navigasi samping
    │   └── ui/
    │       ├── EmptyState.jsx        # Tampilan saat data kosong
    │       ├── LoadingSkeleton.jsx   # Skeleton loading tabel
    │       ├── SummaryCard.jsx       # Kartu ringkasan angka
    │       └── Toast.jsx             # Sistem notifikasi toast custom
    ├── context/
    │   └── ThemeContext.jsx          # Global state tema (light/dark)
    ├── hooks/
    │   ├── useAuth.js                # Logic login, register, logout
    │   └── useTransactions.js        # Fetch data transaksi harian
    ├── pages/
    │   ├── Login.jsx                 # Halaman masuk akun
    │   ├── Register.jsx              # Halaman daftar akun baru
    │   ├── LupaPassword.jsx          # Reset password via OTP
    │   ├── InputChat.jsx             # Input teks chat WhatsApp
    │   ├── Konfirmasi.jsx            # Konfirmasi & edit hasil AI
    │   ├── Dashboard.jsx             # Tabel transaksi harian
    │   ├── Laporan.jsx               # Laporan keuangan bulanan
    │   ├── EditProfil.jsx            # Edit nama, email, foto profil
    │   └── Pengaturan.jsx            # Pengaturan akun & preferensi
    ├── services/
    │   ├── axiosInstance.js          # Instance Axios + interceptor JWT
    │   ├── authService.js            # Fungsi register, login, logout
    │   ├── aiService.js              # Koneksi ke API model AI (FastAPI)
    │   └── transactionService.js     # CRUD transaksi & laporan bulanan
    └── utils/
        └── formatRupiah.js           # Helper format angka ke Rupiah
```

---

## Konfigurasi Environment

Salin file `.env.example` menjadi `.env`, lalu sesuaikan isinya:

```bash
cp .env.example .env
```

Isi `.env`:

```env
# URL backend FS-2 Reihan (Express.js)
VITE_API_BASE_URL=http://localhost:3000

# URL API model AI-2 Denny (FastAPI)
VITE_AI_API_URL=http://localhost:8000
```

> **Catatan:** Semua service saat ini masih menggunakan **mode mock** (`USE_MOCK = true`). Ubah nilainya menjadi `false` di masing-masing file service setelah backend tersedia.

---

## Cara Menjalankan

```bash
# Install dependensi
npm install

# Jalankan dev server
npm run dev

# Build untuk produksi
npm run build

# Preview hasil build
npm run preview
```

Aplikasi akan berjalan di `http://localhost:5173` secara default.

---

## Halaman (Pages)

### `Login.jsx` — `/login`
Halaman masuk akun. Menampilkan form email dan password dengan validasi client-side menggunakan `react-hook-form`. Terdapat panel kiri bergaya gelap (green-950) dengan statistik aplikasi (jumlah UMKM aktif, transaksi, akurasi AI). Setelah login berhasil, token JWT dan data user disimpan ke `localStorage` lalu diarahkan ke `/dashboard`.

### `Register.jsx` — `/register`
Halaman pendaftaran akun baru. Form berisi nama, email, password, dan konfirmasi password dengan validasi agar kedua password cocok. Desain dua panel serupa dengan Login, dilengkapi daftar fitur unggulan aplikasi.

### `LupaPassword.jsx` — `/lupa-password`
Alur reset password tiga langkah: (1) masukkan email, (2) verifikasi kode OTP dengan countdown timer 30 detik dan opsi kirim ulang, (3) buat password baru. Belum terhubung ke backend nyata.

### `InputChat.jsx` — `/input` *(Protected)*
Halaman inti untuk memasukkan teks chat WhatsApp. Pengguna bisa mengetik manual, paste dari clipboard, atau memilih contoh teks yang tersedia. Setelah teks diproses, hasilnya dikirim ke `aiService` lalu disimpan ke `sessionStorage` dan pengguna diarahkan ke halaman Konfirmasi.

### `Konfirmasi.jsx` — `/konfirmasi` *(Protected)*
Menampilkan hasil ekstraksi AI berupa tabel item (nama produk, jumlah, harga satuan, subtotal). Pengguna dapat mengedit setiap field, menghapus item, atau menambah item baru secara manual sebelum menyimpan ke database. Data diambil dari `sessionStorage` yang diisi oleh halaman InputChat.

### `Dashboard.jsx` — `/dashboard` *(Protected)*
Menampilkan rekap transaksi harian dengan date picker untuk memilih tanggal. Dilengkapi tiga `SummaryCard` (total transaksi, total nominal, rata-rata per transaksi) dan tabel lengkap semua transaksi pada hari tersebut. Ada tombol navigasi ke halaman InputChat jika data kosong.

### `Laporan.jsx` — `/laporan` *(Protected)*
Laporan keuangan bulanan. Pengguna memilih bulan dan tahun untuk melihat ringkasan pemasukan, total transaksi, rata-rata harian, bar chart pemasukan harian (`RevenueBarChart`), dan tabel 5 produk terlaris beserta total terjual dan pendapatannya.

### `EditProfil.jsx` — `/profil` *(Protected)*
Form untuk mengubah nama, email, dan foto profil. Foto dapat diunggah dari perangkat dan ditampilkan sebagai preview. Perubahan disimpan ke `localStorage` (belum terhubung ke backend).

### `Pengaturan.jsx` — `/pengaturan` *(Protected)*
Halaman pengaturan akun berisi toggle-toggle preferensi (notifikasi, tema, dll.) dengan komponen `Toggle` custom. Juga tersedia opsi hapus akun dan ganti password.

---

## Komponen (Components)

### Layout

#### `MainLayout.jsx`
Wrapper layout untuk semua halaman yang memerlukan autentikasi. Menyusun `Navbar` di atas dan `Sidebar` di samping kiri, lalu merender `children` di area konten utama. Mendukung toggle sidebar mobile melalui state `isMobileOpen`.

#### `Navbar.jsx`
Header aplikasi yang sticky di bagian atas. Berisi:
- Tombol hamburger (hanya muncul di mobile) untuk membuka sidebar
- Logo dan nama "ChatKasir"
- Tombol toggle tema (light/dark)
- Info nama dan email user
- Avatar user dengan dropdown menu: Ubah Profil, Pengaturan Akun, daftar akun tersimpan (switch account), dan tombol Keluar

#### `Sidebar.jsx`
Navigasi samping dengan tiga menu utama: **Catat Transaksi** (`/input`), **Dashboard** (`/dashboard`), dan **Laporan** (`/laporan`). Di desktop dapat di-collapse menjadi mode ikon-saja. Di mobile tampil sebagai overlay dengan backdrop blur. Aktif-tidaknya menu ditandai dengan highlight hijau dan indikator garis vertikal.

### UI Reusable

#### `SummaryCard.jsx`
Kartu statistik ringkasan. Menerima props `title`, `value`, `type` (`'number'` atau `'rupiah'`), `icon`, dan `loading`. Jika `loading` bernilai `true`, menampilkan skeleton pulse. Jika `type` adalah `'rupiah'`, nilai diformat menggunakan `formatRupiah`.

#### `Toast.jsx`
Sistem notifikasi toast custom (tidak menggunakan library eksternal). Menggunakan React Context (`ToastCtx`) dan fungsi global `showToast(msg, type)` yang bisa dipanggil dari mana saja tanpa perlu hook. Mendukung empat tipe: `success`, `error`, `info`, `warning`, masing-masing dengan warna dan ikon berbeda. Toast otomatis hilang setelah 1,8 detik dengan animasi keluar.

#### `EmptyState.jsx`
Komponen tampilan kosong yang ditampilkan saat tidak ada data. Menampilkan ikon 📭, pesan teks, dan opsional tombol aksi (props `action: { label, onClick }`).

#### `LoadingSkeleton.jsx`
Skeleton loading berupa baris-baris animasi pulse untuk tabel transaksi. Menerima props `rows` (default 5) untuk mengatur jumlah baris skeleton yang ditampilkan.

### Charts

#### `RevenueBarChart.jsx`
Bar chart pemasukan harian menggunakan library Recharts. Menampilkan data `daily_summary` dari laporan bulanan dalam bentuk grafik batang yang responsif (`ResponsiveContainer`). Mendukung mode gelap dan terang.

---

## Services

### `axiosInstance.js`
Membuat instance Axios terpusat dengan `baseURL` dari `VITE_API_BASE_URL`. Dilengkapi dua interceptor:
- **Request interceptor:** Otomatis menyisipkan token JWT dari `localStorage` ke header `Authorization: Bearer <token>`.
- **Response interceptor:** Jika respons `401 Unauthorized`, otomatis menghapus token dan user dari `localStorage` lalu redirect ke `/login`.

### `authService.js`
Fungsi-fungsi autentikasi yang menggunakan `axiosInstance`:
- `register(nama, email, password)` — POST `/auth/register`
- `login(email, password)` — POST `/auth/login`, menyimpan token dan user ke `localStorage`
- `logout()` — Menghapus token dan user dari `localStorage`
- `getCurrentUser()` — Membaca dan mem-parse data user dari `localStorage`

> Saat ini `USE_MOCK = true`, sehingga login dan register mensimulasikan respons berhasil tanpa menyentuh backend.

### `aiService.js`
Fungsi `predictFromChat(teks)` yang mengirim teks chat ke endpoint `/predict` di API AI (FastAPI). Menggunakan instance Axios tersendiri dengan `baseURL` dari `VITE_AI_API_URL` dan timeout 15 detik.

> Saat ini `USE_MOCK = true`, sehingga mengembalikan dua item dummy (Nasi Goreng Spesial dan Es Teh Manis) setelah simulasi delay 1 detik.

### `transactionService.js`
Tiga fungsi untuk mengelola transaksi:
- `saveTransactions(items)` — POST `/transactions` untuk menyimpan hasil konfirmasi AI
- `getTransactions({ tanggal, page, limit })` — GET `/transactions` untuk data tabel Dashboard
- `getMonthlyReport(bulan, tahun)` — GET `/report/monthly` untuk data halaman Laporan

> Saat ini `USE_MOCK = true` dengan data dummy berupa 5 transaksi sampel dan 30 hari data historis acak untuk grafik.

---

## Hooks

### `useAuth.js`
Custom hook yang membungkus logika autentikasi:
- `handleLogin(email, password)` — Memanggil `authService.login`, menampilkan toast sukses/error, dan redirect ke `/dashboard`
- `handleRegister(nama, email, password)` — Memanggil `authService.register`, menampilkan toast, dan redirect ke `/login`
- `handleLogout()` — Memanggil `authService.logout` dan redirect ke `/login`
- `loading` — State boolean untuk menonaktifkan tombol saat proses berlangsung

### `useTransactions.js`
Custom hook untuk mengambil data transaksi harian. Menerima parameter `tanggal` (string format `YYYY-MM-DD`) dan secara otomatis re-fetch setiap kali tanggal berubah (via `useEffect`). Mengembalikan `{ data, loading, error, refetch }`.

---

## Context

### `ThemeContext.jsx`
Context global untuk tema aplikasi (light/dark). Menyimpan preferensi tema ke `localStorage` dengan key `ck_theme` dan mengaplikasikannya sebagai atribut `data-theme` di `<html>`. Menyediakan:
- `theme` — nilai `'light'` atau `'dark'`
- `toggleTheme()` — fungsi untuk beralih tema

---

## Utils

### `formatRupiah.js`
Fungsi helper `formatRupiah(angka)` untuk memformat angka ke format mata uang Rupiah Indonesia menggunakan `Intl.NumberFormat`. Contoh: `formatRupiah(15000)` menghasilkan `"Rp 15.000"`. Menangani nilai `null` dan `undefined` dengan mengembalikan `"Rp 0"`.

---

## Assets & Public

### `src/assets/logo.png`
Logo aplikasi ChatKasir yang diimpor langsung ke dalam komponen React (misalnya di `Navbar.jsx` dan halaman `Login.jsx`/`Register.jsx`). Diproses oleh Vite saat build.

### `public/logo.png`
Logo yang sama namun disimpan di folder `public` agar dapat diakses sebagai URL statis `/logo.png`. Digunakan sebagai favicon di `index.html`.

---

## File Root

### `index.html`
Entry point HTML tunggal (SPA). Mendefinisikan:
- Charset UTF-8 dan viewport responsif
- Judul halaman: **"ChatKasir — Pencatat Keuangan UMKM"**
- Favicon dari `/logo.png`
- Font **Plus Jakarta Sans** dari Google Fonts (weight 400–800)
- `<div id="root">` sebagai mount point React
- Script `src/main.jsx` sebagai entry module

### `package.json`
Mendefinisikan nama proyek (`chatkasir-frontend`), versi (`1.0.0`), tipe modul ESM, dan tiga script npm: `dev`, `build`, dan `preview`.

### `vite.config.js`
Konfigurasi Vite dengan dua plugin: `@vitejs/plugin-react` (untuk JSX dan Fast Refresh) dan `@tailwindcss/vite` (integrasi Tailwind CSS langsung via Vite tanpa PostCSS terpisah).

### `src/index.css`
File CSS global yang di-import di `main.jsx`. Berisi:
- Konfigurasi Tailwind CSS dan DaisyUI (tema light dan dark)
- Font global: Plus Jakarta Sans untuk seluruh elemen
- Definisi animasi keyframes: `fadeUp`, `fadeIn`, `slideDown`, `toastIn`, `toastOut`
- Utility class animasi: `.animate-fade-up`, `.animate-fade-in`, `.animate-slide-down`, `.toast-in`, `.toast-out`
- Kelas delay animasi: `.delay-1` hingga `.delay-5`

### `src/main.jsx`
File bootstrap React. Merender komponen `<App />` ke dalam elemen `#root` dengan `createRoot` dan membungkusnya dalam `<StrictMode>`.

### `src/App.jsx`
Komponen root yang menyusun seluruh routing aplikasi menggunakan `BrowserRouter`. Mendefinisikan komponen `ProtectedRoute` (mengecek keberadaan token di `localStorage`, redirect ke `/login` jika tidak ada). Semua halaman yang membutuhkan login dibungkus dengan `ProtectedRoute`. Root path `/` dan path yang tidak dikenal diarahkan ke `/login`.

### `.env` dan `.env.example`
File konfigurasi environment berisi dua variabel:
- `VITE_API_BASE_URL` — URL backend Express.js (FS-2 Reihan), default `http://localhost:3000`
- `VITE_AI_API_URL` — URL API model AI FastAPI (AI-2 Denny), default `http://localhost:8000`

### `.gitkeep`
File kosong untuk memastikan folder tetap terlacak oleh Git meskipun tidak ada isi file lain di dalamnya.

---

## Dokumentasi Tambahan

### `docs/ui-reference.md`
Dokumen referensi keputusan desain UI yang dibuat pada 21 April 2026. Berisi:
- Tabel alasan pemilihan setiap library UI
- Panduan sistem warna menggunakan DaisyUI (primary, base, error, success)
- Daftar komponen yang dibangun beserta fungsinya
- Tabel semua halaman beserta route dan keterangannya
- Tabel koneksi ke anggota tim lain
- Referensi inspirasi desain (Moka POS, Majoo)

---

## Koneksi ke Anggota Tim

| Anggota | Bagian yang terhubung |
|---|---|
| **FS-2 Reihan** (Backend Express.js) | `authService.js` → `POST /auth/register` dan `/auth/login` |
| **FS-2 Reihan** (Backend Express.js) | `transactionService.js` → `GET/POST /transactions`, `GET /report/monthly` |
| **AI-2 Denny** (FastAPI) | `aiService.js` → `POST /predict` untuk ekstraksi teks chat |
| **DS-2 Salman** | Data yang diinput melalui frontend ini menjadi sumber analisis di dashboard Streamlit |
