import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import MainLayout from '../components/layout/MainLayout'
import { useTheme } from '../context/ThemeContext'
import toast from 'react-hot-toast'
import { updateProfile, getCurrentUser } from '../services/authService'

export default function EditProfil() {
  const navigate  = useNavigate()
  const { theme } = useTheme()
  const isDark    = theme === 'dark'
  const fileRef   = useRef(null)

  // Baca user dari localStorage (sudah berisi nama & foto setelah login)
  const user = getCurrentUser() || {}

  const [nama,    setNama]    = useState(user.nama  || '')
  const [email,   setEmail]   = useState(user.email || '')
  const [foto,    setFoto]    = useState(user.foto  || null)
  const [fotoFile, setFotoFile] = useState(null) // file mentah untuk upload
  const [saving,  setSaving]  = useState(false)

  function handleFotoChange(e) {
    const file = e.target.files[0]
    if (!file) return
    if (file.size > 2 * 1024 * 1024) {
      toast.error('Ukuran foto maksimal 2MB.')
      return
    }
    setFotoFile(file)
    
    // Proses kompresi gambar sebelum diset menjadi Base64
    const reader = new FileReader()
    reader.onload = (event) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const MAX_WIDTH = 400
        const MAX_HEIGHT = 400
        let width = img.width
        let height = img.height

        // Kalkulasi rasio ukuran baru
        if (width > height) {
          if (width > MAX_WIDTH) {
            height *= MAX_WIDTH / width
            width = MAX_WIDTH
          }
        } else {
          if (height > MAX_HEIGHT) {
            width *= MAX_HEIGHT / height
            height = MAX_HEIGHT
          }
        }

        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)

        // Konversi ke format JPEG dengan kualitas 70% agar base64 sangat kecil
        const compressedDataUrl = canvas.toDataURL('image/jpeg', 0.7)
        setFoto(compressedDataUrl) // preview & payload base64 yang sudah kecil
      }
      img.src = event.target.result
    }
    reader.readAsDataURL(file)
  }

  async function handleSimpan() {
    // Tidak ada validasi yang block — nama boleh tidak diubah,
    // foto boleh tidak diubah. Minimal salah satu berubah baru kirim.
    const namaChanged = nama.trim() !== (user.nama || '')
    const fotoChanged = fotoFile !== null

    if (!namaChanged && !fotoChanged) {
      toast('Tidak ada perubahan.', { icon: 'ℹ️' })
      return
    }

    setSaving(true)
    try {
      // Siapkan payload — hanya kirim field yang berubah
      const newNama = namaChanged ? nama.trim()  : undefined
      const newFoto = fotoChanged ? foto          : undefined  // base64 string yang sudah dikompres

      await updateProfile(newNama, newFoto)
      toast.success('Profil berhasil diperbarui!')
      navigate(-1)
    } catch (err) {
      const msg = err.response?.data?.error
               || err.response?.data?.message
               || 'Gagal menyimpan profil.'
      toast.error(msg)
    } finally {
      setSaving(false)
    }
  }

  const initial = (nama || email || 'U')[0].toUpperCase()

  // Warna input sesuai tema
  const inputStyle = {
    borderColor: isDark ? '#374151' : '#e2e8f0',
    background:  isDark ? '#1f2937' : '#fff',
    color:       isDark ? '#f9fafb' : '#111827',
    boxShadow:   'none',
  }

  return (
    <MainLayout>
      <div className="max-w-lg mx-auto animate-fade-up">

        {/* Header */}
        <div className="flex items-center gap-3 mb-7">
          <button
            onClick={() => navigate(-1)}
            className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all hover:scale-105 ${
              isDark ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-600'
            }`}
          >
            ←
          </button>
          <div>
            <h2 className="text-2xl font-extrabold">Ubah Profil</h2>
            <p className={`text-sm mt-0.5 ${isDark ? 'text-gray-400' : 'text-gray-400'}`}>
              Perbarui nama dan foto kamu
            </p>
          </div>
        </div>

        <div
          className="rounded-2xl overflow-hidden"
          style={{
            border:     `1px solid ${isDark ? '#1f2937' : '#e2e8f0'}`,
            boxShadow:  '0 2px 16px rgba(0,0,0,0.06)',
          }}
        >
          {/* ── Foto Profil ── */}
          <div
            className="flex flex-col items-center py-8 px-6 border-b"
            style={{
              borderColor: isDark ? '#1f2937' : '#f1f5f9',
              background:  isDark ? '#0f172a' : '#f0fdf4',
            }}
          >
            <div className="relative group mb-4">
              <div
                className="w-24 h-24 rounded-full overflow-hidden flex items-center justify-center text-white text-3xl font-extrabold shadow-lg"
                style={{ background: 'linear-gradient(135deg,#16a34a,#14532d)' }}
              >
                {foto
                  ? <img src={foto} alt="foto profil" className="w-24 h-24 object-cover" />
                  : initial}
              </div>
              {/* Overlay hover */}
              <button
                onClick={() => fileRef.current?.click()}
                className="absolute inset-0 rounded-full flex items-center justify-center text-white text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity"
                style={{ background: 'rgba(0,0,0,0.45)' }}
              >
                Ganti Foto
              </button>
            </div>

            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFotoChange}
            />
            <button
              onClick={() => fileRef.current?.click()}
              className="text-sm font-semibold text-green-600 hover:text-green-700 transition-colors"
            >
              📷 Pilih foto dari perangkat
            </button>
            <p className={`text-xs mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
              JPG, PNG, maks. 2MB
            </p>
            {/* Indikator foto baru dipilih */}
            {fotoFile && (
              <p className="text-xs mt-2 text-green-600 font-semibold">
                ✓ Foto baru siap disimpan
              </p>
            )}
          </div>

          {/* ── Form ── */}
          <div
            className="p-6 space-y-5"
            style={{ background: isDark ? '#111827' : '#fff' }}
          >
            {/* Nama */}
            <div>
              <label className={`block text-sm font-semibold mb-1.5 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                Nama Lengkap
              </label>
              <input
                type="text"
                value={nama}
                onChange={(e) => setNama(e.target.value)}
                placeholder="Nama kamu"
                className="w-full px-4 py-3 rounded-xl border text-sm outline-none transition-all focus:ring-2 focus:ring-green-500 focus:border-green-500"
                style={inputStyle}
              />
            </div>

            {/* Email — hanya tampil, tidak bisa diedit */}
            <div>
              <label className={`block text-sm font-semibold mb-1.5 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                Email
                <span className="ml-2 text-xs font-normal text-gray-400">(tidak dapat diubah)</span>
              </label>
              <input
                type="email"
                value={email}
                disabled
                className="w-full px-4 py-3 rounded-xl border text-sm outline-none cursor-not-allowed opacity-60"
                style={inputStyle}
              />
            </div>
          </div>

          {/* ── Tombol Aksi ── */}
          <div
            className="px-6 py-4 flex gap-3 border-t"
            style={{
              borderColor: isDark ? '#1f2937' : '#f1f5f9',
              background:  isDark ? '#0f172a' : '#fafffe',
            }}
          >
            <button
              onClick={() => navigate(-1)}
              className={`flex-1 py-3 rounded-xl text-sm font-semibold transition-all ${
                isDark
                  ? 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              Batal
            </button>
            <button
              onClick={handleSimpan}
              disabled={saving}
              className="flex-1 py-3 rounded-xl text-sm font-bold text-white transition-all active:scale-95 disabled:opacity-60 flex items-center justify-center gap-2"
              style={{ background: '#16a34a' }}
            >
              {saving ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Menyimpan...
                </>
              ) : 'Simpan Perubahan'}
            </button>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}