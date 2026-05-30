import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

// IMPORT GAMBAR LOGO
import logoImg from '../assets/logo.png' 

const FITUR = [
  { icon: '✨', title: 'Ekstraksi AI Akurat', desc: 'Sistem membaca pesanan otomatis' },
  { icon: '📈', title: 'Analitik Real-time',  desc: 'Pantau omset harian dan bulanan' },
  { icon: '🔒', title: 'Keamanan Data',       desc: 'Tersimpan aman dengan enkripsi' },
]

export default function Register() {
  const { loading, handleRegister } = useAuth()
  
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm()
  const [showPass, setShowPass]   = useState(false)
  const [showPass2, setShowPass2] = useState(false)

  const passwordValue = watch('password') || ''
  const confirmValue  = watch('konfirmasi') || ''
  const strength = getStrength(passwordValue)

  function onSubmit(data) { 
    handleRegister(data.nama, data.email, data.password) 
  }

  function generateStrongPassword() {
    const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    const numbers = "0123456789"
    const symbols = "!@#$%^&*"
    const all = letters + numbers + symbols
    
    let pass = ""
    pass += letters[Math.floor(Math.random() * letters.length)]
    pass += numbers[Math.floor(Math.random() * numbers.length)]
    pass += symbols[Math.floor(Math.random() * symbols.length)]
    
    for (let i = 0; i < 9; i++) {
      pass += all[Math.floor(Math.random() * all.length)]
    }
    
    pass = pass.split('').sort(() => 0.5 - Math.random()).join('')
    
    setValue('password', pass, { shouldValidate: true })
    setValue('konfirmasi', pass, { shouldValidate: true })
    
    setShowPass(true)
    setShowPass2(true)
  }

  const eyeOpen = <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
  const eyeClosed = <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>

  return (
    <div className="flex flex-col lg:flex-row min-h-dvh font-sans w-full">
      
      {/* Sisi Kiri (Terkunci Sempurna) */}
      <div className="flex flex-col w-full lg:w-5/12 xl:w-120 shrink-0 relative lg:sticky lg:top-0 lg:h-dvh bg-green-950 overflow-hidden">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-green-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
        <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-emerald-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>

        <div className="relative z-10 flex flex-col h-full p-8 xl:p-12">
          <div className="flex items-center gap-3 mb-8 lg:mb-auto">
            <img src={logoImg} alt="Logo ChatKasir" className="w-10 h-10 rounded-lg shadow-lg shadow-green-500/30 object-contain" />
            <span className="text-white font-extrabold text-2xl tracking-tight">ChatKasir.</span>
          </div>

          <div className="mb-8 lg:mt-auto lg:mb-10">
            <h1 className="text-3xl xl:text-4xl font-extrabold text-white leading-tight mb-4">
              Mulai digitalisasi <br />
              <span className="text-transparent bg-clip-text bg-linear-to-r from-green-300 to-emerald-200">bisnis Anda.</span>
            </h1>
            <p className="text-green-100/80 text-sm xl:text-base leading-relaxed max-w-sm">
              Bergabung dan rasakan mudahnya merekap keuangan UMKM. 100% Gratis.
            </p>
          </div>

          <div className="space-y-3 xl:space-y-4">
            {FITUR.map((f) => (
              <div key={f.title} className="flex items-start gap-4 p-3 xl:p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm transition-colors">
                <span className="text-2xl mt-0.5">{f.icon}</span>
                <div>
                  <p className="text-white text-sm font-bold">{f.title}</p>
                  <p className="text-green-200/70 text-xs mt-1 font-medium">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sisi Kanan (Form Registrasi) */}
      <div className="flex-1 flex flex-col justify-center p-6 sm:p-10 md:p-12 bg-[linear-gradient(180deg,#f0fff8_0%,#e8faf2_50%,#f0fdf9_100%)]">
        <div className="w-full max-w-md mx-auto my-4 lg:my-auto">

          <div className="mb-6">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight mb-2">Buat Akun Baru</h2>
            <p className="text-gray-500 text-sm font-medium">Lengkapi form di bawah untuk mulai menggunakan aplikasi.</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">Nama Lengkap</label>
              <input type="text" placeholder="Masukkan nama Anda"
                className={`w-full px-4 py-3 rounded-xl text-sm outline-none border ${errors.nama ? 'border-red-300 bg-red-50 focus:border-red-500 focus:ring-4' : 'border-green-200 bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/20'}`}
                {...register('nama', { required: 'Nama wajib diisi' })} />
              {errors.nama && <p className="text-red-500 text-xs font-medium pl-1">{errors.nama.message}</p>}
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">Email Akses</label>
              <input type="email" placeholder="contoh@umkm.com"
                className={`w-full px-4 py-3 rounded-xl text-sm outline-none border ${errors.email ? 'border-red-300 bg-red-50 focus:border-red-500 focus:ring-4' : 'border-green-200 bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/20'}`}
                {...register('email', { required: 'Email wajib diisi', pattern: { value: /^\S+@\S+$/i, message: 'Format email tidak valid' } })} />
              {errors.email && <p className="text-red-500 text-xs font-medium pl-1">{errors.email.message}</p>}
            </div>

            {/* AREA PASSWORD */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-end">
                <label className="text-sm font-semibold text-gray-700">Password</label>
                <button type="button" onClick={generateStrongPassword} className="text-xs font-bold text-green-600 hover:text-green-700 bg-green-50 px-2 py-1 rounded-md transition-colors flex items-center gap-1">
                  <span>✨</span> Rekomendasi Sandi Kuat
                </button>
              </div>
              <div className="relative">
                <input type={showPass ? 'text' : 'password'} placeholder="Minimal 6 karakter"
                  className={`w-full pl-4 pr-12 py-3 rounded-xl text-sm outline-none border [&::-ms-reveal]:hidden [&::-ms-clear]:hidden ${errors.password ? 'border-red-300 bg-red-50 focus:border-red-500 focus:ring-4' : 'border-green-200 bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/20'}`}
                  {...register('password', { required: 'Wajib diisi', minLength: { value: 6, message: 'Minimal 6 karakter' } })} />
                <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-green-600 transition-colors">
                  {showPass ? eyeClosed : eyeOpen}
                </button>
              </div>
              
              {/* === KOMENTAR PERBAIKAN 1 === */}
              {/* Class "h-5" diubah menjadi "h-2". Ini memangkas ruang transparan di bawah form password, 
                  sehingga form konfirmasi di bawahnya otomatis tertarik ke atas. */}
              <div className="h-2 mt-1 relative z-10">
                <div className={`absolute w-full transition-all duration-300 ease-in-out ${passwordValue.length > 0 ? 'opacity-100 visible' : 'opacity-0 invisible'}`}>
                  <div className="flex flex-col gap-1">
                    <div className="flex gap-1 h-1 w-full rounded-full overflow-hidden">
                      {[1, 2, 3].map((level) => (
                        <div key={level} className={`h-full flex-1 transition-all duration-300 ${strength >= level ? STRENGTH_COLORS[strength] : 'bg-green-200/40'}`} />
                      ))}
                    </div>
                    <p className={`text-[11px] leading-none font-medium pl-0.5 ${strength === 1 ? 'text-red-500' : strength === 2 ? 'text-yellow-600' : 'text-green-600'}`}>
                      Kekuatan: {STRENGTH_LABELS[strength]}
                    </p>
                  </div>
                </div>
              </div>
              
              {errors.password && <p className="text-red-500 text-xs font-medium pl-1">{errors.password.message}</p>}
            </div>

            {/* AREA KONFIRMASI PASSWORD */}
            {/* === KOMENTAR PERBAIKAN 2 === */}
            {/* Saya tambahkan class "-mt-1" (margin-top negatif) di sini untuk melawan jarak bawaan 
                dari form. Efeknya, input Ulangi Password akan melangkah naik mendekati indikator di atasnya. */}
            <div className="space-y-1.5 -mt-1 relative z-20">
              <label className="text-sm font-semibold text-gray-700">Ulangi Password</label>
              <div className="relative">
                <input type={showPass2 ? 'text' : 'password'} placeholder="Ketik ulang password"
                  className={`w-full pl-4 pr-12 py-3 rounded-xl text-sm outline-none border [&::-ms-reveal]:hidden [&::-ms-clear]:hidden ${errors.konfirmasi ? 'border-red-300 bg-red-50 focus:border-red-500 focus:ring-4' : 'border-green-200 bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/20'}`}
                  {...register('konfirmasi', { required: 'Wajib diisi', validate: (v) => v === watch('password') || 'Password tidak cocok' })} />
                <button type="button" onClick={() => setShowPass2(!showPass2)} className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-green-600 transition-colors">
                  {showPass2 ? eyeClosed : eyeOpen}
                </button>
              </div>

              {/* Ruang statis dikecilkan menjadi h-3 */}
              <div className="h-3 mt-1 relative z-10">
                <div className={`absolute w-full transition-all duration-300 ease-in-out ${confirmValue.length > 0 ? 'opacity-100 visible' : 'opacity-0 invisible'}`}>
                  <p className={`text-[11px] leading-none font-medium pl-1 ${passwordValue === confirmValue ? 'text-green-600' : 'text-red-500'}`}>
                    {passwordValue === confirmValue ? '✓ Kata sandi cocok' : '✗ Kata sandi tidak cocok dengan input sebelumnya'}
                  </p>
                </div>
              </div>
              
              {errors.konfirmasi && <p className="text-red-500 text-xs font-medium pl-1">{errors.konfirmasi.message}</p>}
            </div>

            <button type="submit" disabled={loading}
              className="w-full py-3 mt-4 rounded-xl font-bold text-white text-sm transition-all shadow-sm bg-green-600 hover:bg-green-700 flex items-center justify-center cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">
              {loading ? 'Memproses...' : 'Daftar Sekarang'}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-green-200/50 text-center space-y-2">
            <p className="text-gray-600 text-sm font-medium">
              Sudah mendaftar?{' '}
              <Link to="/login" className="text-green-600 font-bold hover:text-green-700 transition-colors">
                Masuk di sini
              </Link>
            </p>
            <p className="text-gray-400 text-xs font-medium">
              Dengan mendaftar, Anda menyetujui Ketentuan Layanan.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

// --- LOGIKA HITUNGAN KEKUATAN PASSWORD ---
const STRENGTH_LABELS = ['', 'Lemah', 'Sedang', 'Kuat']
const STRENGTH_COLORS = ['', 'bg-red-500', 'bg-yellow-500', 'bg-green-500']

function getStrength(pass) {
  if (!pass) return 0
  
  const hasLetter = /[a-zA-Z]/.test(pass)
  const hasNumber = /[0-9]/.test(pass)
  const hasSymbol = /[^a-zA-Z0-9]/.test(pass)

  const typesCount = (hasLetter ? 1 : 0) + (hasNumber ? 1 : 0) + (hasSymbol ? 1 : 0)

  if (typesCount === 1) return 1 
  if (typesCount === 2) return 2 
  if (typesCount === 3) return 3 
  
  return 0
}