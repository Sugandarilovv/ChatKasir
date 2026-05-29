import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import MainLayout from '../components/layout/MainLayout'
import { useTheme } from '../context/ThemeContext'
import toast from 'react-hot-toast'
import { deleteAccount, logout } from '../services/authService'

function Toggle({ value, onChange }) {
  return (
    <button
      onClick={() => onChange(!value)}
      className="relative w-11 h-6 rounded-full transition-colors duration-300 focus:outline-none"
      style={{ background: value ? '#16a34a' : '#d1d5db' }}
    >
      <span
        className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform duration-300"
        style={{ transform: value ? 'translateX(20px)' : 'translateX(0)' }}
      />
    </button>
  )
}

function Section({ title, children, isDark }) {
  return (
    <div className="rounded-2xl overflow-hidden mb-4" style={{ border: `1px solid ${isDark ? '#1f2937' : '#e2e8f0'}`, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
      <div className="px-5 py-3 border-b" style={{ borderColor: isDark ? '#1f2937' : '#f1f5f9', background: isDark ? '#0f172a' : '#fafffe' }}>
        <p className="text-xs font-bold uppercase tracking-widest text-gray-400">{title}</p>
      </div>
      <div style={{ background: isDark ? '#111827' : '#fff' }}>{children}</div>
    </div>
  )
}

function Row({ icon, label, desc, right, isDark, onClick, danger }) {
  return (
    <div
      onClick={onClick}
      className={`flex items-center justify-between px-5 py-4 border-b last:border-b-0 transition-colors ${onClick ? 'cursor-pointer' : ''} ${onClick ? (isDark ? 'hover:bg-gray-800' : 'hover:bg-gray-50') : ''}`}
      style={{ borderColor: isDark ? '#1f2937' : '#f8fafc' }}
    >
      <div className="flex items-center gap-3">
        <span style={{ fontSize: 18 }}>{icon}</span>
        <div>
          <p className={`text-sm font-semibold ${danger ? 'text-red-500' : isDark ? 'text-gray-200' : 'text-gray-700'}`}>{label}</p>
          {desc && <p className={`text-xs mt-0.5 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{desc}</p>}
        </div>
      </div>
      {right && <div>{right}</div>}
    </div>
  )
}

// ── Modal konfirmasi hapus akun ──────────────────────────────────────────────
function ModalHapusAkun({ onConfirm, onCancel, loading, isDark }) {
  const [konfirmasi, setKonfirmasi] = useState('')
  const bolehHapus = konfirmasi === 'HAPUS'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }}>
      <div className="w-full max-w-sm rounded-2xl p-6 shadow-2xl"
        style={{ background: isDark ? '#1f2937' : '#ffffff', border: `1px solid ${isDark ? '#374151' : '#fecaca'}` }}>

        <div className="w-14 h-14 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
          <span style={{ fontSize: 28 }}>⚠️</span>
        </div>

        <h3 className="text-lg font-extrabold text-center text-red-600 mb-2">Hapus Akun Permanen</h3>
        <p className={`text-sm text-center mb-4 leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
          Tindakan ini akan menghapus <strong>akun, semua transaksi, dan riwayat chat</strong> secara permanen dari server. Tidak bisa dibatalkan.
        </p>

        <div className="mb-4">
          <p className={`text-xs font-bold mb-2 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            Ketik <span className="text-red-500 font-black">HAPUS</span> untuk konfirmasi:
          </p>
          <input
            value={konfirmasi}
            onChange={(e) => setKonfirmasi(e.target.value.toUpperCase())}
            placeholder="Ketik HAPUS di sini..."
            className="w-full px-4 py-2.5 rounded-xl border text-sm font-bold outline-none focus:ring-2 focus:ring-red-400 transition-all"
            style={{
              background:   isDark ? '#374151' : '#fff',
              borderColor:  bolehHapus ? '#ef4444' : (isDark ? '#4b5563' : '#e5e7eb'),
              color:        isDark ? '#f1f5f9' : '#111827',
            }}
          />
        </div>

        <div className="flex gap-3">
          <button onClick={onCancel} disabled={loading}
            className="flex-1 py-2.5 rounded-xl text-sm font-bold transition-all"
            style={{ background: isDark ? '#374151' : '#f1f5f9', color: isDark ? '#d1d5db' : '#6b7280' }}>
            Batal
          </button>
          <button onClick={onConfirm} disabled={!bolehHapus || loading}
            className="flex-1 py-2.5 rounded-xl text-sm font-bold text-white transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            style={{ background: bolehHapus && !loading ? '#ef4444' : '#fca5a5' }}>
            {loading
              ? <><svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                </svg>Menghapus...</>
              : '🗑️ Hapus Sekarang'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Main Component ───────────────────────────────────────────────────────────
export default function Pengaturan() {
  const navigate               = useNavigate()
  const { theme, toggleTheme } = useTheme()
  const isDark                 = theme === 'dark'

  const [notifTransaksi, setNotifTransaksi] = useState(() => JSON.parse(localStorage.getItem('ck_notif_transaksi') ?? 'true'))
  const [notifLaporan,   setNotifLaporan]   = useState(() => JSON.parse(localStorage.getItem('ck_notif_laporan')   ?? 'false'))
  const [autoSave,       setAutoSave]       = useState(() => JSON.parse(localStorage.getItem('ck_autosave')        ?? 'true'))

  const [showModal,    setShowModal]    = useState(false)
  const [loadingHapus, setLoadingHapus] = useState(false)

  function handleToggle(key, val, setter) {
    setter(val)
    localStorage.setItem(key, JSON.stringify(val))
    toast.success(val ? 'Diaktifkan' : 'Dinonaktifkan', { icon: val ? '✅' : '🔕' })
  }

  // ── Hapus akun — kirim ke DELETE /users/account di backend ─────────────────
  async function handleHapusAkun() {
    setLoadingHapus(true)
    try {
      // deleteAccount() → api.delete('/users/account') → userController.deleteAccount
      // Backend hapus dari tabel users + supabase.auth.admin.deleteUser
      await deleteAccount()

      // Bersihkan semua data lokal setelah akun berhasil dihapus
      logout()
      localStorage.clear()

      // Tampilkan toast dulu, navigate setelah toast sempat terbaca user
      toast.success('Akun berhasil dihapus secara permanen.', {
        duration: 2500,
        icon: '🗑️',
      })
      setTimeout(() => navigate('/login'), 2500)
    } catch (err) {
      const msg = err.response?.data?.error || 'Gagal menghapus akun. Coba lagi.'
      toast.error(msg)
      setLoadingHapus(false)
      setShowModal(false)
    }
  }

  return (
    <MainLayout>
      {showModal && (
        <ModalHapusAkun
          isDark={isDark}
          loading={loadingHapus}
          onConfirm={handleHapusAkun}
          onCancel={() => setShowModal(false)}
        />
      )}

      <div className="max-w-lg mx-auto animate-fade-up">

        {/* Header */}
        <div className="flex items-center gap-3 mb-7">
          <button onClick={() => navigate(-1)}
            className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all hover:scale-105 ${isDark ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-600'}`}>
            ←
          </button>
          <div>
            <h2 className="text-2xl font-extrabold">Pengaturan</h2>
            <p className={`text-sm mt-0.5 ${isDark ? 'text-gray-400' : 'text-gray-400'}`}>Kelola preferensi aplikasi kamu</p>
          </div>
        </div>

        {/* Tampilan */}
        <Section title="Tampilan" isDark={isDark}>
          <Row
            icon={isDark ? '☀️' : '🌙'}
            label="Mode Gelap"
            desc={isDark ? 'Tampilan gelap aktif' : 'Tampilan terang aktif'}
            isDark={isDark}
            right={<Toggle value={isDark} onChange={toggleTheme} />}
          />
        </Section>

        {/* Notifikasi */}
        <Section title="Notifikasi" isDark={isDark}>
          <Row icon="🔔" label="Notifikasi Transaksi" desc="Tampilkan notif saat transaksi tersimpan"
            isDark={isDark}
            right={<Toggle value={notifTransaksi} onChange={(v) => handleToggle('ck_notif_transaksi', v, setNotifTransaksi)} />}
          />
          <Row icon="📊" label="Notifikasi Laporan" desc="Ingatkan saat laporan bulanan tersedia"
            isDark={isDark}
            right={<Toggle value={notifLaporan} onChange={(v) => handleToggle('ck_notif_laporan', v, setNotifLaporan)} />}
          />
        </Section>

        {/* Data & Sinkronisasi */}
        <Section title="Data & Sinkronisasi" isDark={isDark}>
          <Row icon="💾" label="Simpan Otomatis" desc="Simpan draft input secara otomatis"
            isDark={isDark}
            right={<Toggle value={autoSave} onChange={(v) => handleToggle('ck_autosave', v, setAutoSave)} />}
          />
        </Section>

        {/* Keamanan */}
        <Section title="Keamanan" isDark={isDark}>
          <Row icon="🛡️" label="Versi Aplikasi" desc="ChatKasir v1.0.0 — CC26-PSU065" isDark={isDark} />
        </Section>

        {/* Zona Berbahaya */}
        <Section title="Zona Berbahaya" isDark={isDark}>
          <Row icon="🗑️" label="Hapus Akun"
            desc="Hapus akun & semua data transaksi secara permanen"
            isDark={isDark} danger
            onClick={() => setShowModal(true)}
            right={<span className="text-red-400 text-xs font-bold">→</span>}
          />
        </Section>

        <p className={`text-center text-xs mt-4 ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
          ChatKasir · CC26-PSU065 · Coding Camp 2026 DBS Foundation
        </p>
      </div>
    </MainLayout>
  )
}