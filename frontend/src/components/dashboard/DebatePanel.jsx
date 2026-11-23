import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Swords, Scale, ChevronDown, AlertTriangle, CheckCircle2, XCircle, Minus } from 'lucide-react'

const SEVERITY_COLORS = {
  critical: { bg: '#ef444420', border: '#ef444460', text: '#ef4444' },
  major: { bg: '#f9731620', border: '#f9731660', text: '#f97316' },
  minor: { bg: '#f59e0b20', border: '#f59e0b60', text: '#f59e0b' },
}

const RULING_CONFIG = {
  accepted: { icon: CheckCircle2, color: '#22c55e', label: 'Accepted' },
  partially_accepted: { icon: Minus, color: '#f59e0b', label: 'Partially Accepted' },
  dismissed: { icon: XCircle, color: '#6b7280', label: 'Dismissed' },
}

const IMPACT_COLORS = {
  minimal: '#22c55e',
  moderate: '#f59e0b',
  significant: '#ef4444',
}

export default function DebatePanel({ debate }) {
  const [expanded, setExpanded] = useState(true)

  if (!debate || (!debate.devils_advocate && !debate.judge)) return null

  const da = debate.devils_advocate || {}
  const judge = debate.judge || {}
  const challenges = da.challenges || []
  const verdicts = judge.verdicts || []
  const adjustedScores = judge.adjusted_scores || {}
  const impact = judge.debate_impact || 'minimal'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="glass-card p-6 mt-6"
    >
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-orange-500/10 flex items-center justify-center">
            <Swords size={20} className="text-orange-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Multi-Agent Debate</h3>
            <p className="text-sm text-white/50">
              {challenges.length} challenge{challenges.length !== 1 ? 's' : ''} raised
              <span
                className="ml-2 px-2 py-0.5 rounded-full text-xs font-medium"
                style={{
                  background: `${IMPACT_COLORS[impact]}20`,
                  color: IMPACT_COLORS[impact],
                }}
              >
                {impact} impact
              </span>
            </p>
          </div>
        </div>
        <ChevronDown
          size={20}
          className={`text-white/40 transition-transform ${expanded ? 'rotate-180' : ''}`}
        />
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Devil's Advocate */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Swords size={16} className="text-red-400" />
                  <h4 className="text-sm font-semibold text-red-400 uppercase tracking-wider">
                    Devil&apos;s Advocate
                  </h4>
                </div>

                <div className="space-y-3">
                  {challenges.map((c, i) => {
                    const sev = SEVERITY_COLORS[c.severity] || SEVERITY_COLORS.minor
                    const verdict = verdicts[i]
                    const ruling = verdict ? RULING_CONFIG[verdict.ruling] || RULING_CONFIG.dismissed : null

                    return (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-3 rounded-lg"
                        style={{ background: sev.bg, border: `1px solid ${sev.border}` }}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span
                                className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded"
                                style={{ background: sev.border, color: '#fff' }}
                              >
                                {c.severity}
                              </span>
                              <span className="text-xs text-white/50">
                                vs {c.target_agent}
                              </span>
                            </div>
                            <p className="text-sm text-white/80">{c.challenge}</p>
                          </div>
                          {ruling && (
                            <div className="flex-shrink-0" title={ruling.label}>
                              <ruling.icon size={16} style={{ color: ruling.color }} />
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )
                  })}
                </div>

                {da.analysis && (
                  <div className="mt-4 p-3 rounded-lg bg-white/5 border border-white/10">
                    <p className="text-xs text-white/60 leading-relaxed">{da.analysis}</p>
                  </div>
                )}
              </div>

              {/* Judge */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Scale size={16} className="text-indigo-400" />
                  <h4 className="text-sm font-semibold text-indigo-400 uppercase tracking-wider">
                    Judge Verdict
                  </h4>
                </div>

                <div className="space-y-3">
                  {verdicts.map((v, i) => {
                    const ruling = RULING_CONFIG[v.ruling] || RULING_CONFIG.dismissed
                    const RulingIcon = ruling.icon
                    return (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 + 0.2 }}
                        className="p-3 rounded-lg bg-white/5 border border-white/10"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <RulingIcon size={14} style={{ color: ruling.color }} />
                          <span className="text-xs font-semibold" style={{ color: ruling.color }}>
                            {ruling.label}
                          </span>
                        </div>
                        <p className="text-sm text-white/70">{v.reasoning}</p>
                      </motion.div>
                    )
                  })}
                </div>

                {judge.verdict && (
                  <div className="mt-4 p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/30">
                    <p className="text-xs text-white/70 leading-relaxed">{judge.verdict}</p>
                  </div>
                )}

                {/* Score Adjustments */}
                {Object.keys(adjustedScores).length > 0 && (
                  <div className="mt-4">
                    <h5 className="text-xs font-semibold text-white/40 uppercase mb-2">
                      Score Adjustments
                    </h5>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(adjustedScores).map(([key, val]) => (
                        <div key={key} className="p-2 rounded bg-white/5 text-center">
                          <div className="text-[10px] text-white/40 capitalize">{key}</div>
                          <div className="text-sm font-bold text-white">{typeof val === 'number' ? val.toFixed(1) : val}</div>
                        </div>
                      ))}
                    </div>
                    {judge.adjusted_overall && (
                      <div className="mt-2 p-2 rounded bg-indigo-500/10 text-center">
                        <div className="text-[10px] text-white/40">Adjusted Overall</div>
                        <div className="text-lg font-bold text-indigo-400">
                          {typeof judge.adjusted_overall === 'number' ? judge.adjusted_overall.toFixed(1) : judge.adjusted_overall}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Contradictions */}
            {da.contradictions && da.contradictions.length > 0 && (
              <div className="mt-6 p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle size={14} className="text-amber-400" />
                  <h5 className="text-xs font-semibold text-amber-400 uppercase">
                    Contradictions Detected
                  </h5>
                </div>
                {da.contradictions.map((c, i) => (
                  <p key={i} className="text-sm text-white/70 mt-1">
                    <span className="text-amber-400">{(c.agents || []).join(' vs ')}</span>: {c.description}
                  </p>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
