import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { Shield, LogOut, LayoutDashboard } from 'lucide-react'

export default function Navbar({ transparent = false }) {
  const { token, user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 ${transparent ? '' : 'bg-navy-900/90 backdrop-blur-md border-b border-white/5'}`}>
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg group-hover:shadow-cyan-500/30 transition-shadow">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-white text-lg leading-none">BFSI</span>
            <span className="gradient-text font-bold text-lg leading-none"> RiskAI</span>
          </div>
        </Link>

        {/* Nav Links */}
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-slate-400 hover:text-white text-sm font-medium transition-colors">Features</a>
          <a href="#architecture" className="text-slate-400 hover:text-white text-sm font-medium transition-colors">Architecture</a>
          <a href="#tech-stack" className="text-slate-400 hover:text-white text-sm font-medium transition-colors">Tech Stack</a>
        </div>

        {/* Auth Actions */}
        <div className="flex items-center gap-3">
          {token ? (
            <>
              <span className="text-slate-400 text-sm hidden sm:block">
                {user?.full_name || user?.username}
              </span>
              <button onClick={() => navigate('/dashboard')} className="btn-primary py-2 px-4 text-sm flex items-center gap-2">
                <LayoutDashboard className="w-4 h-4" />
                Dashboard
              </button>
              <button onClick={handleLogout} className="p-2 rounded-xl hover:bg-white/10 text-slate-400 hover:text-red-400 transition-colors">
                <LogOut className="w-4 h-4" />
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-slate-400 hover:text-white text-sm font-medium transition-colors">
                Sign In
              </Link>
              <Link to="/login?mode=register" className="btn-primary py-2 px-4 text-sm">
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
