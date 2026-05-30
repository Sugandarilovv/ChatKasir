import { useState, useEffect } from 'react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from 'recharts'
import { useTheme } from '../../context/ThemeContext'
import { formatRupiah } from '../../utils/formatRupiah'

const PAGE_SIZE = 7
const HARI      = ['MIN','SEN','SEL','RAB','KAM','JUM','SAB']
const BLN_SHORT = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des']

function getNamaHari(tanggal, bulan, tahun) {
  const d = new Date(tahun, bulan - 1, parseInt(tanggal))
  return HARI[d.getDay()]
}

// FORMATTER: Memotong desimal agar rapi (cth: 1.34jt jadi 1.3jt)
function truncate1Dec(val) {
  const num = Math.floor(val / 100000) / 10
  return num.toFixed(1).replace(/\.0$/, '')
}

function fmt(v) {
  if (v === 0) return '0'
  if (v >= 1000000) return `${truncate1Dec(v)}jt`
  if (v >= 1000)    return `${Math.round(v / 1000)}rb`
  return `${v}`
}

function fmtRing(v) {
  if (v >= 1000000) return `Rp ${truncate1Dec(v)} Juta`
  return formatRupiah(v)
}

function CustomTooltip({ active, payload, label, isDark, bulan }) {
  if (!active || !payload?.length) return null
  const val = payload[0].value
  const display = fmtRing(val)
  
  return (
    <div style={{
      background: isDark ? '#1e293b' : '#ffffff',
      border: `1px solid ${isDark ? '#334155' : '#6ee7b7'}`,
      borderRadius: 14, padding: '10px 16px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
      textAlign: 'center', minWidth: 130,
    }}>
      <p style={{ fontSize: 11, fontWeight: 700, color: isDark ? '#94a3b8' : '#047857', marginBottom: 4 }}>
        {label} {BLN_SHORT[bulan - 1]}
      </p>
      <p style={{ fontSize: 15, fontWeight: 800, color: isDark ? '#4ade80' : '#065f46' }}>
        {display}
      </p>
    </div>
  )
}

function CustomDot(props) {
  const { cx, cy, payload, maxVal, isDark } = props
  const isMax = payload.total === maxVal && maxVal > 0 
  
  if (!isMax) return (
    <circle cx={cx} cy={cy} r={4}
      fill={isDark ? '#0f172a' : '#fff'}
      stroke={isDark ? '#4ade80' : '#10b981'} strokeWidth={2.5} />
  )
  return (
    <g>
      <circle cx={cx} cy={cy} r={12}
        fill={isDark ? 'rgba(74,222,128,0.2)' : 'rgba(16,185,129,0.1)'} />
      <circle cx={cx} cy={cy} r={7}
        fill={isDark ? '#4ade80' : '#10b981'}
        stroke={isDark ? '#0f172a' : '#fff'} strokeWidth={2.5} />
    </g>
  )
}

export default function RevenueBarChart({ data = [], bulan = 1, tahun = 2026 }) {
  const { theme } = useTheme()
  const isDark    = theme === 'dark'
  const [offset, setOffset] = useState(0)

  // 1. BUAT DATA DINAMIS FULL 1 BULAN
  const daysInMonth = new Date(tahun, bulan, 0).getDate()
  const fullData = Array.from({ length: daysInMonth }, (_, i) => {
    const tgl = String(i + 1)
    const found = data.find(d => String(d.tanggal) === tgl)
    return {
      tanggal: tgl,
      total: found ? found.total : 0, 
    }
  })

  // 2. AUTO-ARAHKAN KE HALAMAN TERAKHIR YANG ADA DATANYA
  useEffect(() => {
    if (data && data.length > 0) {
      const lastTransactionDay = Math.max(...data.map(d => Number(d.tanggal)))
      const targetPage = Math.floor((lastTransactionDay - 1) / PAGE_SIZE)
      setOffset(targetPage * PAGE_SIZE)
    } else {
      setOffset(0)
    }
  }, [data, bulan, tahun])

  const totalPages  = Math.ceil(fullData.length / PAGE_SIZE)
  const currentPage = Math.floor(offset / PAGE_SIZE)

  // 3. AMBIL DATA UNTUK HALAMAN SAAT INI
  const visibleData = fullData.slice(offset, offset + PAGE_SIZE).map(d => ({
    ...d,
    hari: getNamaHari(d.tanggal, bulan, tahun),
  }))

  const maxVal  = Math.max(...visibleData.map(d => d.total), 0)
  const totalPg = visibleData.reduce((s, d) => s + d.total, 0)

  // =====================================================================
  // FOKUS PERBAIKAN: Memaksa garis Y sejajar lurus dengan nilai pemasukan
  // =====================================================================
  // Ambil semua nominal pemasukan harian yang ada di tampilan saat ini
  let yTicks = visibleData
    .map(d => d.total)
    .filter((v, i, arr) => arr.indexOf(v) === i) // Hapus angka yang kembar/duplikat
    
  // Pastikan angka 0 selalu ada di urutan paling bawah
  if (!yTicks.includes(0)) {
    yTicks.push(0)
  }
  
  // Urutkan angka dari yang terkecil ke terbesar
  yTicks.sort((a, b) => a - b)

  // Berikan sedikit ruang kosong di bagian atas (+15%) agar titik tertinggi tidak menabrak atap grafik
  const yDomainMax = maxVal > 0 ? maxVal * 1.15 : 100000
  // =====================================================================

  const startDay = visibleData[0]?.tanggal || ''
  const endDay   = visibleData[visibleData.length - 1]?.tanggal || ''
  const blnLabel = ['Januari','Februari','Maret','April','Mei','Juni',
                    'Juli','Agustus','September','Oktober','November','Desember'][bulan - 1]

  const axisColor = isDark ? '#94a3b8' : '#6b7280'
  const gridColor = isDark ? '#334155' : '#e6f7ef'
  const cardBg    = isDark ? '#111827' : '#ffffff'
  const headGrad  = isDark
    ? 'linear-gradient(135deg,#1e293b,#0f172a)'
    : 'linear-gradient(135deg,#ecfdf5,#d1fae5)'
  const txt       = isDark ? '#f8fafc' : '#065f46'
  const txtMut    = isDark ? '#cbd5e1' : '#047857'

  if (!data.length) {
    return (
      <div className="flex flex-col items-center justify-center h-52 gap-3">
        <span style={{ fontSize: 40 }}>📊</span>
        <p style={{ color: axisColor, fontSize: 13, fontWeight: 500 }}>
          Belum ada data untuk ditampilkan
        </p>
      </div>
    )
  }

  return (
    <div style={{
      borderRadius: 16, overflow: 'hidden',
      border: `1px solid ${isDark ? '#334155' : '#a7f3d0'}`,
    }}>
      <div style={{ background: headGrad }} className="px-3 py-3 sm:px-5 sm:py-4">
        
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 mb-3 w-full">
          <p className="text-[13px] sm:text-base font-black shrink-0" style={{ color: txt, letterSpacing: '-0.3px' }}>
            PEMASUKAN HARIAN
          </p>

          <div className="flex flex-row items-center justify-between gap-2 w-full md:w-auto overflow-hidden">
            <div className="flex items-center gap-1.5 px-2 py-1.5 sm:px-3 sm:py-2 rounded-lg border truncate" style={{
              background: isDark ? 'rgba(30,41,59,0.8)' : 'rgba(255,255,255,0.85)',
              borderColor: isDark ? '#475569' : '#6ee7b7'
            }}>
              <span className="text-[11px] sm:text-sm shrink-0">📅</span>
              <span className="text-[9px] sm:text-xs font-bold truncate" style={{ color: txt }}>
                <span className="hidden sm:inline">PERIODE: </span>
                <strong>{startDay} – {endDay} {blnLabel} {tahun}</strong>
              </span>
            </div>

            <div className="flex items-center gap-1 sm:gap-2 shrink-0">
              <button
                onClick={() => setOffset(o => Math.max(0, o - PAGE_SIZE))}
                disabled={offset === 0}
                className="w-7 h-7 sm:w-8 sm:h-8 flex items-center justify-center rounded-lg border-[1.5px] text-base sm:text-lg font-black transition-all"
                style={{
                  background: isDark ? 'rgba(74,222,128,0.1)' : 'rgba(255,255,255,0.8)',
                  borderColor: isDark ? '#334155' : '#6ee7b7',
                  color: offset === 0 ? (isDark ? '#475569' : '#a7f3d0') : (isDark ? '#4ade80' : '#065f46'),
                  cursor: offset === 0 ? 'not-allowed' : 'pointer',
                }}
              >‹</button>

              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }).map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setOffset(i * PAGE_SIZE)}
                    className="h-1.5 sm:h-2 rounded-full transition-all duration-300"
                    style={{
                      width: currentPage === i ? 16 : 6,
                      background: currentPage === i ? (isDark ? '#4ade80' : '#10b981') : (isDark ? '#334155' : '#a7f3d0'),
                      border: 'none', cursor: 'pointer', padding: 0,
                    }}
                  />
                ))}
              </div>

              <button
                onClick={() => { if (offset + PAGE_SIZE < fullData.length) setOffset(o => o + PAGE_SIZE) }}
                disabled={offset + PAGE_SIZE >= fullData.length}
                className="w-7 h-7 sm:w-8 sm:h-8 flex items-center justify-center rounded-lg border-[1.5px] text-base sm:text-lg font-black transition-all"
                style={{
                  background: isDark ? 'rgba(74,222,128,0.1)' : 'rgba(255,255,255,0.8)',
                  borderColor: isDark ? '#334155' : '#6ee7b7',
                  color: offset + PAGE_SIZE >= fullData.length ? (isDark ? '#475569' : '#a7f3d0') : (isDark ? '#4ade80' : '#065f46'),
                  cursor: offset + PAGE_SIZE >= fullData.length ? 'not-allowed' : 'pointer',
                }}
              >›</button>
            </div>
          </div>
        </div>

        <div>
          <span className="text-[10px] sm:text-xs font-bold" style={{ color: txtMut }}>
            TOTAL {visibleData.length} HARI INI:{' '}
            <strong style={{ color: isDark ? '#4ade80' : '#065f46' }}>{fmtRing(totalPg)}</strong>
          </span>
        </div>
      </div>

      <div style={{ background: cardBg }} className="p-2 sm:p-5">
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={visibleData} margin={{ top: 16, right: 15, left: 0, bottom: 8 }}>
            <defs>
              <linearGradient id="areaLight" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#10b981" stopOpacity={0.35}/>
                <stop offset="70%"  stopColor="#34d399" stopOpacity={0.08}/>
                <stop offset="100%" stopColor="#ecfdf5"  stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="areaDark" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#4ade80" stopOpacity={0.4}/>
                <stop offset="70%"  stopColor="#22c55e" stopOpacity={0.1}/>
                <stop offset="100%" stopColor="#0f172a"  stopOpacity={0}/>
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="4 4" stroke={gridColor} vertical={false} />

            <XAxis
              dataKey="tanggal"
              tickLine={false}
              axisLine={false}
              height={40}
              tick={({ x, y, payload }) => {
                const d = visibleData.find(v => v.tanggal === payload.value)
                return (
                  <g transform={`translate(${x},${y})`}>
                    <text x={0} y={10} textAnchor="middle" fill={axisColor} fontSize={10} fontWeight={600}>
                      {payload.value} {BLN_SHORT[bulan - 1]}
                    </text>
                    <text x={0} y={22} textAnchor="middle" fill={isDark ? '#4ade80' : '#10b981'} fontSize={9} fontWeight={800}>
                      ({d?.hari || ''})
                    </text>
                  </g>
                )
              }}
            />

            {/* Sumbu Y kini menggunakan nilai absolut dari yTicks */}
            <YAxis
              tickFormatter={fmt}
              tick={{ fontSize: 10, fill: axisColor, fontWeight: 600 }}
              tickLine={false} 
              axisLine={false} 
              width={50}
              domain={[0, yDomainMax]}
              ticks={yTicks}
            />

            <Tooltip
              content={<CustomTooltip isDark={isDark} bulan={bulan} />}
              cursor={{ stroke: isDark ? '#4ade80' : '#10b981', strokeWidth: 1.5, strokeDasharray: '5 4' }}
            />

            <Area
              type="monotone"
              dataKey="total"
              stroke={isDark ? '#4ade80' : '#10b981'}
              strokeWidth={3}
              fill={`url(#${isDark ? 'areaDark' : 'areaLight'})`}
              dot={(props) => {
                const { key, ...restProps } = props;
                return <CustomDot key={key} {...restProps} maxVal={maxVal} isDark={isDark} />;
              }}
              activeDot={{ r: 6, fill: isDark ? '#4ade80' : '#10b981', stroke: isDark ? '#0f172a' : '#fff', strokeWidth: 3 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}