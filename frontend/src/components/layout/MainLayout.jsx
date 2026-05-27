import { useState } from 'react'
import Navbar  from './Navbar'
import Sidebar from './Sidebar'
import { useTheme } from '../../context/ThemeContext'

export default function MainLayout({ children }) {
  const { theme } = useTheme()
  const isDark    = theme === 'dark'
  
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  const toggleMobileMenu = () => {
    setIsMobileOpen((prev) => !prev)
  }

  return (
    // PERBAIKAN 1: Menggunakan h-screen dan overflow-hidden.
    // Ini mengunci layout agar tepat 1 layar penuh dan mencegah scroll global yang bikin belang.
    <div className="flex flex-col h-screen w-full overflow-hidden transition-colors duration-300"
      style={{ background: isDark ? '#0d1117' : '#f1f5f9' }}>
      
      {/* PERBAIKAN 2: Navbar dibungkus div terpisah dengan flex-shrink-0 */}
      {/* Agar posisi navbar kokoh di atas dan tidak ikut tertekan saat konten bawah memanjang */}
      <div className="shrink-0 z-50">
        <Navbar onMenuClick={toggleMobileMenu} />
      </div>
      
      {/* Pembungkus Bawah (Tempat Sidebar & Area Utama) */}
      <div className="flex flex-1 overflow-hidden relative w-full">
        
        {/* Sidebar Kiri - Sekarang akan selalu penuh dari atas ke bawah layar */}
        <Sidebar 
          isMobileOpen={isMobileOpen} 
          onClose={() => setIsMobileOpen(false)} 
        />
        
        {/* PERBAIKAN 3: Area Main diberi overflow-y-auto */}
        {/* Sekarang, jika konten panjang, scroll-nya hanya akan terjadi di dalam area kanan ini saja! */}
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-4 md:p-6 lg:p-8 w-full">
          {/* Pembungkus dalam agar konten tidak terlalu melebar di monitor besar */}
          <div className="max-w-7xl mx-auto w-full">
            {children}
          </div>
        </main>

      </div>
    </div>
  )
}