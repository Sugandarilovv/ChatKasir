import { NavLink } from 'react-router-dom'
import { useState } from 'react'
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
  // TAMBAHAN BARU: Menu Tanya AI
  {
    to: '/tanya-ai',
    label: 'Tanya AI',
    desc: 'Asisten Bisnis',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        <path d="m10 7 2 4 4 2-4 2-2 4-2-4-4-2 4-2Z"></path>
      </svg>
    ),
  },
]

export default function Sidebar({ isMobileOpen, onClose }) {
  const { theme } = useTheme()
  const isDark    = theme === 'dark'
  const [isCollapsed, setIsCollapsed] = useState(false)

  const sidebarBg = isDark
    ? 'linear-gradient(180deg, #0a1628 0%, #0d1f38 50%, #0a1e2e 100%)'
    : 'linear-gradient(180deg, #f0fff8 0%, #e8faf2 50%, #f0fdf9 100%)'
  const borderColor = isDark ? '#0f2d3d' : '#c6f0de'

  return (
    <>
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm md:hidden transition-opacity"
          onClick={onClose}
        />
      )}

      <aside
        className={`
          fixed md:relative top-16 md:top-0 left-0 z-40 md:z-0
          flex flex-col shrink-0 transition-transform duration-300 ease-in-out
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
        style={{
          width: isMobileOpen ? 200 : (isCollapsed ? 88 : 220), 
          background: sidebarBg,
          borderRight: `1px solid ${borderColor}`,
          height: 'calc(100dvh - 64px)', 
        }}
      >
        <div className={`flex items-center pt-5 pb-2 ${isCollapsed && !isMobileOpen ? 'justify-center px-0' : 'justify-between px-4'}`}>
          {(!isCollapsed || isMobileOpen) && (
            <p
              className="text-xs font-black uppercase tracking-[0.15em] px-2 whitespace-nowrap"
              style={{ color: isDark ? '#1e4d6b' : '#86c9aa' }}
            >
              Menu
            </p>
          )}
          
          <button 
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden md:block p-1.5 rounded-lg transition-colors hover:bg-black/5 dark:hover:bg-white/10 text-green-700 dark:text-green-400 shrink-0"
            title="Toggle Sidebar"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
        </div>

        <nav className="px-3 flex flex-col gap-1 mt-2">
          {menu.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => { if (isMobileOpen) onClose() }} 
              className="group"
              title={isCollapsed && !isMobileOpen ? item.label : ""} 
            >
              {({ isActive }) => (
                <div
                  className={`flex items-center py-3 rounded-2xl transition-all duration-200 ${isCollapsed && !isMobileOpen ? 'justify-center px-0' : 'px-3 gap-3'}`}
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
                >
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

                  {(!isCollapsed || isMobileOpen) && (
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
                  )}

                  {(!isCollapsed || isMobileOpen) && isActive && (
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

        <div className={`mt-auto py-5 ${isCollapsed && !isMobileOpen ? 'px-3' : 'px-5'}`}>
          <div
            className={`rounded-2xl flex items-center justify-center transition-all ${isCollapsed && !isMobileOpen ? 'p-2' : 'p-3 flex-col items-start'}`}
            style={{
              background: isDark ? 'rgba(52,211,153,0.04)' : 'rgba(22,163,74,0.05)',
              border: `1px solid ${isDark ? 'rgba(52,211,153,0.08)' : 'rgba(22,163,74,0.10)'}`,
            }}
          >
            {isCollapsed && !isMobileOpen ? (
              <p className="text-xs font-black" style={{ color: isDark ? '#d1fae5' : '#065f46' }}>CK</p>
            ) : (
              <>
                <p className="text-xs font-bold" style={{ color: isDark ? '#d1fae5' : '#065f46' }}>
                  ChatKasir
                </p>
                <p className="text-xs mt-0.5 whitespace-nowrap" style={{ color: isDark ? '#6ee7b7' : '#059669' }}>
                  v1.0
                </p>
              </>
            )}
          </div>
        </div>
      </aside>
    </>
  )
}