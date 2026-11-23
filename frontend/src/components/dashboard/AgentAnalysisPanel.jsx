import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  TrendingUp, MessageSquare, FileText, Shield, Swords, Scale,
  ChevronDown, ChevronUp, CheckCircle, AlertTriangle, XCircle,
  Cpu, Database, Zap, BarChart2, ShieldCheck, ShieldAlert
} from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts'

const AGENT_META = {
  market:     { icon: TrendingUp,    color: '#06b6d4', label: 'Market Risk Agent',           mcp: ['get_stock_data', 'get_financial_metrics'] },
  sentiment:  { icon: MessageSquare, color: '#8b5cf6', label: 'Sentiment Agent',              mcp: ['get_news_sentiment'] },
  financial:  { icon: FileText,      color: '#3b82f6', label: 'Financial Report Agent (RAG)', mcp: ['get_financial_metrics', 'hybrid_rag_search', 'rerank_chunks'] },
  regulatory: { icon: Shield,        color: '#22c55e', label: 'Regulatory Compliance Agent',  mcp: ['get_regulatory_rules'] },
}

const RISK_COLORS = { LOW: '#22c55e', MEDIUM: '#f59e0b', HIGH: '#f97316', CRITICAL: '#ef4444' }

const TOOL_COLORS = {
  get_stock_data: '#06b6d4',
  get_financial_metrics: '#3b82f6',
  get_news_sentiment: '#8b5cf6',
  get_regulatory_rules: '#22c55e',
  rag_query: '#ec4899',
  hybrid_rag_search: '#f97316',
  rerank_chunks: '#a855f7',
}

function ScoreBar({ label, value, color }) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="text-slate-500 w-20 flex-shrink-0">{label}</span>
      <div className="flex-1 h-1.5 rounded-full bg-white/10">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${(value * 100).toFixed(0)}%`, background: color }}
        />
      </div>
      <span className="text-slate-400 font-mono w-8 text-right">{(value * 100).toFixed(0)}%</span>
    </div>
  )
}

function MCPCallBadge({ call }) {
  const color = TOOL_COLORS[call.tool] || '#94a3b8'
  return (
    <div
      className="flex items-start gap-2 p-2.5 rounded-xl text-xs border"
      style={{ background: `${color}08`, borderColor: `${color}25` }}
    >
      <Cpu className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color }} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-bold font-mono" style={{ color }}>{call.tool}</span>
          {call.success !== false && <span className="text-green-400">✓</span>}
        </div>
        {call.params && Object.keys(call.params).length > 0 && (
          <p className="text-slate-500 mt-0.5 font-mono truncate">
            {Object.entries(call.params).map(([k, v]) => `${k}=${JSON.stringify(v)}`).join(' ')}
          </p>
        )}
        {call.result_summary && <p className="text-slate-400 mt-0.5">{call.result_summary}</p>}
        {call.called_at && (
          <p className="text-slate-600 mt-0.5">{new Date(call.called_at).toLocaleTimeString()}</p>
        )}
      </div>
    </div>
  )
}

function HybridScoreCard({ scores }) {
  if (!scores?.length) return null
  return (
    <div className="p-3 rounded-xl border border-orange-500/20 bg-orange-500/5">
      <div className="flex items-center gap-2 mb-2">
        <BarChart2 className="w-3.5 h-3.5 text-orange-400" />
        <span className="text-xs font-semibold text-orange-400 uppercase tracking-wider">
          Hybrid Retrieval Scores
        </span>
        <span className="ml-auto text-xs text-slate-500 font-mono">BM25 + Dense → Re-ranked</span>
      </div>
      <div className="space-y-3">
        {scores.map((s, i) => (
          <div key={i} className="bg-white/3 rounded-lg p-2.5 border border-white/5">
            <p className="text-slate-300 text-xs font-medium mb-1.5">
              {s.source} <span className="text-slate-600">p.{s.page}</span>
            </p>
            <ScoreBar label="Hybrid" value={s.hybrid_score || 0} color="#f97316" />
            <ScoreBar label="Dense" value={s.dense_score || 0} color="#3b82f6" />
            <ScoreBar label="BM25" value={s.bm25_score || 0} color="#06b6d4" />
            <ScoreBar label="Re-rank" value={s.rerank_score || 0} color="#a855f7" />
          </div>
        ))}
      </div>
    </div>
  )
}

function GuardrailsBadge({ guardrails }) {
  if (!guardrails) return null
  const score = guardrails.confidence_score
  const status = guardrails.validation_status
  if (score == null) return null

  const config = score >= 80
    ? { icon: ShieldCheck, color: '#22c55e', label: 'Verified', bg: '#22c55e15' }
    : score >= 50
    ? { icon: ShieldAlert, color: '#f59e0b', label: 'Review', bg: '#f59e0b15' }
    : { icon: ShieldAlert, color: '#ef4444', label: 'Flagged', bg: '#ef444415' }

  const BadgeIcon = config.icon
  return (
    <span
      className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs border font-medium"
      style={{ background: config.bg, borderColor: `${config.color}30`, color: config.color }}
      title={`Confidence: ${score}/100 — ${(guardrails.issues || []).length} issue(s)`}
    >
      <BadgeIcon className="w-2.5 h-2.5" />{config.label} {score}
    </span>
  )
}

function GuardrailsDetail({ guardrails }) {
  if (!guardrails) return null
  const issues = guardrails.issues || []
  const verified = guardrails.verified_claims || []
  if (issues.length === 0 && verified.length === 0) return null

  return (
    <div className="p-3 rounded-xl border border-white/10 bg-white/3">
      <div className="flex items-center gap-2 mb-2">
        <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
        <p className="text-xs font-medium text-cyan-400 uppercase tracking-wider">
          Factual Validation
        </p>
      </div>
      {verified.length > 0 && (
        <div className="space-y-1 mb-2">
          {verified.map((claim, i) => (
            <div key={i} className="flex items-start gap-2 text-xs">
              <CheckCircle className="w-3 h-3 mt-0.5 text-green-400 flex-shrink-0" />
              <span className="text-slate-300">{claim}</span>
            </div>
          ))}
        </div>
      )}
      {issues.length > 0 && (
        <div className="space-y-1">
          {issues.map((issue, i) => {
            const sevColor = issue.severity === 'high' ? '#ef4444' : issue.severity === 'medium' ? '#f59e0b' : '#6b7280'
            return (
              <div key={i} className="flex items-start gap-2 text-xs">
                <AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" style={{ color: sevColor }} />
                <span className="text-slate-300">{issue.description}</span>
                <span className="ml-auto text-slate-500 flex-shrink-0">{issue.severity}</span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function AgentCard({ agentKey, data, defaultOpen = false, guardrails }) {
  const [open, setOpen] = useState(defaultOpen)
  const meta = AGENT_META[agentKey]
  if (!meta) return null
  const Icon = meta.icon
  const riskColor = RISK_COLORS[data?.risk_level] || '#94a3b8'

  return (
    <div className="glass-card border border-white/10 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-4 p-5 hover:bg-white/5 transition-colors text-left"
      >
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: `${meta.color}18`, border: `1px solid ${meta.color}44` }}
        >
          <Icon className="w-5 h-5" style={{ color: meta.color }} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="text-white font-semibold text-sm">{meta.label}</p>
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Cpu className="w-2.5 h-2.5" />MCP
            </span>
            {agentKey === 'financial' && (
              <>
                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs bg-pink-500/10 border border-pink-500/20 text-pink-400">
                  <Database className="w-2.5 h-2.5" />RAG
                </span>
                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs bg-orange-500/10 border border-orange-500/20 text-orange-400">
                  <BarChart2 className="w-2.5 h-2.5" />Hybrid
                </span>
              </>
            )}
            <GuardrailsBadge guardrails={guardrails} />
          </div>
          <p className="text-slate-400 text-xs truncate mt-0.5">{data?.analysis?.slice(0, 80)}...</p>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <div
            className="px-2.5 py-1 rounded-lg text-xs font-bold border"
            style={{ background: `${riskColor}15`, borderColor: `${riskColor}40`, color: riskColor }}
          >
            {data?.score?.toFixed(1)} — {data?.risk_level}
          </div>
          {open ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </div>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden border-t border-white/5"
          >
            <div className="p-5 space-y-4">
              {/* Analysis */}
              <div className="text-slate-300 text-sm leading-relaxed bg-white/3 rounded-xl p-4 border border-white/5">
                {data?.analysis}
              </div>

              {/* Guardrails validation */}
              <GuardrailsDetail guardrails={guardrails} />

              {/* MCP Calls */}
              {data?.mcp_calls?.length > 0 && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                    <p className="text-xs font-medium text-cyan-400 uppercase tracking-wider">
                      MCP Tool Calls ({data.mcp_calls.length})
                    </p>
                  </div>
                  <div className="space-y-1.5">
                    {data.mcp_calls.map((call, i) => <MCPCallBadge key={i} call={call} />)}
                  </div>
                </div>
              )}

              {/* Hybrid RAG section for financial agent */}
              {agentKey === 'financial' && (
                <>
                  <div
                    className="p-3 rounded-xl border text-xs"
                    style={{
                      background: data?.rag_chunks_retrieved > 0 ? '#ec489910' : '#94a3b810',
                      borderColor: data?.rag_chunks_retrieved > 0 ? '#ec489930' : '#94a3b830',
                    }}
                  >
                    <div className="flex items-center gap-2 mb-1.5">
                      <Database className="w-3.5 h-3.5" style={{ color: data?.rag_chunks_retrieved > 0 ? '#ec4899' : '#94a3b8' }} />
                      <span className="font-semibold" style={{ color: data?.rag_chunks_retrieved > 0 ? '#ec4899' : '#94a3b8' }}>
                        ChromaDB Hybrid RAG
                      </span>
                      {data?.rag_method && (
                        <span className="ml-auto text-slate-500 font-mono">{data.rag_method}</span>
                      )}
                    </div>
                    <div className="grid grid-cols-2 gap-2 mt-1.5">
                      <div>
                        <p className="text-slate-500">Collection</p>
                        <p className="font-mono text-slate-300">{data?.rag_collection || 'sample_financial_docs'}</p>
                      </div>
                      <div>
                        <p className="text-slate-500">Retrieved → Re-ranked</p>
                        <p className="text-white font-bold">
                          {data?.rag_chunks_retrieved ?? 0} → {data?.rag_chunks_reranked ?? 0}
                        </p>
                      </div>
                    </div>
                    {data?.sources_used?.length > 0 && (
                      <p className="text-slate-400 mt-1.5">
                        Sources: {data.sources_used.map(s => (
                          <span key={s} className="font-mono text-slate-300 mr-2">{s}</span>
                        ))}
                      </p>
                    )}
                  </div>

                  {/* Hybrid scores per chunk */}
                  <HybridScoreCard scores={data?.hybrid_scores} />
                </>
              )}

              {/* Metrics */}
              {data?.metrics && (
                <div>
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-3">Key Metrics</p>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {Object.entries(data.metrics).map(([k, v]) => (
                      <div key={k} className="bg-white/5 rounded-lg p-3 border border-white/5">
                        <p className="text-slate-400 text-xs capitalize">{k.replace(/_/g, ' ')}</p>
                        <p className="text-white font-semibold text-sm mt-0.5">
                          {typeof v === 'number'
                            ? (v > 1000 ? `$${(v / 1e9).toFixed(2)}B` : v.toLocaleString(undefined, { maximumFractionDigits: 3 }))
                            : String(v)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Compliance checks */}
              {data?.compliance_checks && (
                <div>
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-3">Compliance Checks</p>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {data.compliance_checks.map((c, i) => {
                      const StatusIcon = c.status === 'COMPLIANT' ? CheckCircle : c.status === 'WARNING' ? AlertTriangle : XCircle
                      const sc = c.status === 'COMPLIANT' ? 'text-green-400' : c.status === 'WARNING' ? 'text-amber-400' : 'text-red-400'
                      return (
                        <div key={i} className="flex items-start gap-2 text-xs">
                          <StatusIcon className={`w-3.5 h-3.5 mt-0.5 flex-shrink-0 ${sc}`} />
                          <div>
                            <span className="text-slate-300 font-medium">{c.rule}</span>
                            <span className="text-slate-500"> — {c.category}</span>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* News feed */}
              {data?.news_feed && (
                <div>
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-3">News Feed Analyzed</p>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {data.news_feed.slice(0, 5).map((n, i) => {
                      const sc = n.sentiment === 'positive' ? 'text-green-400 bg-green-500/10'
                        : n.sentiment === 'negative' ? 'text-red-400 bg-red-500/10'
                        : 'text-slate-400 bg-white/5'
                      return (
                        <div key={i} className="flex items-start gap-2">
                          <span className={`text-xs px-1.5 py-0.5 rounded uppercase font-bold flex-shrink-0 ${sc}`}>{n.sentiment[0]}</span>
                          <p className="text-slate-300 text-xs leading-relaxed">{n.headline}</p>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function AgentAnalysisPanel({ agents, scores, mcpCalls, techStackActive, guardrails }) {
  const radarData = [
    { subject: 'Market', score: scores?.market || 0 },
    { subject: 'Sentiment', score: scores?.sentiment || 0 },
    { subject: 'Financial', score: scores?.financial || 0 },
    { subject: 'Compliance', score: scores?.compliance || 0 },
  ]

  const totalMCPCalls = mcpCalls?.length || 0

  return (
    <div className="space-y-4">
      {/* Tech Stack Active banner */}
      {techStackActive && (
        <div className="glass-card p-4 border border-cyan-500/15">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="w-4 h-4 text-cyan-400" />
            <p className="text-white font-semibold text-sm">Tech Stack — All Active</p>
            <span className="ml-auto text-xs text-cyan-400 font-mono">{totalMCPCalls} MCP calls</span>
          </div>
          <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
            {Object.entries(techStackActive).map(([tech, active]) => (
              <div
                key={tech}
                className="text-center p-2 rounded-lg border"
                style={{
                  background: active ? '#22c55e08' : '#94a3b808',
                  borderColor: active ? '#22c55e30' : '#94a3b830',
                }}
              >
                <div className={`w-2 h-2 rounded-full mx-auto mb-1 ${active ? 'bg-green-400' : 'bg-slate-600'}`} />
                <p className="font-mono" style={{ color: active ? '#86efac' : '#64748b', fontSize: '9px' }}>
                  {tech.replace(/_/g, '-')}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Radar */}
      <div className="glass-card p-5">
        <p className="text-white font-semibold mb-4 text-sm">Risk Radar — Agent Score Breakdown</p>
        <ResponsiveContainer width="100%" height={220}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="rgba(255,255,255,0.08)" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <Radar name="Risk" dataKey="score" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.15} strokeWidth={2} />
            <Tooltip
              contentStyle={{ background: '#0f2044', border: '1px solid rgba(6,182,212,0.3)', borderRadius: 10, color: '#fff' }}
              formatter={(v) => [`${v.toFixed(1)} / 100`, 'Risk Score']}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Agent cards */}
      {agents && Object.entries(agents).map(([key, data], i) => (
        <AgentCard
          key={key}
          agentKey={key}
          data={data}
          defaultOpen={i === 0}
          guardrails={guardrails?.agents?.[key]}
        />
      ))}
    </div>
  )
}
