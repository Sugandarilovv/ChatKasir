import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { predictFromChat } from '../services/aiService'
import MainLayout from '../components/layout/MainLayout'
import { useTheme } from '../context/ThemeContext'
import { showToast } from '../components/ui/Toast'

const CONTOH_LIST = [
  '[29/5, 07.14] +62 811-2222-3333: order paket ayam bakar madu 10 pack\n[29/5, 07.21] Warung Sejahtera: siap harganya 35k',
  '[28/05, 05:26] Budi: order paket ayam bakar madu 10 pack sama es kopi susu gula aren 5 cup\n[28/05, 06:01] Warung Sejahtera: siap paket ayam bakar madu harganya 35k dan es kopi susu gula aren harganya 18k jadi total tagihan katering semuanya 440k',
]

const TIPS = [
  { icon: '💰', text: 'Harga bisa "15rb", "15.000", atau "15k"' },
  { icon: '🔢', text: 'Jumlah bisa "3 porsi", "tiga", atau angka "3"' },
  { icon: '📦', text: 'Satu pesan bisa berisi banyak item sekaligus' },
]

export default function InputChat() {
  const { theme }   = useTheme()
  const isDark      = theme === 'dark'
  const [teks, setTeks]           = useState('')
  const [loading, setLoading]     = useState(false)
  const [pasting, setPasting]     = useState(false)
  const [contohIdx, setContohIdx] = useState(0)
  const textareaRef = useRef(null)
  const navigate    = useNavigate()

  const isReady   = teks.trim().length >= 5
  const charCount = teks.length

  const bg      = isDark ? '#111827' : '#ffffff'
  const barBg   = isDark ? '#0f172a' : '#f0fdf4'
  const barBdr  = isDark ? '#1e293b' : '#d1fae5'
  const txt     = isDark ? '#f1f5f9' : '#1f2937'
  const txtHint = isDark ? '#64748b' : '#6b7280'  
  const cardBdr = isReady ? '#4ade80' : isDark ? '#1e293b' : '#d1fae5'

  // --- LOGIKA SIMPAN OTOMATIS: Muat Draft ---
  useEffect(() => {
    const autoSave = JSON.parse(localStorage.getItem('ck_autosave') ?? 'true')
    if (autoSave) {
      const draft = localStorage.getItem('ck_draft_input')
      if (draft) setTeks(draft)
    }
  }, [])

  // --- LOGIKA SIMPAN OTOMATIS: Simpan ke Draft saat Mengetik ---
  useEffect(() => {
    const autoSave = JSON.parse(localStorage.getItem('ck_autosave') ?? 'true')
    if (autoSave && teks.trim().length > 0) {
      localStorage.setItem('ck_draft_input', teks)
    } else if (!autoSave || teks.trim().length === 0) {
      localStorage.removeItem('ck_draft_input')
    }
  }, [teks])

  async function handlePaste() {
    try {
      setPasting(true)
      const text = await navigator.clipboard.readText()
      if (!text.trim()) { showToast('Clipboard kosong.', 'warning'); return }
      setTeks((prev) => prev + (prev ? '\n' : '') + text)
      showToast('Teks berhasil ditempel!', 'success')
      textareaRef.current?.focus()
    } catch {
      showToast('Izin clipboard ditolak. Gunakan Ctrl+V.', 'error')
    } finally { setPasting(false) }
  }

  async function handleProses() {
    if (!teks.trim()) { showToast('Teks chat tidak boleh kosong.', 'error'); return }
    if (teks.trim().length < 5) { showToast('Teks terlalu pendek.', 'error'); return }
    setLoading(true)
    try {
      const result = await predictFromChat(teks.trim())
      sessionStorage.setItem('hasil_ai', JSON.stringify(result))
      sessionStorage.setItem('teks_chat', teks.trim())
      localStorage.removeItem('ck_draft_input') // Bersihkan draft jika sukses pindah ke konfirmasi
      navigate('/konfirmasi')
    } catch (err) {
      showToast(err.response?.data?.detail || 'Gagal memproses. Coba lagi.', 'error')
    } finally { setLoading(false) }
  }

  function pakaiContoh() {
    setTeks(CONTOH_LIST[contohIdx])
    setContohIdx((p) => (p + 1) % CONTOH_LIST.length)
  }

  function hapusSemuaTeks() {
    setTeks('')
    localStorage.removeItem('ck_draft_input')
  }

  return (
    <MainLayout>
      <div className="max-w-2xl mx-auto animate-fade-up">

        <div className="mb-7">
          <h2 className="text-2xl font-extrabold mb-1" style={{ color: txt }}>
            Catat Transaksi
          </h2>
          <p className="text-sm" style={{ color: txtHint }}>
            Salin chat pesanan dari WhatsApp, AI akan membaca dan mencatat otomatis.
          </p>
        </div>

        <div className="rounded-2xl overflow-hidden mb-5 transition-all duration-200"
          style={{
            background: bg, border: `1.5px solid ${cardBdr}`,
            boxShadow: isReady ? '0 0 0 4px rgba(74,222,128,0.12), 0 2px 16px rgba(0,0,0,0.08)' : `0 2px 16px rgba(0,0,0,${isDark ? '0.2' : '0.06'})`,
          }}>

          <div className="flex items-center justify-between px-4 py-2.5 border-b flex-wrap gap-2"
            style={{ background: barBg, borderColor: barBdr }}>
            
            <div className="flex items-center gap-1.5">
              {['#fca5a5', '#fde68a', '#86efac'].map((c, i) => (
                <div key={i} className="w-3 h-3 rounded-full" style={{ background: c }} />
              ))}
              <span className="ml-2 text-xs font-mono hidden sm:block" style={{ color: txtHint }}>
                chat-input.txt
              </span>
            </div>
            
            <div className="flex items-center gap-3">
              <span style={{
                fontSize: 11, fontWeight: 600, transition: 'color 0.2s', letterSpacing: '0.02em',
                color: charCount > 0 ? (isDark ? '#4ade80' : '#16a34a') : (isDark ? '#4b5563' : '#6b7280'),
              }}>
                {charCount === 0 ? '0 karakter' : `${charCount} karakter`}
              </span>

              <button onClick={handlePaste} disabled={pasting || loading}
                className="flex items-center gap-1.5 text-xs font-bold px-2.5 py-1.5 rounded-lg transition-all hover:scale-105 active:scale-95"
                style={{ background: isDark ? '#374151' : '#f1f5f9', color: isDark ? '#d1d5db' : '#475569', cursor: pasting ? 'wait' : 'pointer', opacity: pasting ? 0.7 : 1 }}>
                {pasting ? (
                  <svg className="animate-spin" width="13" height="13" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/></svg>
                ) : (
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="2" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
                )}
                Tempel
              </button>

              <button onClick={pakaiContoh}
                className="text-xs font-bold px-2.5 py-1.5 rounded-lg transition-all hover:scale-105 active:scale-95"
                style={{ background: isDark ? '#14532d' : '#dcfce7', color: isDark ? '#4ade80' : '#166534', border: `1px solid ${isDark ? '#2d6a45' : '#86efac'}` }}>
                Coba contoh
              </button>
            </div>
          </div>

          <textarea
            ref={textareaRef}
            className="w-full px-5 py-4 text-sm resize-none outline-none custom-scrollbar"
            style={{ height: 220, background: bg, color: txt, lineHeight: '1.75', caretColor: '#16a34a' }}
            placeholder="Tempel teks chat di sini..."
            value={teks}
            onChange={(e) => setTeks(e.target.value)}
            disabled={loading}
          />

          <div className="flex items-center justify-between px-4 py-3 border-t" style={{ background: barBg, borderColor: barBdr }}>
            <button onClick={hapusSemuaTeks} disabled={!teks || loading}
              style={{
                fontSize: 12, fontWeight: 600, background: 'transparent', border: 'none', display: 'flex', alignItems: 'center', gap: 5, transition: 'color 0.2s',
                color: !teks || loading ? (isDark ? '#374151' : '#9ca3af') : (isDark ? '#f87171' : '#dc2626'),
                cursor: !teks ? 'not-allowed' : 'pointer', opacity: !teks ? 0.45 : 1,
              }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polyline points="3,6 5,6 21,6"/><path d="M19,6v14a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6m3,0V4a2,2,0,0,1,2-2h4a2,2,0,0,1,2,2v2"/></svg>
              Hapus teks
            </button>

            <button onClick={handleProses} disabled={loading || !isReady}
              style={{
                display: 'flex', alignItems: 'center', gap: 8, padding: '10px 24px', borderRadius: 14, fontSize: 14, fontWeight: 800, border: 'none', transition: 'all 0.2s',
                color: '#ffffff', background: isReady && !loading ? 'linear-gradient(135deg,#16a34a,#15803d)' : isDark ? '#1e293b' : '#d1fae5',
                cursor: loading || !isReady ? 'not-allowed' : 'pointer', opacity: loading || !isReady ? 0.55 : 1,
                boxShadow: isReady && !loading ? '0 4px 14px rgba(22,163,74,0.35)' : 'none',
              }}
              onMouseEnter={(e) => { if (isReady && !loading) e.currentTarget.style.transform = 'scale(1.03)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)' }}>
              {loading ? (
                <><svg className="animate-spin" width="15" height="15" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/></svg>Membaca...</>
              ) : (
                <><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><polygon points="13,2 3,14 12,14 11,22 21,10 12,10 13,2"/></svg>Proses Sekarang</>
              )}
            </button>
          </div>
        </div>

        <div className="rounded-2xl p-5" style={{ background: isDark ? '#0c1f14' : '#f0fdf4', border: `1px solid ${isDark ? '#14532d' : '#bbf7d0'}` }}>
          <p className="text-xs font-black uppercase tracking-widest mb-3" style={{ color: isDark ? '#4ade80' : '#15803d' }}>
            Tips Penulisan
          </p>
          <div className="space-y-2.5">
            {TIPS.map((tip, i) => (
              <div key={i} className="flex items-start gap-2.5">
                <span style={{ fontSize: 14, marginTop: 1 }}>{tip.icon}</span>
                <span className="text-xs leading-relaxed" style={{ color: isDark ? '#86efac' : '#166534' }}>{tip.text}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </MainLayout>
  )
}