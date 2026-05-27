import { formatRupiah } from '../../utils/formatRupiah'
import { useTheme } from '../../context/ThemeContext'

export default function SummaryCard({ title, value, type = 'number', icon, loading = false }) {
  const { theme } = useTheme()
  const isDark    = theme === 'dark'

  const bgCard    = isDark ? '#1e293b' : '#ffffff'
  const bdrCard   = isDark ? '#334155' : '#e2e8f0'
  const txtTitle  = isDark ? '#94a3b8' : '#9ca3af' 
  const txtValue  = isDark ? '#f8fafc' : '#111827' 
  const pulseBg   = isDark ? '#334155' : '#f0fdf4'
  const shadow    = isDark ? '0 4px 12px rgba(0,0,0,0.2)' : '0 2px 8px rgba(0,0,0,0.04)'

  if (loading) {
    return (
      <div className="rounded-xl sm:rounded-2xl p-2.5 sm:p-5 transition-all h-full flex flex-col justify-center" style={{ background: bgCard, border: `1px solid ${bdrCard}`, boxShadow: shadow }}>
        <div className="h-2 sm:h-3 w-12 sm:w-24 rounded-full animate-pulse mb-2 sm:mb-3" style={{ background: pulseBg }} />
        <div className="h-4 sm:h-7 w-16 sm:w-32 rounded-full animate-pulse" style={{ background: pulseBg }} />
      </div>
    )
  }

  const displayValue = type === 'rupiah'
    ? formatRupiah(value ?? 0)
    : (value ?? 0).toLocaleString('id-ID')

  return (
    <div className="rounded-xl sm:rounded-2xl p-2.5 sm:p-5 transition-all hover:-translate-y-0.5 h-full flex flex-col justify-between gap-1"
      style={{ background: bgCard, border: `1px solid ${bdrCard}`, boxShadow: shadow }}>
      
      <div className="flex items-start justify-between gap-1 sm:mb-3">
        {/* PERBAIKAN TEKS JUDUL: Dikecilkan jadi text-[7px] dan dibiarkan wrap jika panjang */}
        <p className="text-[6px] sm:text-xs font-extrabold uppercase tracking-wide leading-tight line-clamp-2 sm:line-clamp-1" style={{ color: txtTitle }}>
          {title}
        </p>
        
        {/* PERBAIKAN IKON: Menghapus 'hidden sm:block' agar selalu muncul di HP. Ukuran HP di set text-[10px] */}
        {icon && <span className="text-[10px] sm:text-xl leading-none mt-0.5 sm:mt-0">{icon}</span>}
      </div>
      
      {/* PERBAIKAN NILAI: Dikecilkan agar muat di HP (text-[11px]) */}
      <p className="text-[11px] sm:text-2xl font-black leading-none truncate" style={{ color: txtValue }}>
        {displayValue}
      </p>
    </div>
  )
}