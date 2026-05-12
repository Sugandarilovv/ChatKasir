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
    <div className="min-h-screen flex flex-col transition-colors duration-300"
      style={{ background: isDark ? '#0d1117' : '#f1f5f9' }}>
      
      <Navbar onMenuClick={toggleMobileMenu} />
      
      <div className="flex flex-1 relative w-full max-w-full">
        <Sidebar 
          isMobileOpen={isMobileOpen} 
          onClose={() => setIsMobileOpen(false)} 
        />
        
        {/* PERBAIKAN: pt-6 (padding-top) ditambahkan agar konten sedikit turun ke bawah */}
        <main className="flex-1 px-2 pt-6 pb-4 sm:p-4 md:p-8 w-full min-w-0 max-w-7xl mx-auto overflow-x-hidden">
          {children}
        </main>
      </div>
    </div>
  )
}