import { Shield } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="border-t border-white/5 py-12 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
              <Shield className="w-4 h-4 text-white" />
            </div>
            <div>
              <span className="font-bold text-white">BFSI</span>
              <span className="gradient-text font-bold"> RiskAI</span>
            </div>
          </div>

          <div className="flex flex-wrap justify-center gap-6 text-sm text-slate-400">
            <span>LangGraph · LangChain · GPT-4o · FastAPI · ChromaDB · MCP · SQLAlchemy · JWT</span>
          </div>

          <div className="text-slate-500 text-xs">
            Built for deployment on Render + Vercel
          </div>
        </div>
      </div>
    </footer>
  )
}
