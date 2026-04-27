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

  const [items, setItems]       = useState([])
  const [loading, setLoading]   = useState(false)
  const [teksAsli, setTeksAsli] = useState('')

  useEffect(() => {
    const raw  = sessionStorage.getItem('hasil_ai')
    const teks = sessionStorage.getItem('teks_chat')
    if (!raw) { navigate('/input'); return }
    try {
      const parsed = JSON.parse(raw)
      const arr = Array.isArray(parsed) ? parsed : (parsed.results || [])
      setItems(arr.map((item, i) => ({ ...item, id: i })))
      setTeksAsli(teks || '')
    } catch { navigate('/input') }
  }, [navigate])

  function handleEdit(id, field, value) {
    setItems((prev) => prev.map((item) => item.id === id ? { ...item, [field]: value } : item))
  }

  function handleHapus(id) {
    setItems((prev) => prev.filter((item) => item.id !== id))
    // Memperbaiki fungsi notifikasi hapus agar seragam
    showToast('Item dihapus', 'success')
  }

  function handleTambah() {
    setItems((prev) => [...prev, { id: Date.now(), nama_produk: '', jumlah: 1, harga: 0 }])
  }

  const total = items.reduce((s, i) => s + Number(i.jumlah) * Number(i.harga), 0)

  async function handleSimpan() {
    const valid = items.filter((i) => i.nama_produk?.trim() && Number(i.jumlah) > 0)
    if (!valid.length) { 
      // Memperbaiki notifikasi error agar seragam
      showToast('Tidak ada item valid.', 'error')
      return 
    }
    
    setLoading(true)
    try {
      await saveTransactions(valid.map(({ nama_produk, jumlah, harga }) => ({ nama_produk, jumlah: Number(jumlah), harga: Number(harga) })))
      sessionStorage.removeItem('hasil_ai')
      sessionStorage.removeItem('teks_chat')
      
      // Memperbaiki notifikasi sukses agar seragam dengan fungsi showToast bawaan aplikasi Anda
      showToast(`${valid.length} transaksi berhasil disimpan!`, 'success')
      
      navigate('/dashboard')
    } catch { 
      showToast('Gagal menyimpan. Coba lagi.', 'error') 
    }
    finally { setLoading(false) }
  }

  // Variabel Warna Tema
  const bg      = isDark ? '#111827' : '#ffffff'
  const cardBg  = isDark ? '#1f2937' : '#f8fafc'
  const bdr     = isDark ? '#374151' : '#e2e8f0'
  const txt     = isDark ? '#f8fafc' : '#1f2937'
  const txtMut  = isDark ? '#94a3b8' : '#9ca3af'
  const inputBg = isDark ? '#374151' : '#ffffff'
  const inputBdr= isDark ? '#4b5563' : '#e2e8f0'

  // KUNCI PRESISI: Variabel ini digunakan di Header dan di Row agar jarak kolom 100% sama sejajar
  const gridCols = '1fr 80px 130px 110px 36px'

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto animate-fade-up">

        {/* Header */}
        <div className="flex items-start justify-between mb-6 flex-wrap gap-3">
          <div>
            <h2 className="text-2xl font-extrabold" style={{ color: txt }}>Konfirmasi Hasil AI</h2>
            <p className="text-sm mt-1" style={{ color: txtMut }}>Periksa, edit jika perlu, lalu simpan.</p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold" 
            style={{ background: isDark ? '#14532d' : '#dcfce7', color: isDark ? '#4ade80' : '#15803d' }}>
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
            AI selesai memproses
          </div>
        </div>

        {/* Teks asli */}
        {teksAsli && (
          <div className="mb-5 rounded-2xl p-4 animate-fade-up delay-1" 
            style={{ background: cardBg, border: `1px solid ${bdr}` }}>
            <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: txtMut }}>Teks chat asli</p>
            <p className="text-sm italic" style={{ color: txt }}>"{teksAsli}"</p>
          </div>
        )}

        {/* Area Tabel */}
        <div className="rounded-2xl overflow-hidden animate-fade-up delay-2" 
          style={{ background: bg, border: `1px solid ${bdr}`, boxShadow: `0 2px 16px rgba(0,0,0,${isDark ? '0.3' : '0.05'})` }}>
          
          {/* HEADER TABEL */}
          <div className="grid text-xs font-semibold uppercase tracking-widest px-5 py-3 gap-3"
            style={{ gridTemplateColumns: gridCols, background: cardBg, borderBottom: `1px solid ${bdr}`, color: txtMut }}>
            <span>Nama Produk</span>
            <span className="text-center">Jumlah</span>
            <span className="text-right">Harga Satuan</span>
            <span className="text-right">Subtotal</span>
            <span />
          </div>

          <div className="divide-y" style={{ divideColor: bdr }}>
            {items.length === 0 && (
              <div className="py-12 text-center text-sm font-medium" style={{ color: txtMut }}>
                Tidak ada item. Tambah manual atau kembali ke input.
              </div>
            )}
            
            {items.map((item, idx) => (
              // BARIS ISI TABEL
              <div key={item.id}
                className="grid items-center px-5 py-3 gap-3 group transition-colors"
                style={{ gridTemplateColumns: gridCols, animationDelay: `${idx * 0.04}s` }}>
                
                <input
                  className="w-full px-3 py-2 rounded-lg border text-sm font-semibold outline-none focus:ring-2 focus:ring-green-400 transition-all"
                  style={{ 
                    background: item.nama_produk ? inputBg : (isDark ? '#451a1a' : '#fff9f9'), 
                    borderColor: item.nama_produk ? inputBdr : '#fca5a5',
                    color: txt 
                  }}
                  value={item.nama_produk || ''}
                  onChange={(e) => handleEdit(item.id, 'nama_produk', e.target.value)}
                  placeholder="Ketik produk..." />
                  
                <input type="number" min={1}
                  className="w-full px-2 py-2 rounded-lg border font-bold text-sm text-center outline-none focus:ring-2 focus:ring-green-400 transition-all"
                  style={{ background: inputBg, borderColor: inputBdr, color: txt }}
                  value={item.jumlah || 1}
                  onChange={(e) => handleEdit(item.id, 'jumlah', e.target.value)} />
                  
                <input type="number" min={0}
                  className="w-full px-3 py-2 rounded-lg border font-semibold text-sm text-right outline-none focus:ring-2 focus:ring-green-400 transition-all"
                  style={{ background: inputBg, borderColor: inputBdr, color: txt }}
                  value={item.harga || 0}
                  onChange={(e) => handleEdit(item.id, 'harga', e.target.value)} />
                
                <span className="text-right text-sm font-extrabold" style={{ color: isDark ? '#4ade80' : '#16a34a' }}>
                  {formatRupiah(Number(item.jumlah) * Number(item.harga))}
                </span>
                
                <button onClick={() => handleHapus(item.id)}
                  className="w-8 h-8 rounded-full flex items-center justify-center text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all opacity-0 group-hover:opacity-100">
                  ✕
                </button>
              </div>
            ))}
          </div>

          {/* Footer Total */}
          {items.length > 0 && (
            <div className="flex items-center justify-between px-5 py-4 border-t" style={{ borderColor: bdr, background: cardBg }}>
              <button onClick={handleTambah}
                className="text-sm font-bold transition-colors flex items-center gap-1 hover:opacity-80"
                style={{ color: isDark ? '#4ade80' : '#16a34a' }}>
                + Tambah Item
              </button>
              <div className="flex items-center gap-3">
                <span className="text-sm font-semibold" style={{ color: txtMut }}>Total Pembayaran</span>
                <span className="text-xl font-black" style={{ color: isDark ? '#4ade80' : '#15803d' }}>
                  {formatRupiah(total)}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Tombol Aksi Bawah */}
        <div className="flex gap-3 mt-6 justify-between items-center">
          <button onClick={() => navigate('/input')}
            className="px-5 py-3 rounded-xl text-sm font-bold transition-all hover:-translate-x-1"
            style={{ background: isDark ? '#374151' : '#f1f5f9', color: isDark ? '#d1d5db' : '#475569' }}>
            ← Kembali
          </button>
          
          <button onClick={handleSimpan} disabled={loading || !items.length}
            className="flex items-center gap-2 px-8 py-3.5 rounded-xl text-sm font-black text-white transition-all active:scale-95 disabled:opacity-50"
            style={{ 
              background: loading || !items.length ? (isDark ? '#374151' : '#9ca3af') : 'linear-gradient(135deg,#16a34a,#15803d)',
              boxShadow: loading || !items.length ? 'none' : '0 4px 16px rgba(22,163,74,0.3)'
            }}>
            {loading
              ? <><svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/></svg>Menyimpan...</>
              : '✓ Simpan Transaksi'}
          </button>
        </div>
      </div>
    </MainLayout>
  )
}