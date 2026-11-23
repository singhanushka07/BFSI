import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const stored = localStorage.getItem('bfsi-auth')
  if (stored) {
    const { state } = JSON.parse(stored)
    if (state?.token) {
      config.headers.Authorization = `Bearer ${state.token}`
    }
  }
  return config
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('bfsi-auth')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Auth
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => {
    const form = new URLSearchParams()
    form.append('username', data.email)
    form.append('password', data.password)
    return api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
  },
  me: () => api.get('/auth/me'),
}

// Agents
export const agentsAPI = {
  analyze: (data) => api.post('/agents/analyze', data),
  analyzeStream: (data, onEvent) => {
    const stored = localStorage.getItem('bfsi-auth')
    const token = stored ? JSON.parse(stored)?.state?.token : null
    if (!token) return Promise.reject(new Error('Not authenticated'))

    const url = `${BASE_URL}/agents/analyze-stream?token=${encodeURIComponent(token)}`
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(async (response) => {
      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: 'Stream failed' }))
        throw new Error(err.detail || 'Stream failed')
      }
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let finalResult = null

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        let eventType = null
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.slice(7).trim()
          } else if (line.startsWith('data: ') && eventType) {
            try {
              const eventData = JSON.parse(line.slice(6))
              if (eventType === 'analysis_complete') finalResult = eventData
              if (onEvent) onEvent(eventType, eventData)
            } catch {}
            eventType = null
          }
        }
      }
      return finalResult
    })
  },
  history: () => api.get('/agents/history'),
  detail: (id) => api.get(`/agents/history/${id}`),
  companies: () => api.get('/agents/companies'),
}

// Chat
export const chatAPI = {
  sendMessage: (data) => api.post('/chat/message', data),
  getHistory: (analysisId) => api.get(`/chat/history/${analysisId}`),
  clearHistory: (analysisId) => api.delete(`/chat/history/${analysisId}`),
}

// RAG
export const ragAPI = {
  upload: (formData) => api.post('/rag/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  query: (data) => api.post('/rag/query', data),
  documents: () => api.get('/rag/documents'),
  deleteDoc: (id) => api.delete(`/rag/documents/${id}`),
}

// Dashboard
export const dashboardAPI = {
  stats: () => api.get('/dashboard/stats'),
  riskTrend: (company, days = 30) => api.get(`/dashboard/risk-trend/${encodeURIComponent(company)}?days=${days}`),
  overview: () => api.get('/dashboard/overview'),
}

// MCP
export const mcpAPI = {
  tools: () => api.get('/mcp/tools'),
  invoke: (tool_name, parameters) => api.post('/mcp/invoke', { tool_name, parameters }),
}

export default api
