import Navbar  from './Navbar'
import Sidebar from './Sidebar'
import { useTheme } from '../../context/ThemeContext'

export default function MainLayout({ children }) {
  const { theme } = useTheme()
  const isDark    = theme === 'dark'

  return (
    <div className="min-h-screen transition-colors duration-300"
      style={{ background: isDark ? '#0d1117' : '#f8fffe' }}>
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6 max-w-6xl mx-auto w-full">
          {children}
        </main>
      </div>
    </div>
  )
}