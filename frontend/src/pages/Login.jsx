import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Eye, EyeOff, Loader2, ArrowLeft } from 'lucide-react'
import { authAPI } from '../api/client'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function Login() {
  const [searchParams] = useSearchParams()
  const [mode, setMode] = useState(searchParams.get('mode') === 'register' ? 'register' : 'login')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { setAuth, token } = useAuthStore()
  const navigate = useNavigate()

  const [form, setForm] = useState({ email: '', password: '', username: '', full_name: '' })

  useEffect(() => {
    if (token) navigate('/dashboard')
  }, [token, navigate])

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = mode === 'login'
        ? await authAPI.login({ email: form.email, password: form.password })
        : await authAPI.register(form)
      setAuth(res.data.user, res.data.access_token)
      toast.success(mode === 'login' ? 'Welcome back!' : 'Account created!')
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen hero-bg bg-grid-pattern flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-blue-600/5 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-md relative">
        {/* Back link */}
        <Link to="/" className="flex items-center gap-2 text-slate-400 hover:text-white text-sm mb-8 transition-colors group">
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Back to home
        </Link>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card glow-border p-8"
        >
          {/* Logo */}
          <div className="flex flex-col items-center mb-8">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30 mb-4">
              <Shield className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-2xl font-extrabold text-white">BFSI RiskAI</h1>
            <p className="text-slate-400 text-sm mt-1">Multi-Agent Financial Risk Platform</p>
          </div>

          {/* Mode Toggle */}
          <div className="flex bg-white/5 rounded-xl p-1 mb-7">
            {['login', 'register'].map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                  mode === m ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                }`}
              >
                {m === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            <motion.form
              key={mode}
              initial={{ opacity: 0, x: mode === 'login' ? -10 : 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onSubmit={handleSubmit}
              className="space-y-4"
            >
              {mode === 'register' && (
                <>
                  <div>
                    <label className="text-slate-300 text-sm font-medium mb-1.5 block">Full Name</label>
                    <input
                      name="full_name"
                      value={form.full_name}
                      onChange={handleChange}
                      placeholder="Jane Smith"
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="text-slate-300 text-sm font-medium mb-1.5 block">Username</label>
                    <input
                      name="username"
                      value={form.username}
                      onChange={handleChange}
                      placeholder="janesmith"
                      required
                      className="input-field"
                    />
                  </div>
                </>
              )}

              <div>
                <label className="text-slate-300 text-sm font-medium mb-1.5 block">Email</label>
                <input
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="jane@example.com"
                  required
                  className="input-field"
                />
              </div>

              <div>
                <label className="text-slate-300 text-sm font-medium mb-1.5 block">Password</label>
                <div className="relative">
                  <input
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={form.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    required
                    minLength={6}
                    className="input-field pr-12"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full flex items-center justify-center gap-2 mt-2"
              >
                {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                {mode === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            </motion.form>
          </AnimatePresence>

          {/* Demo hint */}
          <div className="mt-5 p-3 rounded-xl bg-cyan-500/5 border border-cyan-500/20">
            <p className="text-xs text-slate-400 text-center">
              <span className="text-cyan-400 font-medium">Demo:</span> Register any email/password to get started instantly
            </p>
          </div>
        </motion.div>

        {/* Tech tags */}
        <div className="flex flex-wrap justify-center gap-2 mt-6">
          {['FastAPI', 'JWT Auth', 'SQLite', 'bcrypt'].map((t) => (
            <span key={t} className="text-xs px-2.5 py-1 rounded-full bg-white/5 text-slate-500 border border-white/5">{t}</span>
          ))}
        </div>
      </div>
    </div>
  )
}
