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
    const mockUser  = { id: 'mock-id', nama: 'User Mock', email, foto: null }
    localStorage.setItem('token', mockToken)
    localStorage.setItem('user', JSON.stringify(mockUser))
    return { token: mockToken, user: mockUser }
  }

  try {
    // 1. Login → dapat token & user_id
    const res = await api.post('/auth/login', { email, password })
    const { token, user_id } = res.data

    // Simpan token dulu supaya request berikutnya bisa pakai Bearer
    localStorage.setItem('token', token)

    // 2. Ambil full_name dari tabel users pakai token yang baru dapat
    let full_name = ''
    let avatar_url = null
    try {
      const profileRes = await api.get('/users/profile')
      full_name  = profileRes.data?.data?.full_name  || ''
      avatar_url = profileRes.data?.data?.avatar_url || null
    } catch (_) {
      // Kalau gagal ambil profil, tetap lanjut login
    }

    // 3. Simpan semua info user ke localStorage
    const userObj = {
      id:    user_id,
      email,
      nama:  full_name,
      foto:  avatar_url,
    }
    localStorage.setItem('user', JSON.stringify(userObj))
    return res.data
  } catch (err) {
    // PERBAIKAN: Memastikan error dari backend diteruskan dengan benar ke Login.jsx
    // Jika tidak ada response (server down), buatkan objek error standar
    if (!err.response) {
      throw { response: { data: { message: 'Server tidak merespon, periksa koneksi Anda.' } } };
    }
    throw err;
  }
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

export async function updatePassword(accessToken, refreshToken, password) {
  const res = await api.put('/auth/update-password', {
    access_token:  accessToken,
    refresh_token: refreshToken,
    new_password:  password,
  })
  return res.data
}

export async function updateProfile(nama, foto) {
  const payload = {}
  if (nama  !== undefined) payload.full_name  = nama
  if (foto  !== undefined) payload.avatar_url = foto

  const res = await api.put('/users/profile', payload)

  const current = getCurrentUser() || {}
  const updated = {
    ...current,
    nama: nama  !== undefined ? nama  : current.nama,
    foto: foto  !== undefined ? foto  : current.foto,
  }
  localStorage.setItem('user', JSON.stringify(updated))
  return res.data
}