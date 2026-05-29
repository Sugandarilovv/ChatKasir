import { useState, forwardRef } from 'react'
import { useNavigate } from 'react-router-dom'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import MainLayout from '../components/layout/MainLayout'
import SummaryCard from '../components/ui/SummaryCard'
import LoadingSkeleton from '../components/ui/LoadingSkeleton'
import EmptyState from '../components/ui/EmptyState'
import { useTransactions } from '../hooks/useTransactions'
import { formatRupiah } from '../utils/formatRupiah'
import { useTheme } from '../context/ThemeContext' 

function formatDateToYMD(dateObj) {
  return dateObj.toISOString().split('T')[0]
}

function formatTanggal(str) {
  return new Date(str).toLocaleDateString('id-ID', { 
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' 
  })
}

export default function Dashboard() {
  const navigate = useNavigate()
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  
  const [selectedDate, setSelectedDate] = useState(new Date())
  
  const tanggalString = formatDateToYMD(selectedDate)
  const { data, loading, error } = useTransactions(tanggalString)

  const totalNominal  = data.reduce((s, t) => s + (t.total || t.jumlah * t.harga), 0)
  // Jumlah pesanan unik = jumlah extraction_id yang berbeda (1 chat bisa punya banyak item)
  const pesananUnik   = new Set(data.map(t => t.extraction_id).filter(Boolean)).size || data.length
  const totalTranaksi = pesananUnik
  const rataRata      = totalTranaksi > 0 ? Math.round(totalNominal / totalTranaksi) : 0

  const bgTable     = isDark ? '#1e293b' : '#ffffff' 
  const bgHeader    = isDark ? '#0f172a' : '#f8fafc'
  const borderColor = isDark ? '#334155' : '#e2e8f0'
  const textUtama   = isDark ? '#f1f5f9' : '#1f2937'
  const textMuda    = isDark ? '#94a3b8' : '#6b7280'
  const textNomor   = isDark ? '#4ade80' : '#94a3b8' 

  const gridCols = '8% 35% 15% 20% 22%'

  const cards = [
    { title: 'Total Pemasukan',       value: totalNominal,  type: 'rupiah', icon: '💰', delay: '' },
    { title: 'Jumlah Transaksi',      value: totalTranaksi, type: 'number', icon: '🧾', delay: 'delay-1' },
    { title: 'Rata-rata per Pesanan', value: rataRata,      type: 'rupiah', icon: '📈', delay: 'delay-2' },
  ]

  const CustomInput = forwardRef(({ value, onClick }, ref) => (
    <button 
      ref={ref}
      onClick={onClick}
      className="px-1.5 py-1 sm:px-4 sm:py-2.5 rounded-lg sm:rounded-xl border font-semibold outline-none focus:ring-2 focus:ring-green-500 transition-all flex items-center gap-1 sm:gap-2 hover:bg-gray-50 dark:hover:bg-slate-800 text-[10px] sm:text-sm whitespace-nowrap"
      style={{ background: bgTable, borderColor: borderColor, color: textUtama }}
    >
      <svg className="w-3 h-3 sm:w-4 sm:h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <span>{value}</span>
    </button>
  ));

  return (
    <MainLayout>
      <style>{`
        .react-datepicker {
          font-family: inherit;
          border-radius: 1rem;
          border: 1px solid ${borderColor};
          box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
          overflow: hidden;
          font-size: 0.9rem;
        }
        .react-datepicker__header { border-bottom: 1px solid ${borderColor}; padding-top: 12px; }
        .react-datepicker__navigation { top: 14px; }
        .react-datepicker__day--selected, .react-datepicker__day--keyboard-selected {
          background-color: #16a34a !important; color: white !important; border-radius: 0.5rem; font-weight: bold;
        }
        .react-datepicker__day:hover { border-radius: 0.5rem; }
        .react-datepicker__year-dropdown, .react-datepicker__month-dropdown {
          border-radius: 0.75rem; padding: 8px 0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .react-datepicker__year-option, .react-datepicker__month-option {
          padding: 6px 12px; transition: background-color 0.2s;
        }
        
        /* PERBAIKAN: Mengecilkan ukuran popup kalender secara agresif di layar HP */
        @media (max-width: 640px) {
          .react-datepicker { font-size: 0.65rem; }
          .react-datepicker__month-container { width: 190px; }
          .react-datepicker__day-name, .react-datepicker__day { width: 1.25rem; line-height: 1.25rem; margin: 0.1rem; }
          .react-datepicker__header { padding-top: 8px; }
          .react-datepicker__navigation { top: 8px; }
          .react-datepicker__current-month { font-size: 0.8rem; margin-bottom: 4px; }
        }

        .dark-calendar .react-datepicker { background-color: #1e293b; color: #f1f5f9; }
        .dark-calendar .react-datepicker__header { background-color: #0f172a; }
        .dark-calendar .react-datepicker__current-month, .dark-calendar .react-datepicker-time__header,
        .dark-calendar .react-datepicker-year-header, .dark-calendar .react-datepicker__day-name { color: #e2e8f0; font-weight: 600; }
        .dark-calendar .react-datepicker__day { color: #cbd5e1; }
        .dark-calendar .react-datepicker__day:hover { background-color: #334155; }
        .dark-calendar .react-datepicker__day--disabled { color: #475569; }
        .dark-calendar .react-datepicker__navigation-icon::before { border-color: #cbd5e1; }
        .dark-calendar .react-datepicker__year-dropdown, .dark-calendar .react-datepicker__month-dropdown { background-color: #1e293b; border: 1px solid #334155; }
        .dark-calendar .react-datepicker__year-option:hover, .dark-calendar .react-datepicker__month-option:hover { background-color: #334155; }
        .dark-calendar .react-datepicker__year-option--selected_year { color: #4ade80; font-weight: bold; }
      `}</style>

      <div className="space-y-10 sm:space-y-6 animate-fade-up">
        
        <div className="flex flex-row items-center justify-between gap-1 sm:gap-4 w-full">
          <div className="min-w-0 flex-1">
            <h2 className="text-sm sm:text-2xl font-extrabold truncate" style={{ color: textUtama }}>Dashboard Harian</h2>
            <p className="text-[9px] sm:text-sm mt-0.5 truncate" style={{ color: textMuda }}>{formatTanggal(tanggalString)}</p>
          </div>
          
          <div className="flex gap-1 sm:gap-2 items-center relative z-40 shrink-0">
            <div className={isDark ? 'dark-calendar' : ''}>
              <DatePicker
                selected={selectedDate}
                onChange={(date) => setSelectedDate(date)}
                minDate={new Date('2020-01-01')}
                maxDate={new Date('2045-12-31')}
                dateFormat="dd/MM/yyyy"
                showYearDropdown
                scrollableYearDropdown
                yearDropdownItemNumber={50}
                customInput={<CustomInput />}
              />
            </div>

            <button onClick={() => navigate('/input')}
              className="px-2 py-1 sm:px-4 sm:py-2.5 rounded-lg sm:rounded-xl text-[10px] sm:text-sm font-bold text-white transition-all active:scale-95 flex items-center gap-1 shadow-sm hover:shadow-md whitespace-nowrap"
              style={{ background: '#16a34a' }}>
              <span className="text-xs sm:text-lg leading-none">+</span> 
              <span>Catat</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 sm:gap-4 relative z-10">
          {cards.map((c, i) => (
            <div key={i} className={`animate-fade-up ${c.delay} h-full`}>
              <SummaryCard {...c} loading={loading} />
            </div>
          ))}
        </div>

        <div className="mt-12 sm:mt-13 rounded-xl sm:rounded-2xl overflow-hidden shadow-sm animate-fade-up delay-3 relative z-10" 
          style={{ border: `1px solid ${borderColor}`, background: bgTable }}>
          
          <div className="px-2 sm:px-6 py-2 sm:py-4 border-b" style={{ borderColor: borderColor, background: bgHeader }}>
            <h3 className="text-[10px] sm:text-base font-bold" style={{ color: textUtama }}>Detail Transaksi Hari Ini</h3>
          </div>

          <div className="overflow-hidden w-full">
            <div className="grid text-[8px] sm:text-xs font-bold uppercase tracking-widest px-2 sm:px-6 py-2 sm:py-3 border-b w-full"
              style={{ gridTemplateColumns: gridCols, borderColor: borderColor, color: textMuda, background: bgHeader }}>
              <span className="text-center truncate">No</span>
              <span className="truncate">Produk</span>
              <span className="text-center truncate">Jumlah</span>
              <span className="text-right pr-1 sm:pr-2 truncate">Harga</span>
              <span className="text-right truncate">Subtotal</span>
            </div>

            {loading ? (
              <div className="p-2 sm:p-6"><LoadingSkeleton count={3} /></div>
            ) : error ? (
              <div className="p-4 sm:p-10 text-center text-red-500 text-[10px] sm:text-base font-medium">Gagal memuat data.</div>
            ) : data.length === 0 ? (
              <EmptyState message="Belum ada transaksi di tanggal ini." />
            ) : (
              <div className="divide-y w-full" style={{ borderColor: borderColor }}>
                {data.map((t, i) => (
                  <div key={t.id || i}
                    className="grid items-center px-2 sm:px-6 py-2 sm:py-4 transition-colors hover:bg-green-500/5 group w-full"
                    style={{ gridTemplateColumns: gridCols }}>
                    
                    <span className="text-center text-[9px] sm:text-sm font-extrabold" style={{ color: textNomor }}>{i + 1}</span>
                    <span className="font-bold text-[9px] sm:text-sm truncate pr-1" style={{ color: textUtama }} title={t.nama_produk}>{t.nama_produk}</span>
                    <span className="text-center text-[9px] sm:text-sm font-medium" style={{ color: textMuda }}>{t.jumlah}</span>
                    <span className="text-right text-[9px] sm:text-sm font-medium pr-1 sm:pr-2 truncate" style={{ color: textMuda }}>{formatRupiah(t.harga)}</span>
                    <span className="text-right text-[9px] sm:text-sm font-extrabold truncate" style={{ color: '#16a34a' }}>
                      {formatRupiah(t.total || t.jumlah * t.harga)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {!loading && data.length > 0 && (
            <div className="px-3 sm:px-6 py-2 sm:py-4 border-t flex flex-row justify-between items-center w-full" 
              style={{ borderColor: borderColor, background: bgHeader }}>
              <span className="text-[9px] sm:text-sm font-bold" style={{ color: textMuda }}>Total: {totalTranaksi}</span>
              <div className="flex items-center gap-1 sm:gap-4">
                <span className="text-[9px] sm:text-sm font-bold" style={{ color: textMuda }}>Pemasukan:</span>
                <span className="text-[11px] sm:text-xl font-black" style={{ color: isDark ? '#4ade80' : '#15803d' }}>
                  {formatRupiah(totalNominal)}
                </span>
              </div>
            </div>
          )}
        </div>

      </div>
    </MainLayout>
  )
}