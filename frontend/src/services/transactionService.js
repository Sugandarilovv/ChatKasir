import api from './axiosInstance'

// Simpan transaksi yang sudah dikonfirmasi user
// items: array dari { product_name, quantity, price_satuan, total, confidence, is_manual }
export async function saveTransactions(extractionId, products) {
  const res = await api.post('/transactions', {
    extraction_id: extractionId,
    products,
  })
  return res.data
}

// Ambil transaksi harian (untuk Dashboard)
// tanggal: 'YYYY-MM-DD'
export async function getTransactions({ tanggal } = {}) {
  const params = {}
  if (tanggal) {
    params.startDate = tanggal
    params.endDate   = tanggal
  }
  const res = await api.get('/transactions/report', { params })
  // Backend kembalikan: { summary, chart_data, top_products, transactions }
  // Kita mapping transactions ke format yang dipakai Dashboard
  const transactions = (res.data.transactions || []).map((t) => ({
    id:          t.id,
    nama_produk: t.product_name,
    jumlah:      t.quantity,
    harga:       t.price_satuan,
  }))
  return { transactions }
}

// Laporan bulanan (untuk halaman Laporan)
export async function getMonthlyReport(bulan, tahun) {
  const res = await api.get('/report/monthly', { params: { month: bulan, year: tahun } })
  // Backend kembalikan: { summary: { total_revenue, total_items_sold, total_transactions }, data }
  const { summary, data } = res.data

  // Hitung daily_summary dari data transaksi
  const dailyMap = {}
  ;(data || []).forEach((item) => {
    const tgl = new Date(item.transaction_date).getDate()
    if (!dailyMap[tgl]) dailyMap[tgl] = 0
    dailyMap[tgl] += Number(item.total)
  })
  const daily_summary = Object.entries(dailyMap).map(([tgl, total]) => ({
    tanggal: String(tgl),
    total,
  }))

  // Hitung top_products
  const prodMap = {}
  ;(data || []).forEach((item) => {
    const key = item.product_name
    if (!prodMap[key]) prodMap[key] = { nama_produk: key, total_terjual: 0, total_pendapatan: 0 }
    prodMap[key].total_terjual   += Number(item.quantity)
    prodMap[key].total_pendapatan += Number(item.total)
  })
  const top_products = Object.values(prodMap)
    .sort((a, b) => b.total_terjual - a.total_terjual)
    .slice(0, 5)

  return {
    total_pemasukan:  summary.total_revenue,
    total_transaksi:  summary.total_transactions,
    rata_rata_harian: summary.total_revenue
      ? Math.round(summary.total_revenue / new Date(tahun, bulan, 0).getDate())
      : 0,
    daily_summary,
    top_products,
  }
}
