import { motion } from 'framer-motion'

const COLORS = { LOW: '#22c55e', MEDIUM: '#f59e0b', HIGH: '#f97316', CRITICAL: '#ef4444' }
const LABELS = { LOW: 'Low Risk', MEDIUM: 'Medium Risk', HIGH: 'High Risk', CRITICAL: 'Critical Risk' }

export default function RiskScoreGauge({ score = 50, level = 'MEDIUM', size = 160 }) {
  const color = COLORS[level] || '#06b6d4'
  const circumference = 2 * Math.PI * 54
  const progress = (score / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
          {/* Background track */}
          <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
          {/* Score arc */}
          <motion.circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - progress }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
            style={{ filter: `drop-shadow(0 0 8px ${color}80)` }}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-3xl font-extrabold text-white leading-none"
          >
            {score?.toFixed(1)}
          </motion.span>
          <span className="text-slate-500 text-xs mt-0.5">/ 100</span>
        </div>
      </div>
      <div
        className="px-3 py-1 rounded-full text-xs font-bold border"
        style={{ backgroundColor: `${color}20`, borderColor: `${color}40`, color }}
      >
        {LABELS[level] || level}
      </div>
    </div>
  )
}
