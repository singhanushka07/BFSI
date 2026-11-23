import { motion } from 'framer-motion'
import { Shield, ShieldCheck, ShieldAlert } from 'lucide-react'

export default function TrustScoreBadge({ score = 75, size = 120 }) {
  const getConfig = (s) => {
    if (s >= 80) return { color: '#22c55e', label: 'Verified', icon: ShieldCheck, bg: '#22c55e15' }
    if (s >= 50) return { color: '#f59e0b', label: 'Review', icon: ShieldAlert, bg: '#f59e0b15' }
    return { color: '#ef4444', label: 'Flagged', icon: ShieldAlert, bg: '#ef444415' }
  }

  const config = getConfig(score)
  const Icon = config.icon
  const radius = (size - 12) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="rgba(255,255,255,0.05)"
            strokeWidth="6"
            fill="none"
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={config.color}
            strokeWidth="6"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1, ease: 'easeOut', delay: 0.3 }}
            style={{ filter: `drop-shadow(0 0 6px ${config.color}50)` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <Icon size={20} style={{ color: config.color }} />
          <span className="text-xl font-bold text-white mt-1">{score.toFixed(0)}</span>
          <span className="text-[10px] text-white/40">/ 100</span>
        </div>
      </div>
      <span
        className="text-xs font-semibold px-3 py-1 rounded-full"
        style={{ background: config.bg, color: config.color }}
      >
        {config.label} Trust
      </span>
    </div>
  )
}
