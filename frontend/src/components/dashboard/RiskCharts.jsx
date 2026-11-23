import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine
} from 'recharts'
import { motion } from 'framer-motion'

const TOOLTIP_STYLE = {
  contentStyle: { background: '#0f2044', border: '1px solid rgba(6,182,212,0.3)', borderRadius: 12, color: '#fff', fontSize: 12 },
  labelStyle: { color: '#94a3b8' },
}

const AGENT_COLORS = { market: '#06b6d4', sentiment: '#8b5cf6', financial: '#3b82f6', compliance: '#22c55e', overall: '#f97316' }

export function RiskTrendChart({ data = [] }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
      <p className="text-white font-semibold mb-1 text-sm">Risk Score Trend (30 Days)</p>
      <p className="text-slate-500 text-xs mb-4">Historical overall risk across all agents</p>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="overallGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="rgba(255,255,255,0.04)" />
          <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={(d) => d.slice(5)} interval={4} />
          <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
          <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [`${v.toFixed(1)}`, '']} />
          <ReferenceLine y={75} stroke="#ef4444" strokeDasharray="4 3" strokeOpacity={0.4} label={{ value: 'HIGH', fill: '#ef4444', fontSize: 9 }} />
          <ReferenceLine y={50} stroke="#f59e0b" strokeDasharray="4 3" strokeOpacity={0.3} />
          <Area type="monotone" dataKey="overall" stroke="#f97316" strokeWidth={2} fill="url(#overallGradient)" name="Overall" />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  )
}

export function AgentBreakdownChart({ data = [] }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-5">
      <p className="text-white font-semibold mb-1 text-sm">Agent Score Breakdown (14 Days)</p>
      <p className="text-slate-500 text-xs mb-4">Individual agent risk scores over time</p>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid stroke="rgba(255,255,255,0.04)" />
          <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} tickFormatter={(d) => d.slice(5)} interval={1} />
          <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
          <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [`${v.toFixed(1)}`, '']} />
          <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
          {Object.entries(AGENT_COLORS).filter(([k]) => k !== 'overall').map(([key, color]) => (
            <Line key={key} type="monotone" dataKey={key} stroke={color} strokeWidth={2}
              dot={false} name={key.charAt(0).toUpperCase() + key.slice(1)} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
  )
}

export function RiskDistributionBar({ distribution = {} }) {
  const data = Object.entries(distribution).map(([level, count]) => ({ level, count }))
  const colors = { LOW: '#22c55e', MEDIUM: '#f59e0b', HIGH: '#f97316', CRITICAL: '#ef4444' }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-5">
      <p className="text-white font-semibold mb-1 text-sm">Risk Distribution</p>
      <p className="text-slate-500 text-xs mb-4">Breakdown of analyses by risk level</p>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} barSize={36}>
          <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
          <XAxis dataKey="level" tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <YAxis tick={{ fill: '#64748b', fontSize: 10 }} allowDecimals={false} />
          <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [v, 'Analyses']} />
          <Bar dataKey="count" name="Analyses" radius={[6, 6, 0, 0]}>
            {data.map((entry, i) => (
              <rect key={i} fill={colors[entry.level] || '#94a3b8'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  )
}

export function AgentAveragesCard({ averages = {} }) {
  const items = [
    { key: 'market', label: 'Market Risk', color: '#06b6d4' },
    { key: 'sentiment', label: 'Sentiment', color: '#8b5cf6' },
    { key: 'financial', label: 'Financial', color: '#3b82f6' },
    { key: 'compliance', label: 'Compliance', color: '#22c55e' },
  ]

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass-card p-5">
      <p className="text-white font-semibold mb-4 text-sm">Average Agent Scores</p>
      <div className="space-y-4">
        {items.map(({ key, label, color }) => {
          const val = averages[key] || 0
          return (
            <div key={key}>
              <div className="flex justify-between mb-1.5">
                <span className="text-slate-300 text-xs font-medium">{label}</span>
                <span className="text-xs font-bold" style={{ color }}>{val.toFixed(1)}</span>
              </div>
              <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: color }}
                  initial={{ width: 0 }}
                  animate={{ width: `${val}%` }}
                  transition={{ duration: 0.8, delay: 0.3 }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </motion.div>
  )
}
