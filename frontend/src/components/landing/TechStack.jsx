import { motion } from 'framer-motion'

const TECH = [
  {
    name: 'LangGraph',
    role: 'Multi-Agent Orchestration',
    desc: 'State machine that routes, coordinates, and aggregates all 4 risk agent nodes.',
    color: '#22d3ee',
    icon: '⬡',
  },
  {
    name: 'LangChain',
    role: 'LLM Chain Framework',
    desc: 'Powers prompt templates, output parsers, and LLM chains inside each agent node.',
    color: '#06b6d4',
    icon: '⛓',
  },
  {
    name: 'GPT-4o',
    role: 'Large Language Model',
    desc: 'OpenAI flagship model for financial analysis, sentiment reasoning, and compliance checks.',
    color: '#10b981',
    icon: '◎',
  },
  {
    name: 'FastAPI',
    role: 'REST API Backend',
    desc: 'Async Python web framework serving all endpoints with OpenAPI docs at /api/docs.',
    color: '#06b6d4',
    icon: '⚡',
  },
  {
    name: 'ChromaDB',
    role: 'Vector Database (RAG)',
    desc: 'Persistent vector store for semantic search over financial PDF embeddings.',
    color: '#ec4899',
    icon: '◈',
  },
  {
    name: 'MCP',
    role: 'Model Context Protocol',
    desc: 'Tool-serving layer that exposes financial data APIs for agents to call via structured protocol.',
    color: '#f59e0b',
    icon: '⬡',
  },
  {
    name: 'SQLAlchemy',
    role: 'Database ORM',
    desc: 'Maps User, RiskAnalysis, and UploadedDocument models to SQLite with full CRUD.',
    color: '#f97316',
    icon: '▦',
  },
  {
    name: 'SQLite',
    role: 'Persistent Storage',
    desc: 'Zero-config relational database storing users, analysis history, and document metadata.',
    color: '#fb923c',
    icon: '▣',
  },
  {
    name: 'JWT Auth',
    role: 'Authentication',
    desc: 'python-jose + passlib bcrypt — secure token-based auth protecting all API routes.',
    color: '#a855f7',
    icon: '🔐',
  },
  {
    name: 'React + Vite',
    role: 'Frontend Framework',
    desc: 'Lightning-fast React SPA with Vite bundler, Tailwind CSS, Framer Motion, and Recharts.',
    color: '#38bdf8',
    icon: '⚛',
  },
  {
    name: 'Recharts',
    role: 'Data Visualization',
    desc: 'Composable chart library powering the risk trend, agent breakdown, and analytics dashboards.',
    color: '#818cf8',
    icon: '📊',
  },
  {
    name: 'Render + Vercel',
    role: 'Cloud Deployment',
    desc: 'Render free tier for FastAPI backend; Vercel for React frontend — both free to deploy.',
    color: '#64748b',
    icon: '☁',
  },
]

export default function TechStack() {
  return (
    <section id="tech-stack" className="py-28 px-6 relative">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent" />
      </div>
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-sm font-medium mb-4">
            Technology Stack
          </span>
          <h2 className="text-4xl lg:text-5xl font-extrabold text-white mb-4">
            Every Technology,
            <span className="gradient-text"> Front and Center</span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            12 production-grade technologies working in harmony — each with a specific, non-redundant role in the platform.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {TECH.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
              className="glass-card-hover p-5 group"
            >
              {/* Icon + Name row */}
              <div className="flex items-center gap-3 mb-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-lg font-bold border"
                  style={{
                    background: `${t.color}18`,
                    borderColor: `${t.color}44`,
                    color: t.color,
                  }}
                >
                  {t.icon}
                </div>
                <div>
                  <p className="text-white font-bold text-sm leading-tight">{t.name}</p>
                  <p className="text-xs leading-tight" style={{ color: t.color }}>{t.role}</p>
                </div>
              </div>
              <p className="text-slate-400 text-xs leading-relaxed">{t.desc}</p>

              {/* Hover glow bar */}
              <div
                className="mt-4 h-0.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                style={{ background: `linear-gradient(to right, ${t.color}60, ${t.color}10)` }}
              />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
