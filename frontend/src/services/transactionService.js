import api from './axiosInstance'

// ── Simpan transaksi yang sudah dikonfirmasi user ────────────────────────────
export async function saveTransactions(extractionId, products) {
  const res = await api.post('/transactions', {
    extraction_id: extractionId,
    products,
  })
  return res.data
}

// ── Ambil transaksi harian untuk Dashboard ───────────────────────────────────
// Backend GET /transactions/report?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD
// WAJIB kirim kedua param, kalau tidak backend return 400
export async function getTransactions({ tanggal } = {}) {
  const today = tanggal || new Date().toISOString().split('T')[0]

  const res = await api.get('/transactions/report', {
    params: { startDate: today, endDate: today },
  })

  // Backend kembalikan: { summary, chart_data, top_products, transactions }
  // transactions: [{ id, product_name, quantity, price_satuan, total, ... }]
  const transactions = (res.data.transactions || []).map((t) => ({
    id:            t.id,
    extraction_id: t.extraction_id,
    nama_produk:   t.product_name,
    jumlah:        Number(t.quantity),
    harga:         Number(t.price_satuan),
    total:         Number(t.total),
  }))

  return { transactions }
}

// ── Laporan bulanan untuk halaman Laporan ────────────────────────────────────
// Backend GET /report/monthly?month=M&year=YYYY
// Backend kembalikan: { summary: { total_revenue, total_items_sold, total_transactions }, data }
// data: [{ product_name, quantity, total, transaction_date }]
export async function getMonthlyReport(bulan, tahun) {
  const res = await api.get('/report/monthly', {
    params: { month: bulan, year: tahun },
  })

  const { summary, data } = res.data

  // Hitung daily_summary dari array data transaksi
  const dailyMap = {}
  ;(data || []).forEach((item) => {
    // transaction_date format: "YYYY-MM-DD" → ambil tanggal (hari)
    const tgl = new Date(item.transaction_date + 'T00:00:00').getDate()
    if (!dailyMap[tgl]) dailyMap[tgl] = 0
    dailyMap[tgl] += Number(item.total)
  })
  const daily_summary = Object.entries(dailyMap)
    .sort((a, b) => Number(a[0]) - Number(b[0]))
    .map(([tgl, total]) => ({ tanggal: String(tgl), total }))

  // Hitung top_products dari array data transaksi
  // Laporan.jsx pakai: p.nama_produk, p.total_terjual, p.total_pendapatan
  const prodMap = {}
  ;(data || []).forEach((item) => {
    const key = item.product_name
    if (!prodMap[key]) prodMap[key] = { nama_produk: key, total_terjual: 0, total_pendapatan: 0 }
    prodMap[key].total_terjual    += Number(item.quantity)
    prodMap[key].total_pendapatan += Number(item.total)
  })
  const top_products = Object.values(prodMap)
    .sort((a, b) => b.total_terjual - a.total_terjual)
    .slice(0, 5)

  // Rata-rata harian = total revenue / jumlah hari yang BENAR-BENAR ada transaksi
  const hariAdaTransaksi = Object.keys(dailyMap).length || 1

  return {
    total_pemasukan:  Number(summary.total_revenue   || 0),
    total_transaksi:  Number(summary.total_transactions || 0),
    rata_rata_harian: summary.total_revenue
      ? Math.round(Number(summary.total_revenue) / hariAdaTransaksi)
      : 0,
    daily_summary,
    top_products,
  }
}
