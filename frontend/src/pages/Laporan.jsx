import { useState, useEffect } from 'react'
import MainLayout from '../components/layout/MainLayout'
import SummaryCard from '../components/ui/SummaryCard'
import RevenueBarChart from '../components/charts/RevenueBarChart'
import EmptyState from '../components/ui/EmptyState'
import { useTheme } from '../context/ThemeContext'
import { getMonthlyReport } from '../services/transactionService'
import { formatRupiah } from '../utils/formatRupiah'
import { showToast } from '../components/ui/Toast'

const BULAN = [
  'Januari','Februari','Maret','April','Mei','Juni',
  'Juli','Agustus','September','Oktober','November','Desember',
]

// Tahun 2020 sampai 2045
const TAHUN_LIST = Array.from({ length: 2045 - 2020 + 1 }, (_, i) => 2020 + i)

export default function Laporan() {
  const now = new Date()
  const { theme } = useTheme()
  const isDark    = theme === 'dark'

  const [bulan, setBulan]     = useState(now.getMonth() + 1)
  const [tahun, setTahun]     = useState(now.getFullYear())
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(false)

  async function fetchLaporan() {
    setLoading(true)
    try {
      const res = await getMonthlyReport(bulan, tahun)
      setData(res)
    } catch {
      showToast('Gagal memuat laporan.', 'error')
      setData(null)
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchLaporan() }, [bulan, tahun])

  // Menghitung jumlah hari maksimal pada bulan dan tahun yang dipilih (Mencegah bug tanggal 30/31 di bulan Februari)
  const maxDaysInMonth = new Date(tahun, bulan, 0).getDate()

  const chartData   = (data?.daily_summary || [])
    .filter((d) => Number(d.tanggal) <= maxDaysInMonth) // Filter membuang tanggal fiktif
    .map((d) => ({
      tanggal: String(d.tanggal),
      total: d.total,
    }))
    
  const topProducts = data?.top_products || []
  const maxTerjual  = topProducts[0]?.total_terjual || 1

  const card   = isDark ? '#161f2e' : '#ffffff'
  const bdr    = isDark ? '#1e2d3d' : '#e2f0e8'
  const txt    = isDark ? '#f1f5f9' : '#111827'
  const txtMut = isDark ? '#64748b' : '#6b7280'
  const headBg = isDark ? '#0f172a' : '#fafffe'

  const selectStyle = {
    background: card,
    border: `1.5px solid ${isDark ? '#1e2d3d' : '#d1fae5'}`,
    color: txt,
    borderRadius: 12,
    padding: '8px 14px',
    fontSize: 13,
    fontWeight: 600,
    outline: 'none',
    cursor: 'pointer',
  }

  // Kartu ringkasan — nama lebih mudah dipahami
  const summaryCards = [
    {
      title: 'Uang Masuk Bulan Ini',
      sub: 'Total semua penjualan',
      value: data?.total_pemasukan ?? 0,
      type: 'rupiah',
      icon: '💰',
      delay: '',
    },
    {
      title: 'Jumlah Nota / Pesanan',
      sub: 'Transaksi yang tercatat',
      value: data?.total_transaksi ?? 0,
      type: 'number',
      icon: '🧾',
      delay: 'delay-1',
    },
    {
      title: 'Rata-rata Per Hari',
      sub: 'Pendapatan harian rata-rata',
      value: data?.rata_rata_harian ?? 0,
      type: 'rupiah',
      icon: '📈',
      delay: 'delay-2',
    },
  ]

  return (
    <MainLayout>
      <div className="space-y-5 animate-fade-up">

        {/* ── Header ── */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h2 className="text-2xl font-extrabold" style={{ color: txt }}>
              Laporan Keuangan
            </h2>
            <p className="text-sm mt-0.5" style={{ color: txtMut }}>
              Rekap pemasukan {BULAN[bulan - 1]} {tahun}
            </p>
          </div>
          <div className="flex gap-2 flex-wrap">
            <select value={bulan} onChange={(e) => setBulan(Number(e.target.value))} style={selectStyle}>
              {BULAN.map((b, i) => <option key={i} value={i + 1}>{b}</option>)}
            </select>
            <select value={tahun} onChange={(e) => setTahun(Number(e.target.value))} style={selectStyle}>
              {TAHUN_LIST.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
        </div>

        {/* ── Kartu ringkasan ── */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {summaryCards.map((c) => (
            <div key={c.title} className={`animate-fade-up ${c.delay}`}>
              <SummaryCard
                title={c.title}
                sub={c.sub}
                value={c.value}
                type={c.type}
                icon={c.icon}
                loading={loading}
              />
            </div>
          ))}
        </div>

        {/* ── Grafik ── */}
        <div className="rounded-2xl overflow-hidden animate-fade-up delay-3"
          style={{ border: `1px solid ${bdr}`, background: card, boxShadow: `0 2px 20px rgba(0,0,0,${isDark ? '0.3' : '0.06'})` }}>
          <div className="px-5 py-4 border-b" style={{ borderColor: bdr, background: headBg }}>
            <h3 className="font-extrabold text-base" style={{ color: txt }}>
              Grafik Penjualan Harian
            </h3>
            <p className="text-xs mt-0.5" style={{ color: txtMut }}>
              Klik tombol ‹ › pada grafik untuk melihat hari lain
              {chartData.length > 0 && (
                <span className="ml-2 px-2 py-0.5 rounded-full font-semibold"
                  style={{ background: isDark ? '#14532d' : '#dcfce7', color: isDark ? '#4ade80' : '#15803d', fontSize: 10 }}>
                  {chartData.length} hari
                </span>
              )}
            </p>
          </div>
          <div className="p-4">
            {loading ? (
              <div className="space-y-3">
                <div className="flex items-end gap-3 h-56">
                  {[60, 85, 45, 95, 70, 55, 80].map((h, i) => (
                    <div key={i} className="flex-1 rounded-t-lg animate-pulse"
                      style={{ height: `${h}%`, background: isDark ? '#1e293b' : '#dcfce7' }} />
                  ))}
                </div>
                <div className="flex justify-between">
                  {[1,2,3,4,5,6,7].map((n) => (
                    <div key={n} className="w-8 h-3 rounded animate-pulse"
                      style={{ background: isDark ? '#1e293b' : '#f0fdf4' }} />
                  ))}
                </div>
              </div>
            ) : chartData.length > 0 ? (
              <RevenueBarChart data={chartData} bulan={bulan} tahun={tahun} />
            ) : (
              <EmptyState message="Tidak ada data penjualan di bulan ini." />
            )}
          </div>
        </div>

        {/* ── Produk Terlaris ── */}
        <div className="rounded-2xl overflow-hidden animate-fade-up delay-4"
          style={{ border: `1px solid ${bdr}`, background: card, boxShadow: `0 2px 20px rgba(0,0,0,${isDark ? '0.3' : '0.06'})` }}>
          <div className="px-5 py-4 border-b" style={{ borderColor: bdr, background: headBg }}>
            <h3 className="font-extrabold text-base" style={{ color: txt }}>Menu Paling Laris</h3>
            <p className="text-xs mt-0.5" style={{ color: txtMut }}>
              Urutan menu yang paling banyak dipesan bulan ini
            </p>
          </div>
          <div className="p-5">
            {loading ? (
              <div className="space-y-5">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-full animate-pulse" style={{ background: isDark ? '#1e293b' : '#f0fdf4' }} />
                    <div className="flex-1">
                      <div className="h-3.5 w-32 rounded animate-pulse mb-2" style={{ background: isDark ? '#1e293b' : '#f0fdf4' }} />
                      <div className="h-2 rounded-full animate-pulse" style={{ background: isDark ? '#1e293b' : '#f0fdf4', width: `${70 - i * 15}%` }} />
                    </div>
                    <div className="h-4 w-20 rounded animate-pulse" style={{ background: isDark ? '#1e293b' : '#f0fdf4' }} />
                  </div>
                ))}
              </div>
            ) : topProducts.length === 0 ? (
              <EmptyState message="Belum ada data menu yang terjual bulan ini." />
            ) : (
              <div className="space-y-5">
                {topProducts.map((p, idx) => {
                  const pct      = Math.round((p.total_terjual / maxTerjual) * 100)
                  const medals   = ['🥇', '🥈', '🥉']
                  const barColor = idx === 0 ? '#16a34a'
                    : idx === 1 ? '#4ade80'
                    : idx === 2 ? '#86efac'
                    : isDark ? '#1e293b' : '#d1fae5'

                  return (
                    <div key={idx} className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
                        style={{
                          background: idx < 3 ? (isDark ? '#14532d' : '#dcfce7') : (isDark ? '#1e293b' : '#f3f4f6'),
                          fontSize: idx < 3 ? 16 : 13,
                          fontWeight: 800,
                          color: idx >= 3 ? txtMut : undefined,
                        }}>
                        {idx < 3 ? medals[idx] : idx + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-center mb-1.5">
                          <span className="text-sm font-bold truncate" style={{ color: txt }}>
                            {p.nama_produk}
                          </span>
                          <span className="text-xs ml-2 shrink-0 font-semibold" style={{ color: txtMut }}>
                            {p.total_terjual}× terjual
                          </span>
                        </div>
                        <div className="h-2.5 rounded-full overflow-hidden" style={{ background: isDark ? '#1e293b' : '#f0fdf4' }}>
                          <div className="h-full rounded-full transition-all duration-700 ease-out"
                            style={{ width: `${pct}%`, background: barColor }} />
                        </div>
                      </div>
                      <span className="text-sm font-extrabold shrink-0"
                        style={{ color: isDark ? '#4ade80' : '#15803d' }}>
                        {formatRupiah(p.total_pendapatan)}
                      </span>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>

      </div>
    </MainLayout>
  )
}