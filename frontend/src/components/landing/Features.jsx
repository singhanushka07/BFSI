import { motion } from 'framer-motion'
import { TrendingUp, MessageSquare, FileText, Shield, Database, Zap, Lock, BarChart3 } from 'lucide-react'

const AGENTS = [
  {
    icon: TrendingUp,
    color: 'cyan',
    title: 'Market Risk Agent',
    badge: 'LangGraph Node',
    description: 'Analyzes stock volatility, Value-at-Risk (VaR), beta exposure, and market sensitivity using quantitative models powered by LangChain chains.',
    metrics: ['30-day Volatility', 'VaR (95%)', 'Beta', 'P/E Ratio'],
  },
  {
    icon: MessageSquare,
    color: 'violet',
    title: 'Sentiment Analysis Agent',
    badge: 'LangGraph Node',
    description: 'Processes real-time news headlines using GPT-4o to extract sentiment signals, reputational risk indicators, and investor confidence trends.',
    metrics: ['News Sentiment Score', 'Positive/Negative Ratio', 'Source Credibility', 'Trend Direction'],
  },
  {
    icon: FileText,
    color: 'blue',
    title: 'Financial Report Agent',
    badge: 'LangGraph + RAG',
    description: 'Uses ChromaDB-powered RAG to semantically search uploaded financial PDFs — reducing manual analysis by ~80% through intelligent retrieval and contextual LLM reasoning.',
    metrics: ['Current Ratio', 'Debt-to-Equity', 'ROE / ROA', 'Revenue Trends'],
  },
  {
    icon: Shield,
    color: 'green',
    title: 'Regulatory Compliance Agent',
    badge: 'LangGraph Node',
    description: 'Checks corporate adherence to Basel III, AML/KYC, Dodd-Frank, GDPR, MiFID II, and 8 other critical BFSI regulatory frameworks.',
    metrics: ['Basel III Capital', 'AML/KYC Status', 'GDPR Compliance', 'SOX Controls'],
  },
]

const PLATFORM_FEATURES = [
  {
    icon: Database,
    color: 'cyan',
    title: 'ChromaDB RAG Pipeline',
    description: 'Semantic vector search over uploaded financial PDFs. Chunks, embeds, and retrieves relevant context for LLM reasoning.',
  },
  {
    icon: Zap,
    color: 'amber',
    title: 'MCP Tool Layer',
    description: 'Model Context Protocol server exposes financial data tools that agents call — market data, news feeds, regulatory rules, and RAG queries.',
  },
  {
    icon: Lock,
    color: 'violet',
    title: 'JWT-Secured REST APIs',
    description: 'FastAPI + SQLAlchemy + SQLite backend with full JWT authentication, protected routes, and user-scoped analysis history.',
  },
  {
    icon: BarChart3,
    color: 'blue',
    title: 'Analytics Dashboard',
    description: 'Interactive charts for risk score trends, agent breakdowns, historical analysis, and real-time risk scoring visualization.',
  },
]

const colorMap = {
  cyan: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/30 text-cyan-400',
  violet: 'from-violet-500/20 to-violet-500/5 border-violet-500/30 text-violet-400',
  blue: 'from-blue-500/20 to-blue-500/5 border-blue-500/30 text-blue-400',
  green: 'from-green-500/20 to-green-500/5 border-green-500/30 text-green-400',
  amber: 'from-amber-500/20 to-amber-500/5 border-amber-500/30 text-amber-400',
}

export default function Features() {
  return (
    <section id="features" className="py-28 px-6 relative">
      <div className="max-w-7xl mx-auto">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <span className="inline-block px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-sm font-medium mb-4">
            Core Platform Features
          </span>
          <h2 className="text-4xl lg:text-5xl font-extrabold text-white mb-4">
            4 Specialized AI Agents,
            <br />
            <span className="gradient-text">One Unified Platform</span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Each agent is a dedicated LangGraph node with its own LangChain pipeline, tools, and risk scoring model — orchestrated together by the LangGraph state machine.
          </p>
        </motion.div>

        {/* Agent Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-20">
          {AGENTS.map((agent, i) => {
            const Icon = agent.icon
            const colors = colorMap[agent.color]
            return (
              <motion.div
                key={agent.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className={`glass-card-hover bg-gradient-to-br p-6 ${colors} border`}
              >
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colors} border flex items-center justify-center flex-shrink-0`}>
                    <Icon className={`w-6 h-6 ${colors.split(' ').find(c => c.startsWith('text-'))}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <h3 className="text-white font-bold text-lg">{agent.title}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full bg-white/5 border ${colors.split(' ').find(c => c.startsWith('border-'))} ${colors.split(' ').find(c => c.startsWith('text-'))}`}>
                        {agent.badge}
                      </span>
                    </div>
                    <p className="text-slate-400 text-sm leading-relaxed mb-4">{agent.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {agent.metrics.map((m) => (
                        <span key={m} className="text-xs px-2.5 py-1 rounded-lg bg-white/5 text-slate-300 border border-white/5">
                          {m}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Platform Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h3 className="text-2xl font-bold text-white mb-2">Platform Infrastructure</h3>
          <p className="text-slate-400">Built for production — secure, scalable, and deployment-ready</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {PLATFORM_FEATURES.map((f, i) => {
            const Icon = f.icon
            const colors = colorMap[f.color]
            return (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="glass-card-hover p-5"
              >
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${colors} border flex items-center justify-center mb-4`}>
                  <Icon className={`w-5 h-5 ${colors.split(' ').find(c => c.startsWith('text-'))}`} />
                </div>
                <h4 className="text-white font-semibold mb-2">{f.title}</h4>
                <p className="text-slate-400 text-sm leading-relaxed">{f.description}</p>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
