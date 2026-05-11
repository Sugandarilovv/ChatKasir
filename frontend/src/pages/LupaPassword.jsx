import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function LupaPassword() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [email, setEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [newPass, setNewPass] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)
  
  const [timer, setTimer] = useState(30)
  const [canResend, setCanResend] = useState(false)

  useEffect(() => {
    let interval;
    if (step === 2 && timer > 0) {
      interval = setInterval(() => {
        setTimer((prev) => prev - 1)
      }, 1000)
    } else if (timer === 0) {
      setCanResend(true)
    }
    return () => clearInterval(interval)
  }, [step, timer])

  // Logika baru untuk tombol kembali
  function handleBack(e) {
    e.preventDefault()
    if (step > 1) {
      setStep(1) // Kembali ke tahap email
      setTimer(30)
    } else {
      navigate('/login') // Kembali ke halaman login
    }
  }

  function handleKirimEmail(e) {
    e.preventDefault()
    if (!email) return toast.error('Masukkan email terlebih dahulu')
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      setStep(2)
      setTimer(10)
      setCanResend(false)
      toast.success('Kode pemulihan dikirim ke email Anda!')
    }, 1500)
  }

  function handleKirimUlang() {
    setTimer(10)
    setCanResend(false)
    toast.success('Kode OTP baru telah dikirim.')
  }

  function handleVerifikasiOTP(e) {
    e.preventDefault()
    if (otp.length < 4) return toast.error('Masukkan kode OTP yang valid')
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      setStep(3)
      toast.success('Kode diverifikasi. Silakan buat sandi baru.')
    }, 1500)
  }

  function handleSimpanPassword(e) {
    e.preventDefault()
    if (newPass.length < 8) return toast.error('Sandi minimal 8 karakter')
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      toast.success('Sandi berhasil diperbarui! Silakan login.')
      navigate('/login')
    }, 1500)
  }

  const eyeOpen = <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
  const eyeClosed = <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>

  return (
    <div className="min-h-screen flex items-center justify-center font-sans p-6 bg-[linear-gradient(180deg,#f0fff8_0%,#e8faf2_50%,#f0fdf9_100%)]">
      <div className="w-full max-w-md bg-white rounded-3xl p-8 shadow-sm border border-gray-200 animate-fade-up">
        
        <div className="mb-8">
          <button onClick={handleBack} type="button" className="inline-flex items-center text-sm font-semibold text-gray-400 hover:text-green-600 mb-6 transition-colors">
            ← {step > 1 ? 'Kembali' : 'Kembali'}
          </button>
          <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight mb-2">Pemulihan Akun</h2>
          <p className="text-gray-500 text-sm font-medium">
            {step === 1 && 'Masukkan email yang terdaftar pada akun Anda.'}
            {step === 2 && `Masukkan kode yang kami kirim ke ${email}`}
            {step === 3 && 'Buat kata sandi baru untuk akun Anda.'}
          </p>
        </div>

        {step === 1 && (
          <form onSubmit={handleKirimEmail} className="space-y-5 animate-fade-in">
            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">Email Terdaftar</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="contoh@umkm.com"
                className="w-full px-4 py-3 rounded-xl text-sm outline-none border border-gray-200 bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/10 transition-all" autoFocus />
            </div>
            <button type="submit" disabled={loading} className="w-full py-3.5 rounded-xl font-bold text-white text-sm bg-green-600 hover:bg-green-700 transition-all disabled:opacity-70 flex justify-center">
              {loading ? 'Mengirim...' : 'Kirim Kode Pemulihan'}
            </button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={handleVerifikasiOTP} className="space-y-5 animate-fade-in">
            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">Kode OTP</label>
              <input type="text" value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="Misal: 123456" maxLength={6}
                className="w-full px-4 py-3 rounded-xl text-sm tracking-widest text-center outline-none border border-gray-200 bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/10 transition-all font-bold" autoFocus />
            </div>
            <button type="submit" disabled={loading} className="w-full py-3.5 rounded-xl font-bold text-white text-sm bg-green-600 hover:bg-green-700 transition-all disabled:opacity-70 flex justify-center">
              {loading ? 'Memeriksa...' : 'Verifikasi Kode'}
            </button>
            <div className="text-center mt-4">
              {canResend ? (
                <button type="button" onClick={handleKirimUlang} className="text-sm font-bold text-green-600 hover:text-green-700 transition-colors">
                  Kirim Ulang Kode
                </button>
              ) : (
                <p className="text-sm text-gray-400 font-medium">Kirim ulang dalam <span className="font-bold text-gray-600">{timer}s</span></p>
              )}
            </div>
          </form>
        )}

        {step === 3 && (
          <form onSubmit={handleSimpanPassword} className="space-y-5 animate-fade-in">
            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">Kata Sandi Baru</label>
              <div className="relative">
                {/* Penambahan [&::-ms-reveal]:hidden untuk menyembunyikan ikon mata Edge */}
                <input type={showPass ? 'text' : 'password'} value={newPass} onChange={(e) => setNewPass(e.target.value)} placeholder="Minimal 8 karakter"
                  className="w-full pl-4 pr-12 py-3 rounded-xl text-sm outline-none border [&::-ms-reveal]:hidden [&::-ms-clear]:hidden border-gray-200 bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/10 transition-all" autoFocus />
                <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-gray-600">
                  {showPass ? eyeClosed : eyeOpen}
                </button>
              </div>
            </div>
            <button type="submit" disabled={loading} className="w-full py-3.5 rounded-xl font-bold text-white text-sm bg-green-600 hover:bg-green-700 transition-all disabled:opacity-70 flex justify-center">
              {loading ? 'Menyimpan...' : 'Simpan Sandi Baru'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}