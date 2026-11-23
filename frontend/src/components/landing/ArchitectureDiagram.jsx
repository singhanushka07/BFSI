import { motion } from 'framer-motion'
import { useState } from 'react'

const NODE_DEFS = {
  user:       { label: 'User / Browser',      sub: 'React + Vite',         color: '#94a3b8', bg: 'rgba(148,163,184,0.12)', border: 'rgba(148,163,184,0.4)' },
  jwt:        { label: 'JWT Auth',             sub: 'FastAPI + python-jose',color: '#a855f7', bg: 'rgba(168,85,247,0.12)',  border: 'rgba(168,85,247,0.4)' },
  fastapi:    { label: 'FastAPI',              sub: 'REST API Gateway',     color: '#06b6d4', bg: 'rgba(6,182,212,0.12)',   border: 'rgba(6,182,212,0.4)' },
  mcp:        { label: 'MCP Server',           sub: 'Tool Protocol Layer',  color: '#f59e0b', bg: 'rgba(245,158,11,0.12)',  border: 'rgba(245,158,11,0.4)' },
  langgraph:  { label: 'LangGraph',            sub: 'Agent Orchestrator',   color: '#22d3ee', bg: 'rgba(34,211,238,0.12)',  border: 'rgba(34,211,238,0.4)' },
  market:     { label: 'Market Risk',          sub: 'LangChain Agent',      color: '#06b6d4', bg: 'rgba(6,182,212,0.10)',   border: 'rgba(6,182,212,0.35)' },
  sentiment:  { label: 'Sentiment',            sub: 'LangChain Agent',      color: '#8b5cf6', bg: 'rgba(139,92,246,0.10)',  border: 'rgba(139,92,246,0.35)' },
  financial:  { label: 'Financial Report',     sub: 'LangChain + RAG',      color: '#3b82f6', bg: 'rgba(59,130,246,0.10)',  border: 'rgba(59,130,246,0.35)' },
  regulatory: { label: 'Regulatory',           sub: 'LangChain Agent',      color: '#22c55e', bg: 'rgba(34,197,94,0.10)',   border: 'rgba(34,197,94,0.35)' },
  gpt:        { label: 'GPT-4o',               sub: 'OpenAI LLM',           color: '#10b981', bg: 'rgba(16,185,129,0.12)',  border: 'rgba(16,185,129,0.4)' },
  chromadb:   { label: 'ChromaDB',             sub: 'Vector Store (RAG)',    color: '#ec4899', bg: 'rgba(236,72,153,0.12)',  border: 'rgba(236,72,153,0.4)' },
  sqlite:     { label: 'SQLite / SQLAlchemy',  sub: 'Persistent Storage',   color: '#f97316', bg: 'rgba(249,115,22,0.12)',  border: 'rgba(249,115,22,0.4)' },
}

const FLOW_STEPS = [
  { id: 1, label: 'Request enters', desc: 'User submits analysis request from React dashboard' },
  { id: 2, label: 'JWT Verified', desc: 'FastAPI middleware validates JWT bearer token' },
  { id: 3, label: 'MCP Tools Ready', desc: 'MCP server exposes financial data tools to agents' },
  { id: 4, label: 'LangGraph Runs', desc: 'Orchestrator dispatches 4 agent nodes in sequence' },
  { id: 5, label: 'LLM Reasoning', desc: 'Each agent calls GPT-4o via LangChain for analysis' },
  { id: 6, label: 'RAG Retrieval', desc: 'Financial Report agent queries ChromaDB vector store' },
  { id: 7, label: 'Scores Aggregated', desc: 'Weighted risk scores merged into final report' },
  { id: 8, label: 'Stored + Returned', desc: 'Results saved to SQLite and streamed to dashboard' },
]

function Node({ id, x, y, active, onClick }) {
  const n = NODE_DEFS[id]
  return (
    <motion.g
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.3 }}
      style={{ cursor: 'pointer' }}
      onClick={() => onClick(id)}
    >
      <motion.rect
        x={x - 62} y={y - 26}
        width={124} height={52}
        rx={10}
        fill={n.bg}
        stroke={active ? n.color : n.border}
        strokeWidth={active ? 2 : 1}
        animate={{ stroke: active ? n.color : n.border }}
      />
      {active && (
        <motion.rect
          x={x - 64} y={y - 28}
          width={128} height={56}
          rx={12}
          fill="none"
          stroke={n.color}
          strokeWidth={1}
          opacity={0.4}
          animate={{ opacity: [0.4, 0.8, 0.4] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
        />
      )}
      <text x={x} y={y - 5} textAnchor="middle" fill={n.color} fontSize={11} fontWeight="600" fontFamily="Inter, sans-serif">{n.label}</text>
      <text x={x} y={y + 11} textAnchor="middle" fill="rgba(148,163,184,0.8)" fontSize={9} fontFamily="Inter, sans-serif">{n.sub}</text>
    </motion.g>
  )
}

function Arrow({ x1, y1, x2, y2, color = 'rgba(6,182,212,0.35)', dashed = false, animated = false }) {
  const dx = x2 - x1
  const dy = y2 - y1
  const angle = Math.atan2(dy, dx) * 180 / Math.PI
  const len = Math.sqrt(dx * dx + dy * dy)
  const ex = x1 + dx * ((len - 14) / len)
  const ey = y1 + dy * ((len - 14) / len)

  return (
    <g>
      <motion.line
        x1={x1} y1={y1} x2={ex} y2={ey}
        stroke={color}
        strokeWidth={1.5}
        strokeDasharray={dashed ? '5,4' : 'none'}
        initial={animated ? { pathLength: 0 } : {}}
        animate={animated ? { pathLength: 1 } : {}}
        transition={animated ? { duration: 1, delay: 0.5, repeat: Infinity, repeatDelay: 2 } : {}}
      />
      <polygon
        points={`${x2},${y2} ${x2 - 8},${y2 - 4} ${x2 - 8},${y2 + 4}`}
        fill={color}
        transform={`rotate(${angle}, ${x2}, ${y2})`}
      />
    </g>
  )
}

const LAYOUT = {
  user:       [150, 60],
  jwt:        [420, 60],
  fastapi:    [690, 60],
  mcp:        [960, 60],
  langgraph:  [560, 175],
  market:     [200, 300],
  sentiment:  [400, 300],
  financial:  [600, 300],
  regulatory: [800, 300],
  gpt:        [560, 420],
  chromadb:   [760, 420],
  sqlite:     [360, 420],
}

export default function ArchitectureDiagram() {
  const [activeNode, setActiveNode] = useState(null)
  const [activeStep, setActiveStep] = useState(null)

  const handleNode = (id) => setActiveNode(activeNode === id ? null : id)

  return (
    <section id="architecture" className="py-28 px-6 relative overflow-hidden">
      {/* Subtle bg glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-cyan-500/4 rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-sm font-medium mb-4">
            System Architecture
          </span>
          <h2 className="text-4xl lg:text-5xl font-extrabold text-white mb-4">
            How It All
            <span className="gradient-text"> Works Together</span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Click any node to inspect it. Every component is wired together — from the React frontend through FastAPI, MCP, LangGraph, agents, and back to the database.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-10 items-start">
          {/* Diagram */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="lg:col-span-2 glass-card p-4 overflow-x-auto"
          >
            <svg
              viewBox="0 0 1100 500"
              className="w-full min-w-[600px]"
              style={{ minHeight: 340 }}
            >
              {/* Layer labels */}
              <text x={20} y={68} fill="rgba(148,163,184,0.4)" fontSize={9} fontFamily="Inter" fontWeight="600" letterSpacing="1">REQUEST LAYER</text>
              <text x={20} y={183} fill="rgba(148,163,184,0.4)" fontSize={9} fontFamily="Inter" fontWeight="600" letterSpacing="1">ORCHESTRATION</text>
              <text x={20} y={308} fill="rgba(148,163,184,0.4)" fontSize={9} fontFamily="Inter" fontWeight="600" letterSpacing="1">AGENT NODES</text>
              <text x={20} y={428} fill="rgba(148,163,184,0.4)" fontSize={9} fontFamily="Inter" fontWeight="600" letterSpacing="1">DATA LAYER</text>

              {/* Horizontal dividers */}
              {[95, 210, 365].map(y => (
                <line key={y} x1={0} y1={y} x2={1100} y2={y} stroke="rgba(255,255,255,0.04)" strokeWidth={1} />
              ))}

              {/* Arrows — Request Layer */}
              <Arrow x1={213} y1={60} x2={357} y2={60} color="rgba(168,85,247,0.5)" />
              <Arrow x1={483} y1={60} x2={627} y2={60} color="rgba(6,182,212,0.5)" />
              <Arrow x1={753} y1={60} x2={897} y2={60} color="rgba(245,158,11,0.5)" />

              {/* FastAPI → LangGraph */}
              <Arrow x1={690} y1={87} x2={590} y2={148} color="rgba(6,182,212,0.5)" />
              {/* MCP → LangGraph */}
              <Arrow x1={920} y1={87} x2={630} y2={150} color="rgba(245,158,11,0.4)" dashed />

              {/* LangGraph → Agents */}
              <Arrow x1={500} y1={200} x2={250} y2={273} color="rgba(6,182,212,0.4)" />
              <Arrow x1={530} y1={200} x2={420} y2={273} color="rgba(139,92,246,0.4)" />
              <Arrow x1={580} y1={200} x2={600} y2={273} color="rgba(59,130,246,0.4)" />
              <Arrow x1={610} y1={200} x2={780} y2={273} color="rgba(34,197,94,0.4)" />

              {/* Agents → GPT */}
              {[[200, 327], [400, 327], [600, 327], [800, 327]].map(([x, y], i) => (
                <Arrow key={i} x1={x} y1={y} x2={540} y2={393} color="rgba(16,185,129,0.3)" dashed />
              ))}

              {/* Financial → ChromaDB */}
              <Arrow x1={630} y1={327} x2={730} y2={393} color="rgba(236,72,153,0.4)" animated />

              {/* FastAPI → SQLite */}
              <Arrow x1={660} y1={87} x2={380} y2={393} color="rgba(249,115,22,0.3)" dashed />

              {/* Render all nodes */}
              {Object.entries(LAYOUT).map(([id, [x, y]]) => (
                <Node key={id} id={id} x={x} y={y} active={activeNode === id} onClick={handleNode} />
              ))}
            </svg>

            {/* Node info tooltip */}
            {activeNode && (
              <motion.div
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-3 px-4 py-3 rounded-xl bg-white/5 border border-white/10 flex items-center gap-3"
              >
                <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: NODE_DEFS[activeNode]?.color }} />
                <div>
                  <span className="text-white font-semibold text-sm">{NODE_DEFS[activeNode]?.label}</span>
                  <span className="text-slate-400 text-sm"> — {NODE_DEFS[activeNode]?.sub}</span>
                </div>
              </motion.div>
            )}
          </motion.div>

          {/* Flow steps */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="space-y-2"
          >
            <p className="text-white font-bold text-lg mb-4">Request Flow</p>
            {FLOW_STEPS.map((step) => (
              <div
                key={step.id}
                onMouseEnter={() => setActiveStep(step.id)}
                onMouseLeave={() => setActiveStep(null)}
                className={`flex gap-3 p-3 rounded-xl border cursor-default transition-all duration-200
                  ${activeStep === step.id ? 'bg-cyan-500/10 border-cyan-500/40' : 'bg-white/3 border-white/5'}`}
              >
                <div className={`w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold
                  ${activeStep === step.id ? 'bg-cyan-500 text-navy-950' : 'bg-white/10 text-slate-400'}`}>
                  {step.id}
                </div>
                <div>
                  <p className={`text-sm font-semibold ${activeStep === step.id ? 'text-cyan-300' : 'text-slate-300'}`}>{step.label}</p>
                  <p className="text-slate-500 text-xs leading-relaxed">{step.desc}</p>
                </div>
              </div>
            ))}

            {/* Legend */}
            <div className="pt-4 space-y-2">
              <p className="text-slate-500 text-xs font-medium uppercase tracking-wider">Legend</p>
              {[
                { color: 'rgba(6,182,212,0.6)', label: 'Synchronous call', dashed: false },
                { color: 'rgba(6,182,212,0.4)', label: 'Tool / async call', dashed: true },
                { color: 'rgba(236,72,153,0.7)', label: 'RAG vector retrieval', animated: true },
              ].map((l) => (
                <div key={l.label} className="flex items-center gap-3">
                  <svg width={36} height={12}>
                    <line x1={0} y1={6} x2={36} y2={6} stroke={l.color} strokeWidth={2} strokeDasharray={l.dashed ? '4,3' : 'none'} />
                  </svg>
                  <span className="text-slate-400 text-xs">{l.label}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
