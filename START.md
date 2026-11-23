# BFSI Multi-Agent Financial Risk Assessment Platform

## Key Features

- **6 AI Agents** — Market Risk, Sentiment, Financial Report (RAG), Regulatory Compliance, Devil's Advocate, Judge — orchestrated by LangGraph
- **SSE Real-Time Streaming** — Watch agents analyze live via Server-Sent Events
- **Multi-Agent Debate** — Devil's Advocate challenges findings, Judge resolves disagreements with adjusted scores
- **Guardrails + Hallucination Detection** — LLM validates each agent's output against source data with confidence scoring
- **Conversational Risk Chat** — Chat with any completed risk report, ask follow-up questions and what-if scenarios
- **Hybrid RAG Pipeline** — BM25 + dense vector search with LLM re-ranking over ChromaDB
- **MCP Tool Integration** — 7 Model Context Protocol tools for data access
- **Full-Stack** — FastAPI + React + Tailwind + Recharts + Framer Motion + Zustand + JWT Auth

## Quick Start

### Backend
```bash
cd backend
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload
# API docs: http://localhost:8000/api/docs
```

### Frontend
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
# Opens: http://localhost:5173
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agents/analyze` | POST | Synchronous full analysis |
| `/api/agents/analyze-stream?token=...` | POST | SSE streaming analysis (real-time) |
| `/api/chat/message` | POST | Chat with a completed analysis |
| `/api/chat/history/{id}` | GET | Get chat history |
| `/api/rag/upload` | POST | Upload PDF for RAG |
| `/api/health` | GET | Platform health check |
| `/api/docs` | GET | Swagger UI |

## Deployment (Free)

### Backend → Render
1. Push to GitHub
2. New Web Service on render.com → connect repo
3. Root Dir: `backend`, Build: `pip install -r requirements.txt`, Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add env var: `OPENAI_API_KEY`

### Frontend → Vercel
1. `cd frontend && npm run build`
2. `vercel --prod` or connect GitHub repo
3. Set `VITE_API_URL` to your Render backend URL
