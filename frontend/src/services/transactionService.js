import api from './axiosInstance'

const USE_MOCK = true

const MOCK_TRANSACTIONS = [
  { id: 1, nama_produk: 'Nasi Goreng Spesial', jumlah: 2, harga: 18000 },
  { id: 2, nama_produk: 'Es Teh Manis',        jumlah: 3, harga: 5000  },
  { id: 3, nama_produk: 'Ayam Bakar',          jumlah: 1, harga: 25000 },
  { id: 4, nama_produk: 'Mie Goreng',          jumlah: 2, harga: 15000 },
  { id: 5, nama_produk: 'Jus Alpukat',         jumlah: 1, harga: 12000 },
]

// Generate 30 hari data mock agar chart bisa scroll penuh
const daily30 = Array.from({ length: 30 }, (_, i) => ({
  tanggal: String(i + 1),
  total: Math.floor(50000 + Math.random() * 150000 + Math.sin(i * 0.7) * 40000),
}))

const totalBulan    = daily30.reduce((s, d) => s + d.total, 0)
const rataRataHarian = Math.round(totalBulan / daily30.length)

const MOCK_REPORT = {
  total_pemasukan:  totalBulan,
  total_transaksi:  47,
  rata_rata_harian: rataRataHarian,
  daily_summary: daily30,
  top_products: [
    { nama_produk: 'Nasi Goreng Spesial', total_terjual: 28, total_pendapatan: 504000 },
    { nama_produk: 'Ayam Bakar',          total_terjual: 19, total_pendapatan: 475000 },
    { nama_produk: 'Mie Goreng',          total_terjual: 22, total_pendapatan: 330000 },
    { nama_produk: 'Es Teh Manis',        total_terjual: 35, total_pendapatan: 175000 },
    { nama_produk: 'Jus Alpukat',         total_terjual: 12, total_pendapatan: 144000 },
  ],
}

export async function saveTransactions(items) {
  if (USE_MOCK) return { message: 'Tersimpan (mock)', items }
  const res = await api.post('/transactions', { items })
  return res.data
}

export async function getTransactions({ tanggal, page = 1, limit = 20 } = {}) {
  if (USE_MOCK) return { transactions: MOCK_TRANSACTIONS }
  const params = { page, limit }
  if (tanggal) params.tanggal = tanggal
  const res = await api.get('/transactions', { params })
  return res.data
}

export async function getMonthlyReport(bulan, tahun) {
  if (USE_MOCK) return MOCK_REPORT
  const res = await api.get('/report/monthly', { params: { bulan, tahun } })
  return res.data
}