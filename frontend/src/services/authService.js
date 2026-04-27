import api from './axiosInstance'

// Ganti jadi false kalau backend Reihan sudah jalan
const USE_MOCK = true

export async function register(nama, email, password) {
  if (USE_MOCK) {
    // Simulasi register berhasil
    return { message: 'Akun berhasil dibuat (mock)' }
  }
  const res = await api.post('/auth/register', { nama, email, password })
  return res.data
}

export async function login(email, password) {
  if (USE_MOCK) {
    // Simulasi login berhasil — simpan token dummy
    const mockToken = 'mock-jwt-token-123'
    const mockUser  = { nama: 'Alfan (Mock)', email }
    localStorage.setItem('token', mockToken)
    localStorage.setItem('user', JSON.stringify(mockUser))
    return { token: mockToken, user: mockUser }
  }
  const res = await api.post('/auth/login', { email, password })
  const { token, user } = res.data
  localStorage.setItem('token', token)
  localStorage.setItem('user', JSON.stringify(user))
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