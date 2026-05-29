import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { saveTransactions } from '../services/transactionService'
import MainLayout from '../components/layout/MainLayout'
import { formatRupiah } from '../utils/formatRupiah'
import { useTheme } from '../context/ThemeContext'
import { showToast } from '../components/ui/Toast'

export default function Konfirmasi() {
  const navigate = useNavigate()
  const { theme } = useTheme()
  const isDark    = theme === 'dark'

  const [items,        setItems]       = useState([])
  const [loading,      setLoading]     = useState(false)
  const [teksAsli,     setTeksAsli]    = useState('')
  const [extractionId, setExtractionId]= useState(null)

  useEffect(() => {
    const raw  = sessionStorage.getItem('hasil_ai')
    const teks = sessionStorage.getItem('teks_chat')
    if (!raw) { navigate('/input'); return }
    try {
      const parsed = JSON.parse(raw)
      const predictions = parsed.predictions || parsed.results || []
      setExtractionId(parsed.extraction_id || null)
      setItems(predictions.map((item, i) => ({
        id:           i,
        nama_produk:  item.product_name  || '',
        jumlah:       item.quantity      ?? 1,
        harga:        item.price_satuan  ?? 0,
        total:        item.total || item.subtotal || 0,
        confidence:   (item.confidence || 'HIGH').toUpperCase(),
        is_manual:    false,
      })))
      setTeksAsli(teks || '')
    } catch { navigate('/input') }
  }, [navigate])

  function handleEdit(id, field, value) {
    setItems((prev) => prev.map((item) =>
      item.id === id
        ? { ...item, [field]: value, total: field === 'jumlah' || field === 'harga'
            ? Number(field === 'jumlah' ? value : item.jumlah) * Number(field === 'harga' ? value : item.harga)
            : item.total }
        : item
    ))
  }

  function handleHapus(id) {
    setItems((prev) => prev.filter((item) => item.id !== id))
    showToast('Item dihapus', 'success')
  }

  function handleTambah() {
    setItems((prev) => [...prev, {
      id: Date.now(), nama_produk: '', jumlah: 1, harga: 0, total: 0,
      confidence: 'HIGH', is_manual: true,
    }])
  }

  const total = items.reduce((s, i) => s + Number(i.jumlah) * Number(i.harga), 0)

  async function handleSimpan() {
    const valid = items.filter((i) => i.nama_produk?.trim() && Number(i.jumlah) > 0)
    if (!valid.length) { showToast('Tidak ada item valid.', 'error'); return }
    if (!extractionId) { showToast('Session tidak valid, silakan ulang dari input.', 'error'); return }

    setLoading(true)
    try {
      const products = valid.map(({ nama_produk, jumlah, harga, confidence, is_manual }) => ({
        product_name:  nama_produk,
        quantity:      Number(jumlah),
        price_satuan:  Number(harga),
        total:         Number(jumlah) * Number(harga),
        confidence:    confidence || 'HIGH',
        is_manual:     is_manual  || false,
      }))

      await saveTransactions(extractionId, products)
      sessionStorage.removeItem('hasil_ai')
      sessionStorage.removeItem('teks_chat')

      showToast(`${valid.length} transaksi berhasil disimpan!`, 'success')
      navigate('/dashboard')
    } catch (err) {
      showToast(err.response?.data?.error || 'Gagal menyimpan. Coba lagi.', 'error')
    } finally { setLoading(false) }
  }

  const bg      = isDark ? '#111827' : '#ffffff'
  const cardBg  = isDark ? '#1f2937' : '#ffffff'
  const bdr     = isDark ? '#374151' : '#e2e8f0'
  const txt     = isDark ? '#f8fafc' : '#111827'
  const txtMut  = isDark ? '#94a3b8' : '#9ca3af'
  
  // PERBAIKAN: Ubah warna kotak input di mode terang agar tidak menyatu dengan background
  const inputBg = isDark ? '#374151' : '#f1f5f9'
  const inputBdr= isDark ? '#4b5563' : '#cbd5e1'
  
  const gridCols = '30% 12% 18% 18% 15% 7%'

  return (
    <MainLayout>
      <div className="w-full max-w-4xl mx-auto animate-fade-up">

        <div className="flex flex-row items-center justify-between mb-8 lg:mb-6 gap-2 w-full">
          <div className="min-w-0 flex-1">
            <h2 className="text-lg sm:text-3xl font-extrabold truncate" style={{ color: txt, letterSpacing: '-0.5px' }}>
              Konfirmasi Hasil AI
            </h2>
            <p className="text-[10px] sm:text-base mt-0.5 font-medium truncate" style={{ color: txtMut }}>
              Periksa, edit jika perlu, lalu simpan.
            </p>
          </div>
          <div className="inline-flex shrink-0 items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-full text-[9px] sm:text-sm font-bold shadow-sm"
            style={{ background: isDark ? '#14532d' : '#dcfce7', color: isDark ? '#4ade80' : '#15803d' }}>
            <span className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-green-500 animate-pulse" />
            <span>AI selesai memproses</span>
          </div>
        </div>

        {teksAsli && (
          <div className="mb-11 lg:mb-8 rounded-xl sm:rounded-2xl p-4 sm:p-5 animate-fade-up delay-1 shadow-sm"
            style={{ background: cardBg, border: `1px solid ${bdr}` }}>
            <p className="text-[10px] sm:text-xs font-bold uppercase tracking-widest mb-1.5 sm:mb-2" style={{ color: txtMut }}>
              TEKS CHAT ASLI
            </p>
            <p className="text-xs sm:text-base italic font-medium whitespace-pre-wrap leading-relaxed" style={{ color: txt }}>
              {teksAsli}
            </p>
          </div>
        )}

        <div className="rounded-xl sm:rounded-3xl overflow-hidden animate-fade-up delay-2 w-full shadow-sm"
          style={{ background: bg, border: `1px solid ${bdr}` }}>

          {/* Header tabel */}
          <div className="grid text-[8px] sm:text-xs font-bold uppercase tracking-widest px-2 sm:px-6 py-2.5 sm:py-4 gap-1 w-full"
            style={{ gridTemplateColumns: gridCols, background: isDark ? '#1f2937' : '#f8fafc', borderBottom: `1px solid ${bdr}`, color: txtMut }}>
            {/* PERBAIKAN: Penambahan sm:pl-4 untuk merapikan judul dengan kotak input */}
            <span className="truncate sm:pl-4">Nama Produk</span>
            <span className="text-center truncate">JUMLAH</span>
            <span className="text-center sm:text-left truncate sm:pl-4">Harga</span>
            <span className="text-right pr-1 sm:pr-2 truncate">Subtotal</span>
            <span className="text-center truncate">Akurasi</span>
            <span />
          </div>

          <div className="divide-y" style={{ divideColor: bdr }}>
            {items.length === 0 && (
              <div className="py-12 text-center text-xs sm:text-sm font-medium" style={{ color: txtMut }}>
                Tidak ada item. Tambah manual atau kembali ke input.
              </div>
            )}
            {items.map((item, idx) => (
              <div key={item.id}
                className="grid items-center px-2 sm:px-6 py-2 sm:py-4 gap-1 group transition-colors w-full"
                style={{ gridTemplateColumns: gridCols, animationDelay: `${idx * 0.04}s` }}>

                <input
                  className="w-full min-w-0 px-1.5 sm:px-4 py-1.5 sm:py-2.5 rounded-md sm:rounded-xl border text-[9px] sm:text-sm font-bold outline-none focus:ring-2 focus:ring-green-400 transition-all truncate"
                  style={{ background: item.nama_produk ? inputBg : (isDark ? '#451a1a' : '#fff9f9'), borderColor: item.nama_produk ? inputBdr : '#fca5a5', color: txt }}
                  value={item.nama_produk || ''}
                  onChange={(e) => handleEdit(item.id, 'nama_produk', e.target.value)}
                  placeholder="Produk..." />

                <input type="number" min={1}
                  className="w-full min-w-0 px-0.5 sm:px-2 py-1.5 sm:py-2.5 rounded-md sm:rounded-xl border font-bold text-[9px] sm:text-sm text-center outline-none focus:ring-2 focus:ring-green-400 transition-all"
                  style={{ background: inputBg, borderColor: inputBdr, color: txt }}
                  value={item.jumlah || 1}
                  onChange={(e) => handleEdit(item.id, 'jumlah', e.target.value)} />

                <input type="number" min={0}
                  className="w-full min-w-0 px-1.5 sm:px-4 py-1.5 sm:py-2.5 rounded-md sm:rounded-xl border font-bold text-[9px] sm:text-sm text-center sm:text-left outline-none focus:ring-2 focus:ring-green-400 transition-all"
                  style={{ background: inputBg, borderColor: inputBdr, color: txt }}
                  value={item.harga || 0}
                  onChange={(e) => handleEdit(item.id, 'harga', e.target.value)} />

                <span className="text-right text-[9px] sm:text-base font-extrabold pr-1 sm:pr-2 truncate" style={{ color: isDark ? '#4ade80' : '#16a34a' }}>
                  {formatRupiah(Number(item.jumlah) * Number(item.harga))}
                </span>

                <div className="flex items-center justify-center">
                  <span className={`px-1.5 sm:px-2.5 py-0.5 sm:py-1 rounded text-[8px] sm:text-[10px] font-extrabold uppercase tracking-wide
                    ${item.confidence === 'HIGH' ? (isDark ? 'bg-green-900/40 text-green-400' : 'bg-green-100 text-green-700') :
                      item.confidence === 'MEDIUM' ? (isDark ? 'bg-orange-900/40 text-orange-400' : 'bg-orange-100 text-orange-700') :
                      (isDark ? 'bg-red-900/40 text-red-400' : 'bg-red-100 text-red-700')}`}
                  >
                    {item.confidence || 'HIGH'}
                  </span>
                </div>

                <button onClick={() => handleHapus(item.id)}
                  className="w-5 h-5 sm:w-8 sm:h-8 rounded-full flex items-center justify-center text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all opacity-100 md:opacity-0 md:group-hover:opacity-100 mx-auto text-[10px] sm:text-base">
                  ✕
                </button>
              </div>
            ))}
          </div>

          {items.length > 0 && (
            <div className="flex flex-row items-center justify-between px-3 sm:px-6 py-3 sm:py-5 border-t gap-2"
              style={{ borderColor: bdr, background: isDark ? '#1f2937' : '#f8fafc' }}>
              <button onClick={handleTambah}
                className="text-[10px] sm:text-sm font-extrabold transition-colors flex items-center gap-1 hover:opacity-80 shrink-0"
                style={{ color: isDark ? '#4ade80' : '#16a34a' }}>
                + Tambah Item
              </button>
              <div className="flex items-center gap-1.5 sm:gap-4 shrink-0">
                <span className="text-[9px] sm:text-sm font-bold" style={{ color: txtMut }}>Total</span>
                <span className="text-sm sm:text-2xl font-black" style={{ color: isDark ? '#4ade80' : '#15803d' }}>
                  {formatRupiah(total)}
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="flex flex-row justify-between items-center mt-5 sm:mt-8 gap-3">
          <button onClick={() => navigate('/input')}
            className="px-3 sm:px-5 py-2 sm:py-3 rounded-lg sm:rounded-xl text-xs sm:text-base font-bold transition-all hover:-translate-x-1"
            style={{ background: isDark ? '#374151' : '#e2e8f0', color: isDark ? '#d1d5db' : '#475569' }}>
            ← Kembali
          </button>

          <button onClick={handleSimpan} disabled={loading || !items.length}
            className="flex items-center justify-center gap-1.5 sm:gap-2 px-5 sm:px-8 py-2 sm:py-3.5 rounded-lg sm:rounded-2xl text-xs sm:text-base font-extrabold text-white transition-all active:scale-95 disabled:opacity-50"
            style={{
              background: loading || !items.length ? (isDark ? '#374151' : '#9ca3af') : '#16a34a',
              boxShadow:  loading || !items.length ? 'none' : '0 4px 14px rgba(22,163,74,0.4)',
            }}>
            {loading
              ? <><svg className="animate-spin h-3 w-3 sm:h-4 sm:w-4" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/></svg>Menyimpan...</>
              : '✓ Simpan Transaksi'}
          </button>
        </div>
      </div>
    </MainLayout>
  )
}