import { createContext, useContext, useState, useCallback, useRef } from 'react'

const ToastCtx = createContext()

const ICONS = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' }
const COLORS = {
  success: { bg: '#f0fdf4', border: '#86efac', text: '#15803d' },
  error:   { bg: '#fff1f2', border: '#fca5a5', text: '#b91c1c' },
  info:    { bg: '#eff6ff', border: '#93c5fd', text: '#1d4ed8' },
  warning: { bg: '#fffbeb', border: '#fcd34d', text: '#92400e' },
}

let _show = null
export function showToast(msg, type = 'success') { _show?.(msg, type) }

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const timers = useRef({})

  const show = useCallback((msg, type = 'success') => {
    const id = Date.now()
    setToasts((prev) => [...prev.slice(-2), { id, msg, type, out: false }])
    timers.current[id] = setTimeout(() => {
      setToasts((prev) => prev.map((t) => t.id === id ? { ...t, out: true } : t))
      setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 280)
    }, 1800)
  }, [])

  _show = show

  return (
    <ToastCtx.Provider value={show}>
      {children}
      {/* Portal ke tengah atas — z-index 9999 agar tidak tertutup apapun */}
      <div style={{ position: 'fixed', top: 16, left: '50%', transform: 'translateX(-50%)', zIndex: 9999, pointerEvents: 'none', display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'center' }}>
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
                padding: '10px 18px',
                fontSize: 13,
                fontWeight: 600,
                whiteSpace: 'nowrap',
                boxShadow: '0 4px 24px rgba(0,0,0,0.10)',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                pointerEvents: 'auto',
              }}>
              <span style={{ fontSize: 15 }}>{ICONS[t.type]}</span>
              {t.msg}
            </div>
          )
        })}
      </div>
    </ToastCtx.Provider>
  )
}

export function useToast() { return useContext(ToastCtx) }