import { motion, AnimatePresence } from 'framer-motion'
import { Loader2, CheckCircle2, AlertCircle, Bot, Shield, Scale, Swords, Layers } from 'lucide-react'

const AGENT_CONFIG = {
  market_risk: { label: 'Market Risk Agent', color: '#06b6d4', icon: Bot },
  sentiment: { label: 'Sentiment Agent', color: '#8b5cf6', icon: Bot },
  financial_report: { label: 'Financial Report Agent (RAG)', color: '#3b82f6', icon: Bot },
  regulatory: { label: 'Regulatory Compliance Agent', color: '#22c55e', icon: Bot },
  aggregator: { label: 'LangGraph Aggregator', color: '#f97316', icon: Layers },
  guardrails: { label: 'Guardrails Validator', color: '#ec4899', icon: Shield },
  devils_advocate: { label: "Devil's Advocate Agent", color: '#ef4444', icon: Swords },
  judge: { label: 'Judge Agent', color: '#6366f1', icon: Scale },
}

export default function StreamingAgentIndicator({ agents }) {
  const agentOrder = [
    'market_risk', 'sentiment', 'financial_report', 'regulatory',
    'aggregator', 'guardrails', 'devils_advocate', 'judge',
  ]

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-white/60 uppercase tracking-wider mb-4">
        Agent Pipeline — Live
      </h3>
      {agentOrder.map((key, i) => {
        const config = AGENT_CONFIG[key]
        const agent = agents[key]
        if (!agent) return null

        const Icon = config.icon
        const isRunning = agent.status === 'running'
        const isDone = agent.status === 'done'
        const isError = agent.status === 'error'

        return (
          <motion.div
            key={key}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.08 }}
            className="flex items-center gap-3 p-3 rounded-lg"
            style={{
              background: isDone
                ? `${config.color}10`
                : isRunning
                ? `${config.color}08`
                : 'transparent',
              border: `1px solid ${isDone ? config.color + '40' : isRunning ? config.color + '30' : 'rgba(255,255,255,0.05)'}`,
            }}
          >
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ background: `${config.color}20` }}
            >
              <Icon size={16} style={{ color: config.color }} />
            </div>

            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-white/90 truncate">
                {config.label}
              </div>
              {isRunning && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-xs text-white/40 mt-0.5"
                >
                  Analyzing...
                </motion.div>
              )}
              {isDone && agent.score !== undefined && (
                <div className="text-xs text-white/50 mt-0.5">
                  Score: {typeof agent.score === 'number' ? agent.score.toFixed(1) : agent.score}/100
                </div>
              )}
            </div>

            <div className="flex-shrink-0">
              <AnimatePresence mode="wait">
                {isRunning && (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.5 }}
                  >
                    <Loader2 size={18} className="animate-spin" style={{ color: config.color }} />
                  </motion.div>
                )}
                {isDone && (
                  <motion.div
                    key="done"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                  >
                    <CheckCircle2 size={18} style={{ color: config.color }} />
                  </motion.div>
                )}
                {isError && (
                  <motion.div
                    key="error"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                  >
                    <AlertCircle size={18} className="text-red-400" />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}
