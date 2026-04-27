import { NavLink } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'

const menu = [
  {
    to: '/input',
    label: 'Catat Transaksi',
    desc: 'Input chat baru',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
      </svg>
    ),
  },
  {
    to: '/dashboard',
    label: 'Dashboard',
    desc: 'Transaksi harian',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
        <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
      </svg>
    ),
  },
  {
    to: '/laporan',
    label: 'Laporan',
    desc: 'Keuangan bulanan',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
        <line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>
      </svg>
    ),
  },
]

export default function Sidebar() {
  const { theme } = useTheme()
  const isDark    = theme === 'dark'

  // Warna sidebar
  const sidebarBg = isDark
    ? 'linear-gradient(180deg, #0a1628 0%, #0d1f38 50%, #0a1e2e 100%)'
    : 'linear-gradient(180deg, #f0fff8 0%, #e8faf2 50%, #f0fdf9 100%)'

  const borderColor = isDark ? '#0f2d3d' : '#c6f0de'

  return (
    <aside
      className="hidden md:flex flex-col w-58 shrink-0 min-h-[calc(100vh-64px)] transition-all duration-300"
      style={{
        width: 220,
        background: sidebarBg,
        borderRight: `1px solid ${borderColor}`,
      }}
    >
      {/* Spacer atas */}
      <div className="px-4 pt-5 pb-2">
        <p
          className="text-xs font-black uppercase tracking-[0.15em] px-2"
          style={{ color: isDark ? '#1e4d6b' : '#86c9aa' }}
        >
          Navigasi
        </p>
      </div>

      {/* Menu items */}
      <nav className="px-3 flex flex-col gap-1">
        {menu.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className="group"
          >
            {({ isActive }) => (
              <div
                className="flex items-center gap-3 px-3 py-3 rounded-2xl transition-all duration-200"
                style={{
                  background: isActive
                    ? isDark
                      ? 'linear-gradient(135deg, rgba(52,211,153,0.15), rgba(16,185,129,0.08))'
                      : 'linear-gradient(135deg, rgba(22,163,74,0.12), rgba(74,222,128,0.06))'
                    : 'transparent',
                  boxShadow: isActive
                    ? isDark
                      ? 'inset 0 0 0 1px rgba(52,211,153,0.2)'
                      : 'inset 0 0 0 1px rgba(22,163,74,0.15)'
                    : 'none',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.background = isDark
                      ? 'rgba(52,211,153,0.06)'
                      : 'rgba(22,163,74,0.06)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) e.currentTarget.style.background = 'transparent'
                }}
              >
                {/* Icon dengan lingkaran */}
                <div
                  className="flex items-center justify-center w-9 h-9 rounded-xl shrink-0 transition-all duration-200"
                  style={{
                    background: isActive
                      ? isDark ? 'rgba(52,211,153,0.2)' : 'rgba(22,163,74,0.12)'
                      : isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)',
                    color: isActive
                      ? isDark ? '#34d399' : '#16a34a'
                      : isDark ? '#4b6070' : '#7aad90',
                  }}
                >
                  {item.icon}
                </div>

                {/* Label */}
                <div className="min-w-0">
                  <p
                    className="text-sm font-bold leading-tight truncate transition-colors"
                    style={{
                      color: isActive
                        ? isDark ? '#34d399' : '#15803d'
                        : isDark ? '#64748b' : '#5a7a68',
                    }}
                  >
                    {item.label}
                  </p>
                  <p
                    className="text-xs leading-tight mt-0.5 truncate transition-colors"
                    style={{
                      color: isActive
                        ? isDark ? '#6ee7b7' : '#4ade80'
                        : isDark ? '#2d4a5a' : '#a3c4b0',
                    }}
                  >
                    {item.desc}
                  </p>
                </div>

                {/* Indikator aktif */}
                {isActive && (
                  <div
                    className="ml-auto shrink-0 w-1.5 h-6 rounded-full"
                    style={{
                      background: isDark
                        ? 'linear-gradient(180deg,#34d399,#10b981)'
                        : 'linear-gradient(180deg,#16a34a,#4ade80)',
                    }}
                  />
                )}
              </div>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Spacer bawah + versi */}
      <div className="mt-auto px-5 py-5">
        <div
          className="rounded-2xl p-3"
          style={{
            background: isDark ? 'rgba(52,211,153,0.04)' : 'rgba(22,163,74,0.05)',
            border: `1px solid ${isDark ? 'rgba(52,211,153,0.08)' : 'rgba(22,163,74,0.10)'}`,
          }}
        >
          <p className="text-xs font-bold" style={{ color: isDark ? '#1e4d3a' : '#86c9aa' }}>
            ChatKasir
          </p>
          <p className="text-xs mt-0.5" style={{ color: isDark ? '#1a3a2e' : '#a8d8ba' }}>
            v1.0 · CC26-PSU065
          </p>
        </div>
      </div>
    </aside>
  )
}