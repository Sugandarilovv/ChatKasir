import { useNavigate } from 'react-router-dom'
import { useState, useRef, useEffect } from 'react'
import { logout } from '../../services/authService'
import { useTheme } from '../../context/ThemeContext'
import { showToast } from '../ui/Toast'

// IMPORT GAMBAR LOGO
import logoImg from '../../assets/logo.png' // Sesuaikan level folder jika perlu

export default function Navbar() {
  const navigate             = useNavigate()
  const { theme, toggleTheme } = useTheme()
  const [open, setOpen]      = useState(false)
  const dropRef              = useRef(null)
  const isDark               = theme === 'dark'

  const user    = JSON.parse(localStorage.getItem('user') || '{}')
  const initial = (user.nama || user.email || 'A')[0].toUpperCase()

  useEffect(() => {
    function handler(e) {
      if (dropRef.current && !dropRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const savedAccounts = JSON.parse(localStorage.getItem('ck_accounts') || '[]')

  function handleLogout() {
    setOpen(false)
    logout()
    showToast('Berhasil keluar.', 'info')
    navigate('/login')
  }

  function handleSwitchAccount(acc) {
    setOpen(false)
    const current = JSON.parse(localStorage.getItem('user') || '{}')
    if (current.email) {
      const accounts = JSON.parse(localStorage.getItem('ck_accounts') || '[]')
      const exists   = accounts.find((a) => a.email === current.email)
      if (!exists) {
        accounts.push(current)
        localStorage.setItem('ck_accounts', JSON.stringify(accounts))
      }
    }
    localStorage.setItem('user', JSON.stringify(acc))
    localStorage.setItem('token', acc.token || 'mock-token')
    showToast(`Beralih ke ${acc.nama || acc.email}`, 'success')
    window.location.href = '/dashboard'
  }

  return (
    <header
      className="h-16 flex items-center justify-between px-6 border-b sticky top-0 z-40 transition-colors duration-300"
      style={{
        background: isDark ? 'rgba(17,24,39,0.95)' : 'rgba(255,255,255,0.95)',
        backdropFilter: 'blur(10px)',
        borderColor: isDark ? '#1f2937' : '#f0fdf4',
      }}
    >
      {/* PERUBAHAN LOGO: Tidak mengarahkan ke dashboard, hanya div biasa */}
      <div className="flex items-center gap-3">
        <img 
          src={logoImg} 
          alt="Logo ChatKasir" 
          className="w-10 h-10 rounded-full shadow-sm object-cover" 
        />
        <span className={`font-extrabold text-lg tracking-tight hidden sm:block ${isDark ? 'text-white' : 'text-gray-800'}`}>
          ChatKasir
        </span>
      </div>

      <div className="flex items-center gap-3">
        {/* Toggle dark/light */}
        <button
          onClick={toggleTheme}
          className="w-9 h-9 rounded-xl flex items-center justify-center transition-all hover:scale-110 active:scale-95"
          style={{ background: isDark ? '#1f2937' : '#f0fdf4' }}
          title={isDark ? 'Mode Terang' : 'Mode Gelap'}
        >
          <span style={{ fontSize: 16 }}>{isDark ? '☀️' : '🌙'}</span>
        </button>

        {/* Info user */}
        <div className="hidden sm:flex flex-col items-end">
          <span className={`text-sm font-bold leading-none mb-0.5 ${isDark ? 'text-white' : 'text-gray-800'}`}>
            {user.nama || 'Alfan'}
          </span>
          <span className={`text-xs leading-none ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
            {user.email || ''}
          </span>
        </div>

        {/* Avatar + dropdown */}
        <div className="relative" ref={dropRef}>
          <button
            onClick={() => setOpen((v) => !v)}
            className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-white text-base shadow-md transition-all hover:ring-4 ring-green-100 active:scale-95 overflow-hidden"
            style={{ background: 'linear-gradient(135deg,#16a34a,#14532d)' }}
          >
            {user.foto
              ? <img src={user.foto} alt="foto" className="w-10 h-10 object-cover" />
              : initial}
          </button>

          {open && (
            <div
              className="absolute right-0 top-full mt-3 w-64 rounded-2xl border shadow-2xl overflow-hidden animate-slide-down z-50"
              style={{ background: isDark ? '#111827' : '#fff', borderColor: isDark ? '#1f2937' : '#f0f0f0' }}
            >
              {/* Header dropdown */}
              <div className="p-4 border-b" style={{ borderColor: isDark ? '#1f2937' : '#f5f5f5', background: isDark ? '#0f172a' : '#f0fdf4' }}>
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-white shrink-0 overflow-hidden"
                    style={{ background: 'linear-gradient(135deg,#16a34a,#14532d)' }}
                  >
                    {user.foto
                      ? <img src={user.foto} alt="foto" className="w-10 h-10 object-cover" />
                      : initial}
                  </div>
                  <div className="min-w-0">
                    <p className={`text-sm font-extrabold truncate ${isDark ? 'text-white' : 'text-gray-800'}`}>
                      {user.nama || 'Alfan'}
                    </p>
                    <p className={`text-xs truncate ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                      {user.email || ''}
                    </p>
                  </div>
                </div>
              </div>

              {/* Menu utama */}
              <div className="p-2">
                {[
                  { icon: '👤', label: 'Ubah Profil',     path: '/profil' },
                  { icon: '⚙️', label: 'Pengaturan Akun', path: '/pengaturan' },
                ].map((item) => (
                  <button
                    key={item.path}
                    onClick={() => { setOpen(false); navigate(item.path) }}
                    className={`w-full text-left px-3 py-2.5 text-sm font-medium rounded-xl transition-colors flex items-center gap-3
                      ${isDark ? 'text-gray-300 hover:bg-gray-800 hover:text-white' : 'text-gray-600 hover:bg-green-50 hover:text-green-700'}`}
                  >
                    <span style={{ fontSize: 16 }}>{item.icon}</span>
                    {item.label}
                  </button>
                ))}
              </div>

              {/* Akun tersimpan */}
              {savedAccounts.length > 0 && (
                <div className="border-t" style={{ borderColor: isDark ? '#1f2937' : '#f5f5f5' }}>
                  <p className={`px-4 pt-3 pb-1 text-xs font-semibold uppercase tracking-widest ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                    Akun Tersimpan
                  </p>
                  {savedAccounts.map((acc) => (
                    <button
                      key={acc.email}
                      onClick={() => handleSwitchAccount(acc)}
                      className={`w-full text-left px-3 py-2.5 text-sm font-medium rounded-xl mx-2 transition-colors flex items-center gap-3
                        ${isDark ? 'text-gray-300 hover:bg-gray-800' : 'text-gray-600 hover:bg-gray-50'}`}
                      style={{ width: 'calc(100% - 16px)' }}
                    >
                      <div className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0"
                        style={{ background: '#6366f1' }}>
                        {(acc.nama || acc.email || '?')[0].toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <p className="truncate text-xs font-semibold">{acc.nama || acc.email}</p>
                        <p className={`truncate text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{acc.email}</p>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Logout */}
              <div className="p-2 border-t" style={{ borderColor: isDark ? '#1f2937' : '#f5f5f5' }}>
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-3 py-2.5 text-sm font-bold text-red-500 hover:bg-red-50 rounded-xl transition-colors flex items-center gap-3"
                >
                  <span style={{ fontSize: 16 }}>🚪</span> Keluar
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}