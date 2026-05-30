import api from './axiosInstance'

export async function predictFromChat(teks) {
  try {
    const res = await api.post('/transactions/analyze', { raw_text: teks })
    return res.data
  } catch (err) {
    const status = err.response?.status
    const msg = err.response?.data?.error || ''

    if (status === 422) {
      throw { response: { data: { detail: 'AI tidak bisa membaca teks ini. Coba tulis lebih jelas.' } } }
    }
    if (status === 401) {
      throw { response: { data: { detail: 'Sesi habis, silakan login ulang.' } } }
    }
    if (status === 500 || !err.response) {
      throw { response: { data: { detail: 'Server AI sedang tidak tersedia. Coba beberapa saat lagi.' } } }
    }
    throw { response: { data: { detail: msg || 'Gagal memproses teks. Coba lagi.' } } }
  }
}

export async function tanyaAI(history, newMessage) {
  try {
    // Tembak ke endpoint backend Express Anda (sesuaikan URL-nya jika berbeda)
    const res = await api.post('/tanya-ai', {
      history: history,
      message: newMessage
    })
    return res.data.reply
  } catch (err) {
    console.error("Gagal menghubungi AI:", err)
    throw new Error("Maaf, terjadi kesalahan saat menghubungi AI. Silakan coba lagi.")
  }
}