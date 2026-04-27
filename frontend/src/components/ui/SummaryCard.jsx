import { formatRupiah } from '../../utils/formatRupiah'

export default function SummaryCard({ title, value, type = 'number', icon, loading = false }) {
  if (loading) {
    return (
      <div className="rounded-2xl p-5 bg-white" style={{ border: '1px solid #e2e8f0', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
        <div className="h-3 w-24 rounded-full animate-pulse mb-3" style={{ background: '#f0fdf4' }} />
        <div className="h-7 w-32 rounded-full animate-pulse" style={{ background: '#f0fdf4' }} />
      </div>
    )
  }

  const displayValue = type === 'rupiah'
    ? formatRupiah(value ?? 0)
    : (value ?? 0).toLocaleString('id-ID')

  return (
    <div className="rounded-2xl p-5 bg-white transition-all hover:-translate-y-0.5"
      style={{ border: '1px solid #e2e8f0', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{title}</p>
        {icon && <span className="text-xl">{icon}</span>}
      </div>
      <p className="text-2xl font-extrabold text-gray-900 leading-none">{displayValue}</p>
    </div>
  )
}
