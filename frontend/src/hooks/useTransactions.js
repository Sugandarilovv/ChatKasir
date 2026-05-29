import { useState, useEffect } from 'react'
import { getTransactions } from '../services/transactionService'

export function useTransactions(tanggal) {
  const [data,    setData]    = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  async function fetchData() {
    setLoading(true)
    setError(null)
    try {
      const res = await getTransactions({ tanggal })
      // getTransactions sudah mapping ke { id, nama_produk, jumlah, harga }
      setData(res.transactions || [])
    } catch {
      setError('Gagal memuat data transaksi. Coba lagi.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [tanggal])

  return { data, loading, error, refetch: fetchData }
}
