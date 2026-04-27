import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import MainLayout from '../components/layout/MainLayout'
import { useTheme } from '../context/ThemeContext'
import toast from 'react-hot-toast'

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
        <p className={`text-xs font-bold uppercase tracking-widest ${isDark ? 'text-gray-400' : 'text-gray-400'}`}>{title}</p>
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

export default function Pengaturan() {
  const navigate            = useNavigate()
  const { theme, toggleTheme } = useTheme()
  const isDark              = theme === 'dark'

  const [notifTransaksi, setNotifTransaksi] = useState(() => JSON.parse(localStorage.getItem('ck_notif_transaksi') ?? 'true'))
  const [notifLaporan,   setNotifLaporan]   = useState(() => JSON.parse(localStorage.getItem('ck_notif_laporan')   ?? 'false'))
  const [autoSave,       setAutoSave]       = useState(() => JSON.parse(localStorage.getItem('ck_autosave')        ?? 'true'))

  function handleToggle(key, val, setter) {
    setter(val)
    localStorage.setItem(key, JSON.stringify(val))
    toast.success(val ? 'Diaktifkan' : 'Dinonaktifkan', { icon: val ? '✅' : '🔕' })
  }

  function handleHapusData() {
    if (!window.confirm('Yakin ingin menghapus semua data lokal? Tindakan ini tidak bisa dibatalkan.')) return
    const keysToKeep = ['token', 'user']
    Object.keys(localStorage).forEach((k) => { if (!keysToKeep.includes(k)) localStorage.removeItem(k) })
    toast.success('Data lokal berhasil dihapus.')
  }

  function handleUbahPassword() {
    toast('Fitur ini membutuhkan koneksi ke backend FS-2.', { icon: '🔒' })
  }

  return (
    <MainLayout>
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

        {/* Zona Bahaya */}
        <Section title="Zona Berbahaya" isDark={isDark}>
          <Row icon="🗑️" label="Hapus Akun" desc="Hapus cache & preferensi tersimpan"
            isDark={isDark} danger onClick={handleHapusData}
            right={<span className="text-red-400 text-xs">→</span>}
          />
        </Section>

        <p className={`text-center text-xs mt-4 ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
          ChatKasir · CC26-PSU065 · Coding Camp 2026 DBS Foundation
        </p>
      </div>
    </MainLayout>
  )
}