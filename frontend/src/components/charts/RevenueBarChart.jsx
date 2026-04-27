import { useState } from 'react'
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

function CustomTooltip({ active, payload, label, isDark, bulan }) {
  if (!active || !payload?.length) return null
  const val = payload[0].value
  const display = val >= 1000000
    ? `Rp ${(val / 1000000).toFixed(1)} Juta`
    : formatRupiah(val)
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
  const isMax = payload.total === maxVal
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

  const totalPages  = Math.ceil(data.length / PAGE_SIZE)
  const currentPage = Math.floor(offset / PAGE_SIZE)

  const visibleData = data.slice(offset, offset + PAGE_SIZE).map(d => ({
    ...d,
    hari: getNamaHari(d.tanggal, bulan, tahun),
  }))

  const maxVal   = Math.max(...visibleData.map(d => d.total), 1)
  const totalPg  = visibleData.reduce((s, d) => s + d.total, 0)

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

  function fmt(v) {
    if (v >= 1000000) return `${(v / 1000000).toFixed(1)}jt`
    if (v >= 1000)    return `${(v / 1000).toFixed(0)}rb`
    return `${v}`
  }

  function fmtRing(v) {
    return v >= 1000000
      ? `Rp ${(v / 1000000).toFixed(1)} Juta`
      : formatRupiah(v)
  }

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
      borderRadius: 20, overflow: 'hidden',
      border: `1px solid ${isDark ? '#334155' : '#a7f3d0'}`,
    }}>
      {/* ── Header ── */}
      <div style={{ background: headGrad, padding: '16px 20px 12px' }}>
        <div className="flex items-center justify-between flex-wrap gap-3 mb-3">
          <p style={{ fontSize: 16, fontWeight: 900, color: txt, letterSpacing: '-0.3px' }}>
            PEMASUKAN HARIAN
          </p>

          <div className="flex items-center gap-3 flex-wrap">
            {/* Periode */}
            <div style={{
              background: isDark ? 'rgba(30,41,59,0.8)' : 'rgba(255,255,255,0.85)',
              border: `1px solid ${isDark ? '#475569' : '#6ee7b7'}`,
              borderRadius: 10, padding: '5px 12px',
              display: 'flex', alignItems: 'center', gap: 7,
            }}>
              <span style={{ fontSize: 13 }}>📅</span>
              <span style={{ fontSize: 12, fontWeight: 700, color: txt }}>
                PERIODE: <strong>{startDay} – {endDay} {blnLabel} {tahun}</strong>
              </span>
            </div>

            {/* Navigasi */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <button
                onClick={() => setOffset(o => Math.max(0, o - PAGE_SIZE))}
                disabled={offset === 0}
                style={{
                  width: 34, height: 34, borderRadius: 10,
                  background: isDark ? 'rgba(74,222,128,0.1)' : 'rgba(255,255,255,0.8)',
                  border: `1.5px solid ${isDark ? '#334155' : '#6ee7b7'}`,
                  color: offset === 0 ? (isDark ? '#475569' : '#a7f3d0') : (isDark ? '#4ade80' : '#065f46'),
                  fontSize: 18, fontWeight: 900,
                  cursor: offset === 0 ? 'not-allowed' : 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}
              >‹</button>

              <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                {Array.from({ length: totalPages }).map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setOffset(i * PAGE_SIZE)}
                    style={{
                      width: currentPage === i ? 22 : 8,
                      height: 8, borderRadius: 99,
                      background: currentPage === i
                        ? (isDark ? '#4ade80' : '#10b981')
                        : (isDark ? '#334155' : '#a7f3d0'),
                      border: 'none', cursor: 'pointer', padding: 0,
                      transition: 'all 0.25s ease',
                    }}
                  />
                ))}
              </div>

              <button
                onClick={() => { if (offset + PAGE_SIZE < data.length) setOffset(o => o + PAGE_SIZE) }}
                disabled={offset + PAGE_SIZE >= data.length}
                style={{
                  width: 34, height: 34, borderRadius: 10,
                  background: isDark ? 'rgba(74,222,128,0.1)' : 'rgba(255,255,255,0.8)',
                  border: `1.5px solid ${isDark ? '#334155' : '#6ee7b7'}`,
                  color: offset + PAGE_SIZE >= data.length
                    ? (isDark ? '#475569' : '#a7f3d0')
                    : (isDark ? '#4ade80' : '#065f46'),
                  fontSize: 18, fontWeight: 900,
                  cursor: offset + PAGE_SIZE >= data.length ? 'not-allowed' : 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}
              >›</button>
            </div>
          </div>
        </div>

        {/* Total (Rata-rata Harian Dihapus) */}
        <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 12, fontWeight: 600, color: txtMut }}>
            TOTAL {visibleData.length} HARI INI:{' '}
            <strong style={{ color: isDark ? '#4ade80' : '#065f46' }}>{fmtRing(totalPg)}</strong>
          </span>
        </div>
      </div>

      {/* ── Area chart ── */}
      <div style={{ background: cardBg, padding: '20px 8px 16px' }}>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={visibleData} margin={{ top: 16, right: 16, left: 4, bottom: 8 }}>
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
              height={48}
              tick={({ x, y, payload }) => {
                const d = visibleData.find(v => v.tanggal === payload.value)
                return (
                  <g transform={`translate(${x},${y})`}>
                    <text x={0} y={12} textAnchor="middle"
                      fill={axisColor} fontSize={12} fontWeight={600}>
                      {payload.value} {BLN_SHORT[bulan - 1]}
                    </text>
                    <text x={0} y={26} textAnchor="middle"
                      fill={isDark ? '#4ade80' : '#10b981'} fontSize={10} fontWeight={800}>
                      ({d?.hari || ''})
                    </text>
                  </g>
                )
              }}
            />

            <YAxis
              tickFormatter={fmt}
              tick={{ fontSize: 11, fill: axisColor, fontWeight: 500 }}
              tickLine={false} axisLine={false} width={44}
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
              dot={(props) => <CustomDot {...props} maxVal={maxVal} isDark={isDark} />}
              activeDot={{ r: 7, fill: isDark ? '#4ade80' : '#10b981', stroke: isDark ? '#0f172a' : '#fff', strokeWidth: 3 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}