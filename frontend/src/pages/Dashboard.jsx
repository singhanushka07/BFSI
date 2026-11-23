import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Shield, TrendingUp, MessageSquare, FileText, BarChart3,
  Loader2, Play, LogOut, ChevronRight, Database, Zap, AlertTriangle
} from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { agentsAPI, dashboardAPI } from '../api/client'
import { RiskTrendChart, AgentBreakdownChart, RiskDistributionBar, AgentAveragesCard } from '../components/dashboard/RiskCharts'
import AgentAnalysisPanel from '../components/dashboard/AgentAnalysisPanel'
import RiskScoreGauge from '../components/dashboard/RiskScoreGauge'
import TrustScoreBadge from '../components/dashboard/TrustScoreBadge'
import StreamingAgentIndicator from '../components/dashboard/StreamingAgentIndicator'
import DebatePanel from '../components/dashboard/DebatePanel'
import ChatPanel from '../components/dashboard/ChatPanel'
import PDFUpload from '../components/dashboard/PDFUpload'
import toast from 'react-hot-toast'

const TABS = [
  { id: 'overview', label: 'Overview', icon: BarChart3 },
  { id: 'analyze', label: 'Run Analysis', icon: Play },
  { id: 'rag', label: 'RAG / Documents', icon: Database },
  { id: 'history', label: 'History', icon: FileText },
]

const RISK_COLORS = { LOW: '#22c55e', MEDIUM: '#f59e0b', HIGH: '#f97316', CRITICAL: '#ef4444' }

function StatCard({ label, value, sub, color, icon: Icon }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-1">{label}</p>
          <p className="text-3xl font-extrabold" style={{ color }}>{value}</p>
          {sub && <p className="text-slate-500 text-xs mt-1">{sub}</p>}
        </div>
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `${color}15`, border: `1px solid ${color}30` }}>
          <Icon className="w-5 h-5" style={{ color }} />
        </div>
      </div>
    </motion.div>
  )
}

export default function Dashboard() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('overview')

  // Overview
  const [stats, setStats] = useState(null)
  const [trendData, setTrendData] = useState([])
  const [overview, setOverview] = useState(null)

  // Analysis form
  const [companies, setCompanies] = useState([])
  const [selectedCompany, setSelectedCompany] = useState(null)
  const [customCompany, setCustomCompany] = useState('')
  const [customTicker, setCustomTicker] = useState('')
  const [customSector, setCustomSector] = useState('Financial Services')
  const [collectionName, setCollectionName] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [streamingAgents, setStreamingAgents] = useState({})

  // History
  const [history, setHistory] = useState([])

  const loadOverview = useCallback(async () => {
    try {
      const [s, o] = await Promise.all([dashboardAPI.stats(), dashboardAPI.overview()])
      setStats(s.data)
      setOverview(o.data)
      if (o.data?.trend_data) setTrendData(o.data.trend_data)
    } catch { /* silent */ }
  }, [])

  const loadHistory = useCallback(async () => {
    try {
      const res = await agentsAPI.history()
      setHistory(res.data)
    } catch { /* silent */ }
  }, [])

  const loadCompanies = useCallback(async () => {
    try {
      const res = await agentsAPI.companies()
      setCompanies(res.data)
      if (res.data.length > 0) setSelectedCompany(res.data[0])
    } catch { /* silent */ }
  }, [])

  useEffect(() => {
    loadOverview()
    loadHistory()
    loadCompanies()
  }, [loadOverview, loadHistory, loadCompanies])

  const handleLogout = () => { logout(); navigate('/') }

  const runAnalysis = async () => {
    const company = customCompany || selectedCompany?.name || ''
    const ticker = customTicker || selectedCompany?.ticker || 'TKR'
    if (!company) { toast.error('Select or enter a company'); return }
    setAnalyzing(true)
    setAnalysisResult(null)
    setStreamingAgents({})

    const handleStreamEvent = (eventType, data) => {
      if (eventType === 'agent_start') {
        setStreamingAgents((prev) => ({
          ...prev,
          [data.agent]: { status: 'running', label: data.label },
        }))
      } else if (eventType === 'agent_complete') {
        setStreamingAgents((prev) => ({
          ...prev,
          [data.agent]: { status: 'done', label: data.label, score: data.score, risk_level: data.risk_level },
        }))
      } else if (eventType === 'guardrails_complete') {
        setStreamingAgents((prev) => ({
          ...prev,
          guardrails: { status: 'done', label: 'Guardrails Validator', score: data.trust_score },
        }))
      } else if (eventType === 'debate_start') {
        setStreamingAgents((prev) => ({
          ...prev,
          devils_advocate: { status: 'running', label: "Devil's Advocate Agent" },
        }))
      } else if (eventType === 'agent_error') {
        setStreamingAgents((prev) => ({
          ...prev,
          [data.agent]: { ...prev[data.agent], status: 'error' },
        }))
      }
    }

    try {
      const result = await agentsAPI.analyzeStream({
        company, ticker,
        sector: customSector || selectedCompany?.sector || 'Financial Services',
        collection_name: collectionName || undefined,
      }, handleStreamEvent)

      if (result) {
        setAnalysisResult(result)
        toast.success(`Analysis complete — Risk: ${result.risk_level}`)
      }
      await loadOverview()
      await loadHistory()
    } catch (err) {
      toast.error(err.message || 'Analysis failed')
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="min-h-screen bg-navy-950 flex flex-col">
      {/* Header */}
      <header className="bg-navy-900/90 backdrop-blur-md border-b border-white/5 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
              <Shield className="w-4 h-4 text-white" />
            </div>
            <div>
              <span className="font-bold text-white">BFSI</span>
              <span className="gradient-text font-bold"> RiskAI</span>
            </div>
            <span className="hidden sm:block text-slate-600 mx-2">|</span>
            <span className="hidden sm:block text-slate-400 text-sm">Multi-Agent Financial Risk Platform</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
              <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse" />
              <span className="text-cyan-400 text-xs font-medium">6 Agents Online</span>
            </div>
            <span className="text-slate-400 text-sm hidden sm:block">{user?.full_name || user?.username}</span>
            <button onClick={handleLogout} className="p-2 rounded-xl hover:bg-white/10 text-slate-400 hover:text-red-400 transition-colors">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Tech banner */}
      <div className="bg-navy-900/50 border-b border-white/5 py-2.5 overflow-hidden">
        <div className="flex gap-6 px-6 flex-wrap items-center">
          {['LangGraph', 'LangChain', 'GPT-4o', 'FastAPI', 'ChromaDB', 'MCP', 'SSE Streaming', 'Guardrails', 'Agent Debate', 'Risk Chat'].map((t) => (
            <span key={t} className="text-xs text-slate-500 flex items-center gap-1.5">
              <span className="w-1 h-1 bg-cyan-500/50 rounded-full" />{t}
            </span>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-white/5 bg-navy-900/30">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1">
            {TABS.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`flex items-center gap-2 px-4 py-4 text-sm font-medium border-b-2 transition-all duration-200
                  ${activeTab === id ? 'border-cyan-500 text-cyan-400' : 'border-transparent text-slate-400 hover:text-white'}`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:block">{label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">

        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stat cards */}
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="Total Analyses" value={stats?.total_analyses ?? '—'} sub="All time" color="#06b6d4" icon={BarChart3} />
              <StatCard label="Avg Risk Score" value={stats?.avg_risk_score ?? '—'} sub="Weighted avg" color="#f97316" icon={AlertTriangle} />
              <StatCard label="High Risk" value={stats?.high_risk_count ?? '—'} sub="Companies flagged" color="#ef4444" icon={TrendingUp} />
              <StatCard label="RAG Active" value="3 PDFs" sub="sample_financial_docs" color="#ec4899" icon={Database} />
            </div>

            {/* Charts row 1 */}
            <div className="grid lg:grid-cols-2 gap-5">
              <RiskTrendChart data={trendData} />
              <AgentAveragesCard averages={overview?.agent_averages || {}} />
            </div>

            {/* Charts row 2 */}
            <div className="grid lg:grid-cols-3 gap-5">
              <div className="lg:col-span-2">
                <AgentBreakdownChart data={trendData.slice(-14)} />
              </div>
              <RiskDistributionBar distribution={stats?.risk_distribution || {}} />
            </div>

            {/* Recent analyses */}
            {stats?.recent_analyses?.length > 0 && (
              <div className="glass-card p-5">
                <p className="text-white font-semibold text-sm mb-4">Recent Analyses</p>
                <div className="space-y-2">
                  {stats.recent_analyses.map((a) => (
                    <div key={a.id} className="flex items-center gap-4 p-3 rounded-xl bg-white/5 hover:bg-white/8 transition-colors">
                      <div className="flex-1">
                        <p className="text-white text-sm font-medium">{a.company}</p>
                        <p className="text-slate-500 text-xs">{a.ticker} · {a.date}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-white text-sm font-bold">{a.score?.toFixed(1)}</p>
                        <span
                          className="text-xs px-2 py-0.5 rounded-full border font-medium"
                          style={{ color: RISK_COLORS[a.level], borderColor: `${RISK_COLORS[a.level]}40`, background: `${RISK_COLORS[a.level]}15` }}
                        >
                          {a.level}
                        </span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-600" />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {stats?.total_analyses === 0 && (
              <div className="glass-card p-12 text-center">
                <Zap className="w-12 h-12 text-cyan-500/30 mx-auto mb-4" />
                <p className="text-white font-semibold text-lg mb-2">No analyses yet</p>
                <p className="text-slate-400 text-sm mb-6">Run your first 4-agent risk analysis to see your dashboard populate</p>
                <button onClick={() => setActiveTab('analyze')} className="btn-primary mx-auto">
                  Run First Analysis
                </button>
              </div>
            )}
          </div>
        )}

        {/* ANALYZE TAB */}
        {activeTab === 'analyze' && (
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left: Form */}
            <div className="space-y-5">
              <div className="glass-card p-6">
                <h2 className="text-white font-bold text-lg mb-1">Run Risk Analysis</h2>
                <p className="text-slate-400 text-sm mb-6">LangGraph orchestrates all 4 agents and returns a unified risk report</p>

                {/* Quick select */}
                <div className="mb-5">
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mb-3">Quick Select</p>
                  <div className="grid grid-cols-2 gap-2">
                    {companies.map((c) => (
                      <button
                        key={c.ticker}
                        onClick={() => { setSelectedCompany(c); setCustomCompany(''); setCustomTicker('') }}
                        className={`p-3 rounded-xl text-left border transition-all text-xs
                          ${selectedCompany?.ticker === c.ticker && !customCompany
                            ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-300'
                            : 'bg-white/5 border-white/5 text-slate-300 hover:bg-white/10'}`}
                      >
                        <p className="font-semibold">{c.name}</p>
                        <p className="text-slate-500 mt-0.5">{c.ticker} · {c.sector}</p>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="border-t border-white/5 pt-5">
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mb-3">Or Enter Custom</p>
                  <div className="space-y-3">
                    <input value={customCompany} onChange={(e) => { setCustomCompany(e.target.value); setSelectedCompany(null) }}
                      placeholder="Company name" className="input-field text-sm" />
                    <div className="grid grid-cols-2 gap-3">
                      <input value={customTicker} onChange={(e) => setCustomTicker(e.target.value)}
                        placeholder="Ticker (e.g. AAPL)" className="input-field text-sm" />
                      <input value={customSector} onChange={(e) => setCustomSector(e.target.value)}
                        placeholder="Sector" className="input-field text-sm" />
                    </div>
                  </div>
                </div>

                <div className="border-t border-white/5 pt-5 mt-5">
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-medium mb-2">Link RAG Collection (optional)</p>
                  <input value={collectionName} onChange={(e) => setCollectionName(e.target.value)}
                    placeholder="ChromaDB collection name for document RAG"
                    className="input-field text-sm" />
                </div>

                <button
                  onClick={runAnalysis}
                  disabled={analyzing}
                  className="btn-primary w-full mt-5 flex items-center justify-center gap-2 py-3.5"
                >
                  {analyzing ? <><Loader2 className="w-4 h-4 animate-spin" /> Running 4 Agents...</> : <><Play className="w-4 h-4" /> Run Full Risk Analysis</>}
                </button>

                {/* Real-time streaming agent indicators */}
                {analyzing && Object.keys(streamingAgents).length > 0 && (
                  <div className="mt-4">
                    <StreamingAgentIndicator agents={streamingAgents} />
                  </div>
                )}
              </div>
            </div>

            {/* Right: Results */}
            <div>
              {analysisResult ? (
                <div className="space-y-5">
                  {/* Score + Trust */}
                  <div className="glass-card p-6 flex flex-col items-center gap-4">
                    <div>
                      <p className="text-white font-bold text-xl text-center">{analysisResult.company}</p>
                      <p className="text-slate-400 text-sm text-center">{analysisResult.ticker}</p>
                    </div>
                    <div className="flex items-center gap-6 flex-wrap justify-center">
                      <RiskScoreGauge score={analysisResult.adjusted_risk_score || analysisResult.overall_risk_score} level={analysisResult.risk_level} />
                      {analysisResult.trust_score != null && (
                        <TrustScoreBadge score={analysisResult.trust_score} size={120} />
                      )}
                    </div>
                    {analysisResult.adjusted_risk_score && (
                      <p className="text-xs text-white/40 text-center">
                        Original: {analysisResult.overall_risk_score?.toFixed(1)} → Adjusted: {analysisResult.adjusted_risk_score?.toFixed(1)} (post-debate)
                      </p>
                    )}
                    <p className="text-slate-300 text-sm text-center leading-relaxed">{analysisResult.summary}</p>
                  </div>

                  <AgentAnalysisPanel
                    agents={analysisResult.agents}
                    scores={analysisResult.scores}
                    mcpCalls={analysisResult.mcp_calls}
                    techStackActive={analysisResult.tech_stack_active}
                    guardrails={analysisResult.guardrails}
                  />

                  {analysisResult.debate && (
                    <DebatePanel debate={analysisResult.debate} />
                  )}

                  {analysisResult.db_id && (
                    <ChatPanel
                      analysisId={analysisResult.db_id}
                      company={analysisResult.company}
                      riskLevel={analysisResult.risk_level}
                    />
                  )}
                </div>
              ) : (
                <div className="glass-card p-12 text-center h-full flex flex-col items-center justify-center gap-4">
                  <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
                    <Shield className="w-8 h-8 text-cyan-500/50" />
                  </div>
                  <div>
                    <p className="text-white font-semibold">Ready to Analyze</p>
                    <p className="text-slate-400 text-sm mt-1">Select a company and run the 4-agent pipeline</p>
                  </div>
                  <div className="flex flex-wrap justify-center gap-2 mt-2">
                    {['Market Risk', 'Sentiment', 'Financial RAG', 'Regulatory'].map((a) => (
                      <span key={a} className="text-xs px-2.5 py-1 rounded-lg bg-white/5 text-slate-400 border border-white/5">{a}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* RAG TAB */}
        {activeTab === 'rag' && (
          <div className="grid lg:grid-cols-2 gap-8">
            <div>
              <div className="mb-5">
                <h2 className="text-white font-bold text-lg">Advanced RAG Pipeline</h2>
                <p className="text-slate-400 text-sm mt-1">
                  Hybrid BM25 + dense retrieval → LLM re-ranking → GPT analysis. ChromaDB pre-loaded at startup.
                </p>
              </div>

              {/* Pre-loaded collection banner */}
              <div className="glass-card p-4 mb-4 border border-green-500/20">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <p className="text-green-400 text-xs font-semibold uppercase tracking-wider">Default Collection Active</p>
                </div>
                <p className="text-white text-sm font-mono">sample_financial_docs</p>
                <p className="text-slate-400 text-xs mt-1">
                  Auto-ingested at startup: TechCorp Annual Report · FinanceHub Risk Disclosure · BFSI Regulatory Framework
                </p>
              </div>

              {/* Pipeline steps */}
              <div className="glass-card p-5 mb-4 border border-pink-500/20">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-8 h-8 rounded-lg bg-pink-500/15 border border-pink-500/30 flex items-center justify-center">
                    <Database className="w-4 h-4 text-pink-400" />
                  </div>
                  <p className="text-white font-semibold text-sm">ChromaDB — Retrieval Pipeline</p>
                </div>
                <div className="space-y-2 text-xs text-slate-400">
                  {[
                    { step: '1', label: 'Ingestion', text: 'PDFs chunked into ~150-word segments, embedded with text-embedding-3-small, stored in ChromaDB with cosine similarity index' },
                    { step: '2', label: 'Hybrid Retrieval', text: 'BM25 sparse keyword search + ChromaDB dense vector search run in parallel. Scores normalized and combined (60% dense, 40% BM25)' },
                    { step: '3', label: 'LLM Re-ranking', text: 'Top-8 candidates sent to GPT-4o-mini in a single batch prompt. GPT scores each chunk 0-10 for relevance, top-4 selected' },
                    { step: '4', label: 'Augmented Analysis', text: 'Re-ranked chunks injected as context into Financial Report Agent prompt. GPT generates risk assessment grounded in document evidence' },
                  ].map(({ step, label, text }) => (
                    <div key={step} className="flex items-start gap-3">
                      <span className="w-5 h-5 rounded-full bg-pink-500/20 border border-pink-500/30 text-pink-400 flex items-center justify-center flex-shrink-0 font-bold text-xs">{step}</span>
                      <div>
                        <span className="text-slate-300 font-medium">{label}: </span>
                        <span>{text}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* BM25 explanation */}
              <div className="glass-card p-4 border border-orange-500/20">
                <p className="text-orange-400 text-xs font-semibold uppercase tracking-wider mb-2">Why Hybrid Search?</p>
                <div className="space-y-1.5 text-xs text-slate-400">
                  {[
                    'Dense search excels at semantic meaning ("what is the credit risk exposure?")',
                    'BM25 excels at exact keywords ("Basel III", "SOX 404", "IFRS 9", "NIM")',
                    'Financial documents have precise regulatory terminology — BM25 recovers what dense misses',
                    'Weighted combination outperforms either method alone by ~15-20% recall@5',
                  ].map((s) => (
                    <div key={s} className="flex items-start gap-2">
                      <span className="text-orange-400 mt-0.5">→</span>
                      <span>{s}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <PDFUpload onDocumentUploaded={(col) => setCollectionName(col)} />
          </div>
        )}

        {/* HISTORY TAB */}
        {activeTab === 'history' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-white font-bold text-lg">Analysis History</h2>
              <span className="text-slate-400 text-sm">{history.length} analyses</span>
            </div>
            {history.length === 0 ? (
              <div className="glass-card p-12 text-center">
                <p className="text-slate-400">No analyses yet — run one from the Analyze tab</p>
              </div>
            ) : (
              <div className="space-y-3">
                {history.map((h) => (
                  <motion.div key={h.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="glass-card p-5 hover:bg-white/8 transition-colors">
                    <div className="flex flex-wrap items-start gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <p className="text-white font-semibold">{h.company}</p>
                          <span className="text-slate-500 text-sm">{h.ticker}</span>
                          <span
                            className="text-xs px-2 py-0.5 rounded-full border font-medium"
                            style={{ color: RISK_COLORS[h.risk_level], borderColor: `${RISK_COLORS[h.risk_level]}40`, background: `${RISK_COLORS[h.risk_level]}15` }}
                          >
                            {h.risk_level}
                          </span>
                        </div>
                        <p className="text-slate-500 text-xs">{new Date(h.created_at).toLocaleString()}</p>
                      </div>
                      <div className="flex gap-4 text-xs">
                        {[
                          { label: 'Overall', val: h.overall_score, color: RISK_COLORS[h.risk_level] },
                          { label: 'Market', val: h.market, color: '#06b6d4' },
                          { label: 'Sentiment', val: h.sentiment, color: '#8b5cf6' },
                          { label: 'Financial', val: h.financial, color: '#3b82f6' },
                          { label: 'Compliance', val: h.compliance, color: '#22c55e' },
                        ].map(({ label, val, color }) => (
                          <div key={label} className="text-center">
                            <p className="font-bold" style={{ color }}>{val?.toFixed(1)}</p>
                            <p className="text-slate-500">{label}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
