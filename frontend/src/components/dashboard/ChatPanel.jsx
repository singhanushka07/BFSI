import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageCircle, Send, Trash2, Bot, User, Loader2, Sparkles } from 'lucide-react'
import { chatAPI } from '../../api/client'
import toast from 'react-hot-toast'

const SUGGESTED_QUESTIONS = [
  'Explain the market risk score',
  'Why is the sentiment score this value?',
  'What if debt-to-equity ratio was lower?',
  'Compare all agent assessments',
  'What are the key risk drivers?',
]

export default function ChatPanel({ analysisId, company, riskLevel }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    if (analysisId) {
      chatAPI.getHistory(analysisId)
        .then((res) => setMessages(res.data || []))
        .catch(() => {})
    }
  }, [analysisId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    const msg = (text || input).trim()
    if (!msg || isLoading) return

    setMessages((prev) => [...prev, { role: 'user', content: msg, created_at: new Date().toISOString() }])
    setInput('')
    setIsLoading(true)

    try {
      const res = await chatAPI.sendMessage({ analysis_id: analysisId, message: msg })
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: res.data.response, created_at: new Date().toISOString() },
      ])
    } catch (err) {
      toast.error('Failed to get response')
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.', created_at: new Date().toISOString() },
      ])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const clearHistory = async () => {
    try {
      await chatAPI.clearHistory(analysisId)
      setMessages([])
      toast.success('Chat history cleared')
    } catch {
      toast.error('Failed to clear history')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const riskColor = {
    LOW: '#22c55e', MEDIUM: '#f59e0b', HIGH: '#f97316', CRITICAL: '#ef4444',
  }[riskLevel] || '#06b6d4'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="glass-card mt-6 flex flex-col"
      style={{ height: '520px' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-cyan-500/10 flex items-center justify-center">
            <MessageCircle size={18} className="text-cyan-400" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Risk Chat</h3>
            <div className="flex items-center gap-2">
              <span className="text-xs text-white/50">{company}</span>
              <span
                className="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                style={{ background: `${riskColor}20`, color: riskColor }}
              >
                {riskLevel}
              </span>
            </div>
          </div>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearHistory}
            className="p-2 rounded-lg hover:bg-white/5 text-white/30 hover:text-white/60 transition-colors"
            title="Clear chat"
          >
            <Trash2 size={16} />
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Sparkles size={32} className="text-cyan-400/30 mb-3" />
            <p className="text-sm text-white/40 mb-4">
              Ask questions about this risk analysis
            </p>
            <div className="flex flex-wrap gap-2 justify-center max-w-md">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => sendMessage(q)}
                  className="text-xs px-3 py-1.5 rounded-full bg-white/5 text-white/50 hover:bg-cyan-500/10 hover:text-cyan-400 border border-white/10 hover:border-cyan-500/30 transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role === 'assistant' && (
                <div className="w-7 h-7 rounded-full bg-cyan-500/10 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot size={14} className="text-cyan-400" />
                </div>
              )}
              <div
                className={`max-w-[80%] p-3 rounded-xl text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-cyan-600/20 text-white/90 border border-cyan-500/30'
                    : 'bg-white/5 text-white/80 border border-white/10'
                }`}
              >
                {msg.content}
              </div>
              {msg.role === 'user' && (
                <div className="w-7 h-7 rounded-full bg-cyan-500/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <User size={14} className="text-cyan-300" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <div className="w-7 h-7 rounded-full bg-cyan-500/10 flex items-center justify-center flex-shrink-0">
              <Bot size={14} className="text-cyan-400" />
            </div>
            <div className="bg-white/5 border border-white/10 p-3 rounded-xl flex items-center gap-2">
              <Loader2 size={14} className="animate-spin text-cyan-400" />
              <span className="text-xs text-white/40">Thinking...</span>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about this risk analysis..."
            className="input-field flex-1 text-sm"
            disabled={isLoading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 rounded-lg bg-cyan-600/20 text-cyan-400 hover:bg-cyan-600/30 border border-cyan-500/30 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </motion.div>
  )
}
