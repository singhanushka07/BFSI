import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Shield, Zap, Brain, TrendingUp } from 'lucide-react'

const FLOATING_STATS = [
  { label: 'Risk Score', value: '73.2', unit: '/100', color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/20' },
  { label: 'Agents Active', value: '4', unit: '', color: 'text-cyan-400', bg: 'bg-cyan-500/10 border-cyan-500/20' },
  { label: 'Docs Indexed', value: '247', unit: '', color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20' },
  { label: 'Compliance', value: '87.5', unit: '%', color: 'text-green-400', bg: 'bg-green-500/10 border-green-500/20' },
]

export default function Hero() {
  return (
    <section className="relative min-h-screen hero-bg bg-grid-pattern flex items-center overflow-hidden pt-20">
      {/* Animated background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-blue-600/5 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
        <div className="absolute top-3/4 left-1/2 w-64 h-64 bg-violet-500/4 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '2s' }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-6 py-20 grid lg:grid-cols-2 gap-16 items-center">
        {/* Left: Text */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-sm font-medium mb-6"
          >
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
            AI-Powered · 4 Specialized Agents · Real-time Analysis
          </motion.div>

          <h1 className="text-5xl lg:text-6xl font-extrabold leading-tight mb-6">
            <span className="text-white">BFSI Multi-Agent</span>
            <br />
            <span className="gradient-text">Financial Risk</span>
            <br />
            <span className="text-white">Assessment Platform</span>
          </h1>

          <p className="text-slate-400 text-lg leading-relaxed mb-8 max-w-xl">
            Engineered with <span className="text-cyan-400 font-medium">LangGraph</span>, <span className="text-cyan-400 font-medium">LangChain</span>, and <span className="text-cyan-400 font-medium">GPT-4o</span> — orchestrating 4 specialized AI agents to automate corporate risk analysis across market exposure, sentiment, financial reports, and regulatory compliance.
          </p>

          {/* Key highlights */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
            {[
              { icon: Brain, text: 'RAG pipeline — ~80% less manual analysis' },
              { icon: Shield, text: 'JWT-secured REST APIs + SQLite' },
              { icon: TrendingUp, text: 'Real-time risk scoring & trend analysis' },
              { icon: Zap, text: 'MCP tool layer for agent coordination' },
            ].map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-3 text-slate-300 text-sm">
                <div className="w-7 h-7 rounded-lg bg-cyan-500/15 flex items-center justify-center flex-shrink-0">
                  <Icon className="w-3.5 h-3.5 text-cyan-400" />
                </div>
                {text}
              </div>
            ))}
          </div>

          <div className="flex flex-wrap gap-4">
            <Link to="/login?mode=register" className="btn-primary flex items-center gap-2 text-base px-7 py-3.5">
              Launch Platform
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a href="#architecture" className="btn-secondary flex items-center gap-2 text-base px-7 py-3.5">
              View Architecture
            </a>
          </div>
        </motion.div>

        {/* Right: Animated Risk Dashboard Preview */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="relative"
        >
          {/* Main card */}
          <div className="glass-card p-6 glow-border relative overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between mb-5">
              <div>
                <p className="text-slate-400 text-xs font-medium uppercase tracking-wider">Live Risk Assessment</p>
                <p className="text-white font-bold text-lg mt-0.5">TechCorp Global (TCG)</p>
              </div>
              <div className="px-3 py-1.5 rounded-lg bg-orange-500/15 border border-orange-500/30">
                <span className="text-orange-400 font-bold text-sm">HIGH RISK</span>
              </div>
            </div>

            {/* Risk Score Dial */}
            <div className="flex items-center justify-center mb-5">
              <div className="relative w-36 h-36">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                  <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
                  <motion.circle
                    cx="50" cy="50" r="42"
                    fill="none"
                    stroke="url(#scoreGradient)"
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray="263.9"
                    initial={{ strokeDashoffset: 263.9 }}
                    animate={{ strokeDashoffset: 263.9 * (1 - 0.732) }}
                    transition={{ duration: 1.5, delay: 0.8, ease: 'easeOut' }}
                  />
                  <defs>
                    <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#f97316" />
                      <stop offset="100%" stopColor="#ef4444" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-extrabold text-white">73.2</span>
                  <span className="text-slate-400 text-xs">/ 100</span>
                </div>
              </div>
            </div>

            {/* Agent Scores */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              {[
                { label: 'Market Risk', score: 68, color: '#06b6d4' },
                { label: 'Sentiment', score: 55, color: '#22c55e' },
                { label: 'Financial', score: 82, color: '#f97316' },
                { label: 'Compliance', score: 71, color: '#a855f7' },
              ].map(({ label, score, color }) => (
                <div key={label} className="bg-white/5 rounded-xl p-3">
                  <div className="flex justify-between mb-1.5">
                    <span className="text-slate-400 text-xs">{label}</span>
                    <span className="text-white text-xs font-bold">{score}</span>
                  </div>
                  <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      style={{ backgroundColor: color }}
                      initial={{ width: 0 }}
                      animate={{ width: `${score}%` }}
                      transition={{ duration: 1, delay: 1 }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Status */}
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
              4 agents processed · ChromaDB RAG active · MCP connected
            </div>
          </div>

          {/* Floating stats */}
          {FLOATING_STATS.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 1 + i * 0.1 }}
              className={`absolute glass-card border px-3 py-2 text-center ${stat.bg} ${
                i === 0 ? '-top-4 -left-8' :
                i === 1 ? '-top-4 -right-8' :
                i === 2 ? '-bottom-4 -left-8' :
                '-bottom-4 -right-8'
              }`}
            >
              <div className={`font-bold text-lg ${stat.color}`}>{stat.value}{stat.unit}</div>
              <div className="text-slate-400 text-xs">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-slate-500">
        <span className="text-xs">Scroll to explore</span>
        <motion.div animate={{ y: [0, 6, 0] }} transition={{ repeat: Infinity, duration: 1.5 }} className="w-5 h-8 border border-slate-600 rounded-full flex items-start justify-center pt-1.5">
          <div className="w-1 h-2 bg-cyan-400 rounded-full" />
        </motion.div>
      </div>
    </section>
  )
}
