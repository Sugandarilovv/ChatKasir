import axios from 'axios'

const api = axios.create({
  // Menyesuaikan base URL sesuai informasi yang kamu berikan
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://chat-kasir-backend.vercel.app',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // PERBAIKAN: Hanya paksa refresh atau lempar ke halaman login
      // JIKA posisi pengguna saat ini BUKAN di halaman /login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api