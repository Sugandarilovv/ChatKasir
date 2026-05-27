import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { forgotPassword, updatePassword } from '../services/authService'
import { showToast } from '../components/ui/Toast' // Pakai Toast bawaan ChatKasir

export default function LupaPassword() {
  const navigate = useNavigate()
  const location = useLocation()
  
  const [step, setStep] = useState(1) 
  const [email, setEmail] = useState('')
  const [newPass, setNewPass] = useState('')
  const [confirmPass, setConfirmPass] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)
  const [showConfirmPass, setShowConfirmPass] = useState(false)
  
  const [recoveryToken, setRecoveryToken] = useState('')
  const [refreshToken, setRefreshToken] = useState('') 

  useEffect(() => {
    const hash = window.location.hash
    if (hash) {
      const params = new URLSearchParams(hash.replace('#', '?'))
      const accessToken = params.get('access_token')
      const refToken = params.get('refresh_token') 
      const type = params.get('type')

      if (accessToken && refToken && type === 'recovery') {
        setRecoveryToken(accessToken)
        setRefreshToken(refToken) 
        setStep(3)
        window.history.replaceState(null, '', location.pathname)
      }
    }
  }, [location])

  function handleBack(e) {
    e.preventDefault()
    navigate('/login') 
  }

  async function handleKirimEmailReset(e) {
    e.preventDefault()
    if (!email) return showToast('Masukkan email terlebih dahulu', 'error')
    
    setLoading(true)
    try {
      await forgotPassword(email)
      setStep(2) 
    } catch (err) {
      showToast(err.response?.data?.error || err.message || 'Gagal mengirim link pemulihan.', 'error')
    } finally {
      setLoading(false)
    }
  }

  async function handleSimpanPassword(e) {
    e.preventDefault()
    
    if (newPass.length < 8) return showToast('Sandi minimal 8 karakter', 'error')
    if (newPass !== confirmPass) return showToast('Konfirmasi kata sandi tidak cocok', 'error')
    if (!recoveryToken) return showToast('Token tidak valid. Silakan ulangi proses dari awal.', 'error')

    setLoading(true)
    try {
      await updatePassword(recoveryToken, refreshToken, newPass)
      showToast('Password berhasil diubah! Silakan masuk.', 'success')
      
      // PERBAIKAN: Beri jeda 2 detik agar Pop-Up sempat terbaca user
      setTimeout(() => {
        navigate('/login')
      }, 2000)
      
    } catch (err) {
      showToast(err.response?.data?.error || err.message || 'Gagal mengubah password.', 'error')
      setLoading(false) // Matikan loading hanya jika error. Jika sukses, biarkan tombol loading agar user tidak klik 2x.
    } 
  }

  // Ikon disesuaikan agar lebih rapi untuk desain baru
  const eyeOpen = <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
  const eyeClosed = <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
  const mailIcon = <svg className="w-10 h-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>

  return (
    <div className="min-h-screen flex items-center justify-center font-sans p-6 bg-[linear-gradient(180deg,#f0fff8_0%,#e8faf2_50%,#f0fdf9_100%)]">
      <div className="w-full max-w-md bg-white rounded-3xl p-8 shadow-sm border border-gray-200 animate-fade-up">
        
        {step !== 2 && (
          <div className="mb-8">
            {step === 1 && (
              <button onClick={handleBack} type="button" className="inline-flex items-center text-sm font-semibold text-gray-400 hover:text-green-600 mb-6 transition-colors">
                ← Kembali
              </button>
            )}
            <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight mb-2">Pemulihan Akun</h2>
            <p className="text-gray-500 text-sm font-medium">
              {step === 1 && 'Masukkan email yang terdaftar pada akun Anda.'}
              {step === 3 && 'Buat kata sandi baru untuk akun Anda.'}
            </p>
          </div>
        )}

        {/* LANGKAH 1: INPUT EMAIL */}
        {step === 1 && (
          <form onSubmit={handleKirimEmailReset} className="space-y-5 animate-fade-in">
            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">Email Terdaftar</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="contoh@umkm.com"
                className="w-full px-4 py-3 rounded-xl text-sm outline-none border border-gray-200 bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/10 transition-all" autoFocus />
            </div>
            <button type="submit" disabled={loading} className="w-full py-3.5 rounded-xl font-bold text-white text-sm bg-green-600 hover:bg-green-700 transition-all disabled:opacity-70 flex justify-center cursor-pointer">
              {loading ? 'Mengirim...' : 'Kirim Link Pemulihan'}
            </button>
          </form>
        )}

        {/* LANGKAH 2: PEMBERITAHUAN CEK EMAIL (Didesain Ulang) */}
        {step === 2 && (
          <div className="text-center animate-fade-in py-6">
            <div className="w-20 h-20 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-6">
              {mailIcon}
            </div>
            <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight mb-3">Cek Kotak Masuk Anda</h2>
            <p className="text-gray-500 text-sm font-medium mb-8 leading-relaxed">
              Kami telah mengirimkan instruksi pemulihan ke <br/>
              <span className="font-bold text-gray-800 bg-green-50 px-2 py-1 rounded-md">{email}</span> <br/><br/>
              Silakan klik tautan di dalamnya untuk mengatur ulang kata sandi. Periksa juga folder <i>Spam</i> jika tidak menemukannya.
            </p>
            
            <a href="https://mail.google.com" target="_blank" rel="noopener noreferrer"
               className="w-full py-3.5 mb-4 rounded-xl font-bold text-white text-sm bg-green-600 hover:bg-green-700 transition-all flex justify-center items-center gap-2 cursor-pointer shadow-sm">
               Buka Aplikasi Gmail
            </a>

            <button onClick={handleBack} type="button" className="text-sm font-semibold text-gray-400 hover:text-green-600 transition-colors">
              Kembali ke Halaman Login
            </button>
          </div>
        )}

        {/* LANGKAH 3: INPUT PASSWORD BARU */}
        {step === 3 && (
          <form onSubmit={handleSimpanPassword} className="space-y-5 animate-fade-in">
            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">Kata Sandi Baru</label>
              <div className="relative">
                <input type={showPass ? 'text' : 'password'} value={newPass} onChange={(e) => setNewPass(e.target.value)} placeholder="Minimal 8 karakter"
                  className="w-full pl-4 pr-12 py-3 rounded-xl text-sm outline-none border [&::-ms-reveal]:hidden [&::-ms-clear]:hidden border-gray-200 bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/10 transition-all" autoFocus />
                <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-gray-600">
                  {showPass ? eyeClosed : eyeOpen}
                </button>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">Konfirmasi Kata Sandi Baru</label>
              <div className="relative">
                <input type={showConfirmPass ? 'text' : 'password'} value={confirmPass} onChange={(e) => setConfirmPass(e.target.value)} placeholder="Ketik ulang kata sandi baru"
                  className="w-full pl-4 pr-12 py-3 rounded-xl text-sm outline-none border [&::-ms-reveal]:hidden [&::-ms-clear]:hidden border-gray-200 bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/10 transition-all" />
                <button type="button" onClick={() => setShowConfirmPass(!showConfirmPass)} className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-gray-600">
                  {showConfirmPass ? eyeClosed : eyeOpen}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading} className="w-full py-3.5 mt-2 rounded-xl font-bold text-white text-sm bg-green-600 hover:bg-green-700 transition-all disabled:opacity-70 flex justify-center cursor-pointer shadow-sm">
              {loading ? 'Menyimpan...' : 'Ubah Password'}
            </button>
          </form>
        )}

      </div>
    </div>
  )
}