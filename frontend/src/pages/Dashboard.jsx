import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import MainLayout from '../components/layout/MainLayout'
import SummaryCard from '../components/ui/SummaryCard'
import LoadingSkeleton from '../components/ui/LoadingSkeleton'
import EmptyState from '../components/ui/EmptyState'
import { useTransactions } from '../hooks/useTransactions'
import { formatRupiah } from '../utils/formatRupiah'

function today() { return new Date().toISOString().split('T')[0] }

function formatTanggal(str) {
  return new Date(str).toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [tanggal, setTanggal] = useState(today())
  const { data, loading, error, refetch } = useTransactions(tanggal)

  const totalNominal   = data.reduce((s, t) => s + t.jumlah * t.harga, 0)
  const totalTranaksi  = data.length
  const rataRata       = totalTranaksi > 0 ? Math.round(totalNominal / totalTranaksi) : 0

  const cards = [
    { title: 'Total Pemasukan',       value: totalNominal,  type: 'rupiah', icon: '💰', delay: '' },
    { title: 'Jumlah Transaksi',      value: totalTranaksi, type: 'number', icon: '🧾', delay: 'delay-1' },
    { title: 'Rata-rata per Pesanan', value: rataRata,      type: 'rupiah', icon: '📈', delay: 'delay-2' },
  ]

  return (
    <MainLayout>
      <div className="space-y-6 animate-fade-up">

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h2 className="text-2xl font-extrabold text-gray-900">Dashboard</h2>
            <p className="text-gray-400 text-sm mt-0.5">{formatTanggal(tanggal)}</p>
          </div>
          <div className="flex gap-2 items-center">
            {/* PERBAIKAN: Rentang tanggal diubah menjadi 2020 hingga 2045 */}
            <input 
              type="date" 
              min="2020-01-01" 
              max="2045-12-31" 
              value={tanggal}
              onChange={(e) => setTanggal(e.target.value)}
              className="px-3 py-2 rounded-xl border text-sm outline-none focus:ring-2 focus:ring-green-400 focus:border-green-400 transition-all bg-white"
              style={{ borderColor: '#e2e8f0' }} 
            />
            <button onClick={() => navigate('/input')}
              className="px-4 py-2 rounded-xl text-sm font-bold text-white transition-all active:scale-95"
              style={{ background: '#16a34a' }}>
              + Catat
            </button>
          </div>
        </div>

        {/* Kartu ringkasan */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {cards.map((c) => (
            <div key={c.title} className={`animate-fade-up ${c.delay}`}>
              <SummaryCard title={c.title} value={c.value} type={c.type} icon={c.icon} loading={loading} />
            </div>
          ))}
        </div>

        {/* Tabel */}
        <div className="rounded-2xl overflow-hidden animate-fade-up delay-3"
          style={{ border: '1px solid #e2e8f0', boxShadow: '0 2px 16px rgba(0,0,0,0.05)' }}>

          <div className="flex items-center justify-between px-5 py-4 bg-white border-b" style={{ borderColor: '#f1f5f9' }}>
            <h3 className="font-bold text-gray-800">Daftar Transaksi</h3>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full"
              style={{ background: loading ? '#f1f5f9' : totalTranaksi > 0 ? '#dcfce7' : '#f1f5f9', color: totalTranaksi > 0 ? '#15803d' : '#94a3b8' }}>
              {loading ? '...' : `${totalTranaksi} item`}
            </span>
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-center justify-between px-5 py-3 bg-red-50 border-b border-red-100">
              <span className="text-sm text-red-600">{error}</span>
              <button onClick={refetch} className="text-xs font-semibold text-red-600 underline">Coba lagi</button>
            </div>
          )}

          {loading && <div className="p-5"><LoadingSkeleton rows={4} /></div>}

          {!loading && !error && data.length === 0 && (
            <div className="bg-white">
              <EmptyState message="Belum ada transaksi hari ini. Yuk mulai catat!"
                action={{ label: '+ Catat Sekarang', onClick: () => navigate('/input') }} />
            </div>
          )}

          {!loading && !error && data.length > 0 && (
            <>
              {/* Header row */}
              <div className="grid text-xs font-semibold text-gray-400 uppercase tracking-widest px-5 py-2.5"
                style={{ gridTemplateColumns: '32px 1fr 60px 120px 130px', background: '#fafffe', borderBottom: '1px solid #f0fdf4' }}>
                <span>#</span><span>Produk</span><span className="text-center">Jml</span>
                <span className="text-right">Harga</span><span className="text-right">Subtotal</span>
              </div>
              <div className="bg-white divide-y" style={{ divideColor: '#f8fafc' }}>
                {data.map((t, i) => (
                  <div key={t.id || i}
                    className="grid items-center px-5 py-3.5 hover:bg-green-50/30 transition-colors"
                    style={{ gridTemplateColumns: '32px 1fr 60px 120px 130px' }}>
                    <span className="text-xs font-bold text-gray-300">{i + 1}</span>
                    <span className="font-semibold text-gray-800 text-sm">{t.nama_produk}</span>
                    <span className="text-center text-sm text-gray-500">{t.jumlah}</span>
                    <span className="text-right text-sm text-gray-500">{formatRupiah(t.harga)}</span>
                    <span className="text-right text-sm font-bold" style={{ color: '#16a34a' }}>{formatRupiah(t.jumlah * t.harga)}</span>
                  </div>
                ))}
              </div>
              {/* Total footer */}
              <div className="flex items-center justify-between px-5 py-3 border-t" style={{ borderColor: '#f0fdf4', background: '#fafffe' }}>
                <span className="text-sm font-semibold text-gray-400">Total {totalTranaksi} item</span>
                <span className="text-lg font-extrabold" style={{ color: '#15803d' }}>{formatRupiah(totalNominal)}</span>
              </div>
            </>
          )}
        </div>
      </div>
    </MainLayout>
  )
}