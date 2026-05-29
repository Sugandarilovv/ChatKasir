import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ToastProvider }  from './components/ui/Toast'
import { ThemeProvider }  from './context/ThemeContext'
import Register      from './pages/Register'
import Login         from './pages/Login'
import LupaPassword  from './pages/LupaPassword'
import InputChat     from './pages/InputChat'
import Konfirmasi    from './pages/Konfirmasi'
import Dashboard     from './pages/Dashboard'
import Laporan       from './pages/Laporan'
import EditProfil    from './pages/EditProfil'
import Pengaturan    from './pages/Pengaturan'
import TanyaAI       from './pages/TanyaAI' // <-- TAMBAHAN BARU

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <Routes>
            <Route path="/"            element={<Navigate to="/login" replace />} />
            <Route path="/register"    element={<Register />} />
            <Route path="/login"       element={<Login />} />
            <Route path="/lupa-password" element={<LupaPassword />} />
            <Route path="/input"       element={<ProtectedRoute><InputChat /></ProtectedRoute>} />
            <Route path="/konfirmasi"  element={<ProtectedRoute><Konfirmasi /></ProtectedRoute>} />
            <Route path="/dashboard"   element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/laporan"     element={<ProtectedRoute><Laporan /></ProtectedRoute>} />
            
            {/* TAMBAHAN BARU: Route untuk halaman Tanya AI */}
            <Route path="/tanya-ai"    element={<ProtectedRoute><TanyaAI /></ProtectedRoute>} />
            
            <Route path="/profil"      element={<ProtectedRoute><EditProfil /></ProtectedRoute>} />
            <Route path="/pengaturan"  element={<ProtectedRoute><Pengaturan /></ProtectedRoute>} />
            <Route path="*"            element={<Navigate to="/login" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </ThemeProvider>
  )
}