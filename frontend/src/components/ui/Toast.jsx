import { createContext, useContext, useState, useCallback, useRef } from 'react'

const ToastCtx = createContext()

const ICONS = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' }
const COLORS = {
  success: { bg: '#f0fdf4', border: '#86efac', text: '#15803d' },
  error:   { bg: '#fff1f2', border: '#fca5a5', text: '#b91c1c' },
  info:    { bg: '#eff6ff', border: '#93c5fd', text: '#1d4ed8' },
  warning: { bg: '#fffbeb', border: '#fcd34d', text: '#92400e' },
}

// PINDAHKAN LOGIKA INI KE DALAM PROVIDER AGAR VITE TIDAK ERROR
let _showGlobal = null
export const showToast = (msg, type = 'success') => {
  if (_showGlobal) _showGlobal(msg, type)
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const timers = useRef({})

  const show = useCallback((msg, type = 'success') => {
    const id = Date.now()
    setToasts((prev) => [...prev.slice(-2), { id, msg, type, out: false }])
    timers.current[id] = setTimeout(() => {
      setToasts((prev) => prev.map((t) => t.id === id ? { ...t, out: true } : t))
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id))
      }, 300)
    }, 3500) // Tepat 5 detik!
  }, [])

  _showGlobal = show // Simpan fungsi ke variabel luar

  return (
    <ToastCtx.Provider value={show}>
      {children}
      {/* PERBAIKAN POSISI TENAH: Pastikan width & left diatur seperti ini */}
      <div style={{ 
        position: 'fixed', 
        top: 70, 
        left: '65%', 
        transform: 'translateX(-60%)', 
        zIndex: 9999, 
        pointerEvents: 'none', 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 8, 
        alignItems: 'center',
        width: '10%', 
        maxWidth: '450px' // Agar tidak terlalu lebar di tablet/laptop
      }}>
        {toasts.map((t) => {
          const c = COLORS[t.type] || COLORS.info
          return (
            <div key={t.id}
              className={t.out ? 'toast-out' : 'toast-in'}
              style={{
                background: c.bg,
                border: `1px solid ${c.border}`,
                color: c.text,
                borderRadius: 14,
                padding: '4px 9px',
                fontSize: 8,
                fontWeight: 600,
                whiteSpace: 'nowrap',
                boxShadow: '0 4px 24px rgba(0,0,0,0.10)',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                pointerEvents: 'auto',
                width: 'fit-content' // Supaya box tetap pas dengan tulisan
              }}>
              <span style={{ fontSize: 14 }}>{ICONS[t.type]}</span>
              {t.msg}
            </div>
          )
        })}
      </div>
    </ToastCtx.Provider>
  )
}

export function useToast() { return useContext(ToastCtx) }