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
    const res = await api.post('/auth/login', { email, password })
    const { token, user_id } = res.data

    localStorage.setItem('token', token)

    let full_name = ''
    let avatar_url = null
    try {
      const profileRes = await api.get('/users/profile')
      full_name  = profileRes.data?.data?.full_name  || ''
      avatar_url = profileRes.data?.data?.avatar_url || null
    } catch (_) {}

    const userObj = { id: user_id, email, nama: full_name, foto: avatar_url }
    localStorage.setItem('user', JSON.stringify(userObj))
    return res.data
  } catch (err) {
    if (!err.response) {
      throw { response: { data: { message: 'Server tidak merespon, periksa koneksi Anda.' } } }
    }
    throw err
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

// ─── FORGOT PASSWORD ────────────────────────────────────────────────────────
// Langsung pakai Supabase JS client — tidak lewat backend
// Keuntungan: tidak bergantung pada SMTP/env backend, lebih reliable
export async function forgotPassword(email) {
  const { supabase } = await import('./supabaseClient')
  const redirectTo = `${window.location.origin}/lupa-password`

  const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo })

  if (error) {
    throw { response: { data: { error: error.message } } }
  }
  return { message: 'Link reset password sudah dikirim ke email kamu' }
}

// ─── UPDATE PASSWORD ─────────────────────────────────────────────────────────
// Restore session dari token recovery URL, lalu update password via Supabase
export async function updatePassword(accessToken, refreshToken, newPassword) {
  const { supabase } = await import('./supabaseClient')

  // 1. Restore session pakai token dari link di email
  const { error: sessionError } = await supabase.auth.setSession({
    access_token:  accessToken,
    refresh_token: refreshToken,
  })

  if (sessionError) {
    throw { response: { data: { error: 'Token tidak valid atau sudah kedaluwarsa. Ulangi proses dari awal.' } } }
  }

  // 2. Update password
  const { error } = await supabase.auth.updateUser({ password: newPassword })

  if (error) {
    throw { response: { data: { error: error.message } } }
  }

  // 3. Sign out agar sesi recovery bersih, user login ulang dengan password baru
  await supabase.auth.signOut()

  return { message: 'Password berhasil diperbarui' }
}

// ─── UPDATE PROFILE ──────────────────────────────────────────────────────────
export async function updateProfile(nama, foto) {
  const payload = {}
  if (nama !== undefined) payload.full_name  = nama
  if (foto !== undefined) payload.avatar_url = foto

  const res = await api.put('/users/profile', payload)

  const current = getCurrentUser() || {}
  const updated = {
    ...current,
    nama: nama !== undefined ? nama : current.nama,
    foto: foto !== undefined ? foto : current.foto,
  }
  localStorage.setItem('user', JSON.stringify(updated))
  return res.data
}

// ─── DELETE ACCOUNT ──────────────────────────────────────────────────────────
export async function deleteAccount() {
  // Backend route: DELETE /users/account (userRoutes.js)
  const res = await api.delete('/users/account')
  return res.data
}
