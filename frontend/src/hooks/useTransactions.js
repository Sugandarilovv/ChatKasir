import { useState, useEffect, useCallback } from 'react'
import { getTransactions } from '../services/transactionService'

export function useTransactions(tanggal) {
  const [data,    setData]    = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getTransactions({ tanggal })
      setData(res.transactions || [])
    } catch (err) {
      const msg = err.response?.data?.error || 'Gagal memuat data transaksi.'
      setError(msg)
      setData([])
    } finally {
      setLoading(false)
    }
  }, [tanggal])

  useEffect(() => { fetchData() }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}
