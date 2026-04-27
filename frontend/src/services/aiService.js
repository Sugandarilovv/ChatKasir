import axios from 'axios'

const USE_MOCK = true

const aiApi = axios.create({
  baseURL: import.meta.env.VITE_AI_API_URL || 'http://localhost:8000',
  timeout: 15000,
})

export async function predictFromChat(teks) {
  if (USE_MOCK) {
    // Simulasi delay AI 1 detik
    await new Promise((r) => setTimeout(r, 1000))
    // Hasil ekstraksi dummy berdasarkan teks apapun
    return {
      status: 'success',
      results: [
        { nama_produk: 'Nasi Goreng Spesial', jumlah: 2, harga: 18000 },
        { nama_produk: 'Es Teh Manis',        jumlah: 1, harga: 5000  },
      ],
    }
  }
  const res = await aiApi.post('/predict', { text: teks })
  return res.data
}