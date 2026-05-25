import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import toast from 'react-hot-toast'

// IMPORT GAMBAR LOGO
import logoImg from '../assets/logo.png' 

const STATS = [
  { label: 'UMKM aktif', value: '2.4rb+' },
  { label: 'Transaksi', value: '18rb+' },
  { label: 'Akurasi AI', value: '≥85%' },
]

export default function Login() {
  const { loading, handleLogin } = useAuth()
  const { register, handleSubmit, setError, clearErrors, formState: { errors } } = useForm()
  const [showPass, setShowPass] = useState(false)

  async function onSubmit(data) { 
    clearErrors('email')
    clearErrors('password')

    try {
      await handleLogin(data.email, data.password)
    } catch (error) {
      if (error.response) {
        const status = error.response.status;
        const serverPesan = error.response.data?.message || error.response.data?.error || '';
        const lowerPesan = String(serverPesan).toLowerCase();

        // LOGIKA BARU: Jika status 401, beri pesan di KEDUA kolom agar user tidak bingung
        if (status === 401) {
          const pesan = 'Email atau password salah. Silakan periksa kembali.';
          setError('email', { type: 'manual', message: pesan });
          setError('password', { type: 'manual', message: pesan });
        } 
        // Jika 404, sudah benar diarahkan ke email
        else if (status === 404) {
          setError('email', { type: 'manual', message: 'Email tidak terdaftar.' });
        }
        else {
          // Fallback umum
          toast.error(serverPesan || 'Terjadi kesalahan.', { duration: 3500 });
        }
      } else {
        toast.error('Gagal terhubung ke server.', { duration: 3500 });
      }
    }
  }

  return (
    <div className="flex flex-col lg:flex-row min-h-dvh bg-linear-to-b from-[#f0fff8] via-[#e8faf2] to-[#f0fdf9] font-sans w-full">
      
      <div className="flex flex-col w-full lg:w-5/12 xl:w-120 shrink-0 relative bg-green-950 overflow-hidden shadow-xl z-10">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-green-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>
        <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-emerald-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"></div>

        <div className="relative z-10 flex flex-col h-full p-8 xl:p-12">
          <div className="flex items-center gap-3 mb-8 lg:mb-auto">
            <img 
              src={logoImg} 
              alt="Logo ChatKasir" 
              className="w-10 h-10 rounded-lg shadow-lg shadow-green-500/30 object-contain" 
            />
            <span className="text-white font-extrabold text-2xl tracking-tight">ChatKasir.</span>
          </div>

          <div className="mb-8 lg:mt-auto lg:mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/10 border border-white/20 backdrop-blur-sm mb-6">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
              <span className="text-green-50 text-xs font-semibold tracking-wide">Sistem Pintar UMKM</span>
            </div>
            <h1 className="text-3xl xl:text-4xl font-extrabold text-white leading-tight mb-4">
              Kelola kasir <br />
              <span className="text-transparent bg-clip-text bg-linear-to-r from-green-300 to-emerald-200">tanpa ribet.</span>
            </h1>
            <p className="text-green-100/80 text-sm xl:text-base leading-relaxed max-w-sm">
              Ubah chat pelanggan menjadi catatan transaksi akurat dalam hitungan detik menggunakan AI.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-2 xl:gap-4 p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
            {STATS.map((s) => (
              <div key={s.label} className="text-center">
                <p className="text-white text-lg xl:text-xl font-bold">{s.value}</p>
                <p className="text-green-200/70 text-xs mt-1 font-medium">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col justify-center p-6 sm:p-10 md:p-12 bg-transparent">
        <div className="w-full max-w-md mx-auto my-4 lg:my-auto animate-fade-up">
          
          <div className="mb-6">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight mb-2">Selamat Datang 👋</h2>
            <p className="text-gray-500 text-sm font-medium">Masuk untuk mengelola transaksi UMKM Anda.</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">Email Akses</label>
              <input type="email" placeholder="contoh@umkm.com" autoComplete="email"
                className={`w-full px-4 py-3 rounded-xl text-sm transition-all outline-none border ${errors.email ? 'border-red-300 bg-red-50 focus:border-red-500 focus:ring-4 focus:ring-red-500/10' : 'border-gray-200 bg-white/80 focus:bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/10'}`}
                {...register('email', { required: 'Email wajib diisi', pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Format tidak valid' } })} />
              {errors.email && <p className="text-red-500 text-xs font-medium pl-1">{errors.email.message}</p>}
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700">Password</label>
              <div className="relative">
                <input type={showPass ? 'text' : 'password'} placeholder="••••••••" autoComplete="current-password"
                  className={`w-full pl-4 pr-12 py-3 rounded-xl text-sm transition-all outline-none border [&::-ms-reveal]:hidden [&::-ms-clear]:hidden ${errors.password ? 'border-red-300 bg-red-50 focus:border-red-500 focus:ring-4 focus:ring-red-500/10' : 'border-gray-200 bg-white/80 focus:bg-white focus:border-green-500 focus:ring-4 focus:ring-green-500/10'}`}
                  {...register('password', { required: 'Password wajib diisi' })} />
                <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-gray-600 rounded-lg focus:outline-none">
                  {showPass ? (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                  )}
                </button>
              </div>
              {errors.password && <p className="text-red-500 text-xs font-medium pl-1">{errors.password.message}</p>}
            </div>

            <div className="flex justify-end pt-1">
              <Link to="/lupa-password" className="text-xs font-semibold text-green-600 hover:text-green-700">Lupa password?</Link>
            </div>

            <button type="submit" disabled={loading}
              className="w-full py-3 mt-1 rounded-xl font-bold text-white text-sm transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-70 flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700">
              {loading ? 'Memproses...' : 'Masuk ke Sistem'}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-gray-200/60 text-center space-y-2">
            <p className="text-gray-600 text-sm font-medium">
              Belum punya akun?{' '}
              <Link to="/register" className="text-green-600 font-bold hover:text-green-700 transition-colors">
                Buat akun gratis
              </Link>
            </p>
            <p className="text-gray-400 text-xs font-medium">
              &copy; 2026 ChatKasir · Capstone Project
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}