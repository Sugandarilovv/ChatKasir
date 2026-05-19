import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, register, logout } from '../services/authService'
import { showToast } from '../components/ui/Toast'

export function useAuth() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  // Helper untuk membaca format error dari backend Reihan
  function getErrorMessage(err) {
    const data = err.response?.data
    if (!data) return 'Terjadi kesalahan jaringan.'
    
    // Error dari express-validator (contoh: password kurang dari 6 karakter)
    if (data.errors && data.errors.length > 0) return data.errors[0].msg
    
    // Error bawaan dari Supabase
    if (data.error) return data.error
    
    return data.message || 'Terjadi kesalahan.'
  }

  async function handleLogin(email, password) {
    setLoading(true)
    try {
      await login(email, password)
      showToast('Berhasil masuk!', 'success')
      navigate('/dashboard')
    } catch (err) {
      showToast(getErrorMessage(err), 'error')
    } finally { setLoading(false) }
  }

  async function handleRegister(nama, email, password) {
    setLoading(true)
    try {
      await register(nama, email, password)
      showToast('Registrasi berhasil! Silakan cek email untuk kode OTP.', 'success')
      navigate('/login') // Bisa diubah ke /konfirmasi-otp jika halaman OTP sudah siap
    } catch (err) {
      showToast(getErrorMessage(err), 'error')
    } finally { setLoading(false) }
  }

  function handleLogout() {
    logout()
    showToast('Berhasil keluar.', 'info')
    navigate('/login')
  }

  return { loading, handleLogin, handleRegister, handleLogout }
}