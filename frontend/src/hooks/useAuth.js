import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, register, logout } from '../services/authService'
import { showToast } from '../components/ui/Toast'

export function useAuth() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleLogin(email, password) {
    setLoading(true)
    try {
      await login(email, password)
      showToast('Berhasil masuk!', 'success')
      navigate('/dashboard')
    } catch (err) {
      showToast(err.response?.data?.message || 'Email atau password salah.', 'error')
    } finally { setLoading(false) }
  }

  async function handleRegister(nama, email, password) {
    setLoading(true)
    try {
      await register(nama, email, password)
      showToast('Akun berhasil dibuat.', 'success')
      navigate('/login')
    } catch (err) {
      showToast(err.response?.data?.message || 'Gagal membuat akun.', 'error')
    } finally { setLoading(false) }
  }

  function handleLogout() {
    logout()
    showToast('Berhasil keluar.', 'info')
    navigate('/login')
  }

  return { loading, handleLogin, handleRegister, handleLogout }
}