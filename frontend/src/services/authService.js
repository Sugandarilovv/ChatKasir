import api from './axiosInstance'

const USE_MOCK = false

export async function register(nama, email, password) {
  if (USE_MOCK) return { message: 'Akun berhasil dibuat (mock)' }
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

export async function forgotPassword(email) {
  const res = await api.post('/auth/forgot-password', { email })
  return res.data
}

// PERBAIKAN: Tambahkan parameter refreshToken
export async function updatePassword(accessToken, refreshToken, password) {
  const res = await api.put('/auth/update-password', { 
    access_token: accessToken, 
    refresh_token: refreshToken, // Kirim ke backend
    new_password: password 
  })
  return res.data
}