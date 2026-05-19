import api from './axiosInstance'

// Dimatikan karena backend Reihan sudah jalan di Vercel
const USE_MOCK = false

export async function register(nama, email, password) {
  if (USE_MOCK) {
    return { message: 'Akun berhasil dibuat (mock)' }
  }
  // Mapping 'nama' dari frontend menjadi 'full_name' untuk backend
  const res = await api.post('/auth/register', { full_name: nama, email, password })
  return res.data
}

export async function login(email, password) {
  if (USE_MOCK) {
    const mockToken = 'mock-jwt-token-123'
    const mockUser  = { nama: 'Alfan (Mock)', email }
    localStorage.setItem('token', mockToken)
    localStorage.setItem('user', JSON.stringify(mockUser))
    return { token: mockToken, user: mockUser }
  }
  const res = await api.post('/auth/login', { email, password })
  const { token, user_id } = res.data
  
  localStorage.setItem('token', token)
  // Simpan user_id dari respons backend
  localStorage.setItem('user', JSON.stringify({ id: user_id, email }))
  return res.data
}

export function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

export function getCurrentUser() {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

// FUNGSI BARU UNTUK LUPA PASSWORD
export async function forgotPassword(email) {
  const res = await api.post('/auth/forgot-password', { email })
  return res.data
}

export async function updatePassword(password) {
  const res = await api.put('/auth/update-password', { password })
  return res.data
}