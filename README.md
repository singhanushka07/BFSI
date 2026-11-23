# BFSI Multi-Agent Financial Risk Assessment Platform

An enterprise-grade, AI-powered financial risk analysis platform built for the **Banking, Financial Services & Insurance (BFSI)** sector. The platform orchestrates **6 specialized AI agents** through a LangGraph state machine, each running its own LangChain pipeline with GPT-4o-mini, to deliver comprehensive risk assessments with real-time streaming, multi-agent debate, hallucination guardrails, and conversational follow-up.

> **Live Tech Stack:** LangGraph | LangChain | GPT-4o-mini | FastAPI | ChromaDB | MCP | React | Tailwind CSS | SSE Streaming | JWT Auth

---

## Table of Contents

- [Business Case](#business-case)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [AI Agents](#ai-agents)
- [Tech Stack](#tech-stack)
- [Screenshots & Feature Walkthrough](#screenshots--feature-walkthrough)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Demo Credentials](#demo-credentials)
- [License](#license)

---

## Business Case

### The Problem

Financial institutions face a growing challenge: **risk assessment is fragmented across siloed teams**, each using different data sources, methods, and reporting formats. Manual analysis of market data, news sentiment, financial statements, and regulatory compliance is:

- **Slow** — a comprehensive risk report can take days to compile
- **Inconsistent** — different analysts produce different conclusions from the same data
- **Prone to blind spots** — no single analyst covers market risk, sentiment, financials, AND regulatory compliance
- **Difficult to audit** — the reasoning behind a risk score is often opaque

### The Solution

This platform replaces fragmented manual analysis with a **multi-agent AI system** that:

1. **Runs 4 specialized risk agents in parallel**, each covering a distinct risk domain
2. **Uses a Devil's Advocate agent** to challenge findings and expose blind spots
3. **Employs a Judge agent** to resolve disagreements and produce calibrated final scores
4. **Validates all outputs** through an automated guardrails and hallucination detection layer
5. **Grounds analysis in documents** via a Hybrid RAG pipeline (BM25 + dense vector search)
6. **Streams analysis in real-time** so stakeholders can watch agents work via SSE
7. **Enables follow-up conversation** — users can ask what-if questions about any completed report

### Who Is This For?

| Role | Use Case |
|------|----------|
| **Chief Risk Officers** | Unified risk dashboard across all dimensions |
| **Risk Analysts** | Automated first-pass analysis, freeing time for edge cases |
| **Compliance Officers** | Automated regulatory checks against Basel III, AML/KYC, GDPR, SOX, MiFID II |
| **Portfolio Managers** | Quick risk assessment of potential investments |
| **Audit Teams** | Transparent, traceable AI reasoning with guardrails validation |

---

## Key Features

### 1. Multi-Agent Orchestration (LangGraph)
A LangGraph state machine coordinates 6 AI agents in a defined pipeline. Each agent is a graph node with its own LangChain chain, tools, and scoring model. The orchestrator manages state transitions, error handling, and result aggregation.

### 2. Real-Time SSE Streaming
Watch agents analyze live. The backend streams Server-Sent Events as each agent starts, completes, and produces scores. The React frontend renders animated progress indicators in real-time.

### 3. Multi-Agent Debate System
After the 4 core agents complete their analysis:
- **Devil's Advocate Agent** — challenges assumptions, identifies contradictions, and stress-tests conclusions
- **Judge Agent** — evaluates each challenge, issues rulings (accepted / partially accepted / dismissed), and adjusts risk scores

### 4. Guardrails & Hallucination Detection
An LLM-powered validation layer checks every agent's output against its source data:
- Verifies numerical claims match MCP tool results
- Checks risk level assignments match computed scores
- Flags unsupported generalizations
- Produces a per-agent confidence score and an overall trust score

### 5. Hybrid RAG Pipeline (BM25 + Dense Vector Search)
Financial documents are processed through a 4-stage retrieval pipeline:
1. **Ingestion** — PDFs chunked into ~150-word segments, embedded with `text-embedding-3-small`, stored in ChromaDB
2. **Hybrid Retrieval** — BM25 sparse keyword search + ChromaDB dense vector search run in parallel (60% dense / 40% BM25)
3. **LLM Re-ranking** — Top-8 candidates sent to GPT-4o-mini for batch relevance scoring (0-10)
4. **Augmented Generation** — Top-4 re-ranked chunks injected as context into the Financial Report Agent's prompt

> **Why hybrid?** Dense search captures semantic meaning ("credit risk exposure") while BM25 captures exact regulatory terminology ("Basel III", "SOX 404", "IFRS 9") that semantic search alone misses.

### 6. MCP Tool Integration
7 Model Context Protocol tools provide structured data access to all agents:
- `get_stock_data` — Historical OHLCV price data
- `get_financial_metrics` — Key financial ratios (D/E, current ratio, ROE, ROA, beta, P/E)
- `get_news_sentiment` — News headlines with sentiment scores
- `get_regulatory_rules` — BFSI regulatory framework rules
- `rag_query` — Dense vector search over ChromaDB
- `hybrid_rag_search` — BM25 + dense hybrid search
- `rerank_chunks` — LLM batch re-ranking of retrieved chunks

Also includes a **FastMCP SDK server** for connecting to external MCP clients (Claude Desktop, Cursor, etc.).

### 7. Conversational Risk Chat
After analysis, users can chat with any completed report:
- Ask follow-up questions ("Explain the market risk score")
- Run what-if scenarios ("What if debt-to-equity was lower?")
- Compare agent assessments ("Compare all agent findings")
- Full chat history with context memory

### 8. Analytics Dashboard
Interactive dashboard with:
- Risk score trend charts (Recharts)
- Agent breakdown comparisons
- Risk distribution visualization
- Recent analysis history
- Real-time stat cards

---

## System Architecture

```
                        ┌─────────────────────┐
                        │   React + Vite      │
                        │   (Tailwind, Zustand)│
                        └────────┬────────────┘
                                 │ REST / SSE
                        ┌────────▼────────────┐
                        │  FastAPI Gateway     │
                        │  (JWT Auth, CORS)    │
                        └────────┬────────────┘
                    ┌────────────┼────────────────┐
                    │            │                 │
           ┌────────▼──┐  ┌─────▼──────┐  ┌──────▼──────┐
           │ MCP Server │  │  LangGraph │  │  SQLAlchemy │
           │ (7 tools)  │  │Orchestrator│  │  (SQLite)   │
           └────────────┘  └─────┬──────┘  └─────────────┘
                    ┌────────────┼────────────────┐
            ┌───────▼──┐ ┌──────▼──┐ ┌───────────▼──┐ ┌───────────┐
            │ Market   │ │Sentiment│ │  Financial   │ │Regulatory │
            │ Risk     │ │Analysis │ │  Report(RAG) │ │Compliance │
            └──────────┘ └─────────┘ └──────┬───────┘ └───────────┘
                                            │
                              ┌──────────────▼──────────────┐
                              │  ChromaDB Vector Store       │
                              │  (Hybrid BM25 + Dense + LLM │
                              │   Re-ranking)                │
                              └──────────────────────────────┘
                    ┌────────────────────────────────────────┐
                    │          Post-Analysis Pipeline         │
                    │  Aggregator → Guardrails → Devil's     │
                    │  Advocate → Judge → Final Report        │
                    └────────────────────────────────────────┘
```

### Request Flow

1. **User submits analysis** from React dashboard
2. **JWT middleware** validates bearer token
3. **FastAPI** routes request to streaming endpoint
4. **LangGraph orchestrator** dispatches agents sequentially
5. Each agent calls **MCP tools** for data, then **GPT-4o-mini** via LangChain for analysis
6. **Financial Report Agent** queries **ChromaDB** via hybrid RAG pipeline
7. **Aggregator** computes weighted risk scores (Market 30%, Sentiment 20%, Financial 30%, Compliance 20%)
8. **Guardrails** validates all agent outputs against source data
9. **Devil's Advocate** challenges findings; **Judge** issues final verdicts
10. Results saved to **SQLite** and streamed back to dashboard via **SSE**

---

## AI Agents

| # | Agent | Role | Key Metrics | Tools Used |
|---|-------|------|-------------|------------|
| 1 | **Market Risk** | Quantitative analysis of volatility, VaR, beta, and market exposure | 30-day Volatility, VaR (95%), Beta, P/E | `get_stock_data`, `get_financial_metrics` |
| 2 | **Sentiment Analysis** | News sentiment scoring and reputational risk assessment | Avg Sentiment Score, Positive/Negative ratio, Article count | `get_news_sentiment` |
| 3 | **Financial Report** | RAG-powered financial health analysis grounded in document evidence | Current Ratio, D/E, ROE, ROA, Revenue | `get_financial_metrics`, `hybrid_rag_search`, `rerank_chunks` |
| 4 | **Regulatory Compliance** | Checks against Basel III, AML/KYC, GDPR, SOX, MiFID II, Dodd-Frank, IFRS 9 | Violations, Warnings, Compliance Rate | `get_regulatory_rules` |
| 5 | **Devil's Advocate** | Challenges assumptions, finds contradictions between agents | Challenges (minor/major/critical), Contradictions | Receives all agent outputs |
| 6 | **Judge** | Resolves debate, issues rulings, adjusts scores | Verdicts, Adjusted Scores, Debate Impact | Receives agents + Devil's Advocate results |

**Plus:** Guardrails & Hallucination Detection (validates all outputs against source data, computes per-agent confidence scores and overall trust score)

---

## Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **FastAPI** | Async REST API framework with auto-generated Swagger docs |
| **LangGraph** | Multi-agent orchestration as a state machine graph |
| **LangChain** | LLM chain pipelines, prompt templates, model integration |
| **GPT-4o-mini** | OpenAI LLM powering all agent reasoning and analysis |
| **ChromaDB** | Persistent vector store for RAG document embeddings |
| **rank-bm25** | BM25 Okapi sparse keyword search for hybrid retrieval |
| **MCP (FastMCP)** | Model Context Protocol server for structured tool access |
| **SQLAlchemy** | ORM for SQLite/PostgreSQL database management |
| **python-jose** | JWT token creation and validation |
| **pypdf** | PDF text extraction for RAG ingestion |
| **tiktoken** | OpenAI tokenizer for chunk size estimation |
| **SSE (StreamingResponse)** | Server-Sent Events for real-time analysis streaming |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **React 18** | Component-based UI framework |
| **Vite** | Fast build tool and dev server |
| **Tailwind CSS** | Utility-first CSS framework with custom dark theme |
| **Recharts** | Interactive data visualization charts |
| **Framer Motion** | Smooth animations and transitions |
| **Zustand** | Lightweight state management |
| **Lucide React** | Icon library |
| **Axios** | HTTP client with interceptors |
| **React Router v6** | Client-side routing with protected routes |
| **React Hot Toast** | Notification system |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| **SQLite** | Development database (upgradable to PostgreSQL) |
| **ChromaDB PersistentClient** | On-disk vector store with HNSW cosine index |
| **JWT (HS256)** | Stateless authentication |
| **CORS Middleware** | Cross-origin request handling |
| **Render** | Backend deployment (free tier) |
| **Vercel** | Frontend deployment (free tier) |

---

## Screenshots & Feature Walkthrough

> **Note:** To add screenshots, place them in a `screenshots/` folder and update the paths below.

### Landing Page
The landing page showcases the platform's capabilities with an interactive architecture diagram, agent cards, tech stack display, and call-to-action sections.

<!-- ![Landing Page](screenshots/01-landing.png) -->

**Features shown:**
- Interactive SVG architecture diagram (click any node to inspect)
- 4 agent cards with descriptions and key metrics
- Platform infrastructure cards (RAG, MCP, JWT, Analytics)
- Request flow walkthrough (8 steps)

---

### Login & Authentication
JWT-secured authentication with login/register toggle, role-based demo accounts, and protected dashboard routes.

<!-- ![Login](screenshots/02-login.png) -->

**Features shown:**
- Email/password authentication
- Register new accounts
- Demo credential quick-access
- JWT token-based session management

---

### Dashboard — Overview Tab
Analytics dashboard displaying aggregate risk metrics, trend charts, agent breakdowns, and risk distribution.

<!-- ![Dashboard Overview](screenshots/03-dashboard-overview.png) -->

**Features shown:**
- Stat cards: Total Analyses, Avg Risk Score, High Risk count, RAG status
- Risk score trend chart (line chart over time)
- Agent averages comparison card
- Agent breakdown chart (multi-series bar chart)
- Risk distribution bar (LOW / MEDIUM / HIGH / CRITICAL)
- Recent analyses list with color-coded risk levels

---

### Dashboard — Run Analysis Tab
The core analysis interface where users select a company and run the full multi-agent pipeline.

<!-- ![Run Analysis](screenshots/04-run-analysis.png) -->

**Features shown:**
- Quick-select pre-seeded companies (TechCorp, FinanceHub, EnergyMax, PharmaCare, RetailGiant)
- Custom company input (name, ticker, sector)
- Optional ChromaDB collection linking for RAG
- Real-time SSE streaming indicators showing each agent's progress
- Animated agent status (running / done / error)

---

### Analysis Results — Risk Scores
After analysis completes, the results panel shows risk scores, gauges, and trust metrics.

<!-- ![Analysis Results](screenshots/05-analysis-results.png) -->

**Features shown:**
- Animated risk score gauge (circular SVG)
- Trust score badge from guardrails validation
- Original vs adjusted risk score (post-debate)
- Executive summary text
- Tech stack active indicators

---

### Analysis Results — Agent Details
Expandable panels showing each agent's detailed analysis, metrics, and MCP tool calls.

<!-- ![Agent Details](screenshots/06-agent-details.png) -->

**Features shown:**
- Per-agent analysis text (GPT-generated)
- Key metrics for each domain (volatility, sentiment, ratios, compliance)
- MCP tool calls logged per agent
- Guardrails confidence scores per agent
- RAG sources and hybrid scores (for Financial Report agent)

---

### Multi-Agent Debate Panel
The Devil's Advocate vs Judge debate interface showing challenges, rulings, and score adjustments.

<!-- ![Debate Panel](screenshots/07-debate-panel.png) -->

**Features shown:**
- Devil's Advocate challenges (color-coded by severity: critical/major/minor)
- Target agent identification for each challenge
- Judge verdicts with ruling icons (accepted / partially accepted / dismissed)
- Reasoning for each ruling
- Score adjustment grid (original → adjusted)
- Adjusted overall score with debate impact rating (minimal/moderate/significant)
- Contradictions detected between agents

---

### Conversational Risk Chat
Chat interface for asking follow-up questions about any completed analysis.

<!-- ![Risk Chat](screenshots/08-risk-chat.png) -->

**Features shown:**
- Suggested question chips for quick start
- User/AI message bubbles with avatars
- Context-aware responses referencing the specific analysis
- What-if scenario support
- Chat history persistence
- Clear history option

---

### RAG / Documents Tab
Document upload and RAG pipeline management interface.

<!-- ![RAG Tab](screenshots/09-rag-documents.png) -->

**Features shown:**
- Pre-loaded collection status (sample_financial_docs)
- 4-stage pipeline explanation (Ingestion → Hybrid Retrieval → Re-ranking → Augmented Generation)
- Why Hybrid Search explanation
- PDF upload with drag-and-drop
- Collection management

---

### Analysis History Tab
Full history of all past analyses with risk metrics and color-coded levels.

<!-- ![History Tab](screenshots/10-history.png) -->

**Features shown:**
- Chronological list of all analyses
- Per-analysis scores (Overall, Market, Sentiment, Financial, Compliance)
- Color-coded risk level badges
- Timestamps

---

## Getting Started

### Prerequisites

- **Python 3.10+** (tested on 3.12)
- **Node.js 18+** and npm
- **OpenAI API Key** (for GPT-4o-mini and embeddings)

### 1. Clone the Repository

```bash
git clone https://github.com/singhanushka07/BFSI.git
cd BFSI
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Seed the Database

```bash
cd backend
python seed_data.py
```

This creates 3 demo users and 5 pre-analyzed companies.

### 4. Start the Backend

```bash
cd backend
uvicorn main:app --reload
```

The API is now running at **http://localhost:8000**
- Swagger docs: **http://localhost:8000/api/docs**
- ReDoc: **http://localhost:8000/api/redoc**

> On first startup, ChromaDB is automatically pre-loaded with 3 sample financial PDFs for RAG.

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if backend is not on localhost:8000
```

### 6. Start the Frontend

```bash
cd frontend
npm run dev
```

The app is now running at **http://localhost:5173**

### 7. Try It Out

1. Open http://localhost:5173
2. Log in with `demo@bfsi.com` / `Demo@123`
3. Go to **Run Analysis** tab
4. Select a company (e.g., TechCorp Global) and click **Run Full Risk Analysis**
5. Watch the 6 agents analyze in real-time via SSE streaming
6. Explore the results, debate panel, and risk chat

---

## API Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/register` | POST | No | Register new user |
| `/api/auth/login` | POST | No | Login and receive JWT token |
| `/api/agents/analyze` | POST | JWT | Run synchronous full analysis |
| `/api/agents/analyze-stream` | POST | JWT (query param) | Run SSE streaming analysis |
| `/api/agents/companies` | GET | JWT | List available companies |
| `/api/agents/history` | GET | JWT | Get user's analysis history |
| `/api/chat/message` | POST | JWT | Send chat message about an analysis |
| `/api/chat/history/{id}` | GET | JWT | Get chat history for an analysis |
| `/api/chat/history/{id}` | DELETE | JWT | Clear chat history |
| `/api/rag/upload` | POST | JWT | Upload PDF for RAG ingestion |
| `/api/rag/collections` | GET | JWT | List ChromaDB collections |
| `/api/dashboard/stats` | GET | JWT | Get dashboard statistics |
| `/api/dashboard/overview` | GET | JWT | Get dashboard overview data |
| `/mcp/tools` | GET | No | List all MCP tools |
| `/mcp/invoke` | POST | No | Invoke an MCP tool |
| `/api/health` | GET | No | Platform health check |
| `/api/docs` | GET | No | Swagger UI |

---

## Project Structure

```
BFSI/
├── backend/
│   ├── agents/                    # AI Agent implementations
│   │   ├── orchestrator.py        # LangGraph state machine (6 nodes)
│   │   ├── market_risk.py         # Market Risk Agent (volatility, VaR, beta)
│   │   ├── sentiment.py           # Sentiment Analysis Agent (news, reputation)
│   │   ├── financial_report.py    # Financial Report Agent (RAG-powered)
│   │   ├── regulatory.py          # Regulatory Compliance Agent (Basel III, etc.)
│   │   ├── devils_advocate.py     # Devil's Advocate Agent (challenges findings)
│   │   ├── judge.py               # Judge Agent (resolves debate, adjusts scores)
│   │   └── guardrails.py          # Hallucination detection & output validation
│   ├── auth/
│   │   └── jwt_handler.py         # JWT token creation, validation, password hashing
│   ├── data/
│   │   ├── mock_data.py           # Realistic financial data generators
│   │   └── generate_sample_pdfs.py# Auto-generates sample financial PDFs for RAG
│   ├── mcp_server/
│   │   ├── server.py              # MCP HTTP REST server (FastAPI router)
│   │   ├── mcp_sdk_server.py      # Official FastMCP SDK server (stdio)
│   │   └── dispatcher.py          # In-process MCP tool dispatcher for agents
│   ├── models/
│   │   └── database.py            # SQLAlchemy models (User, RiskAnalysis, ChatMessage)
│   ├── rag/
│   │   ├── pipeline.py            # ChromaDB ingestion, embedding, querying
│   │   ├── hybrid_search.py       # BM25 + dense hybrid search with score fusion
│   │   └── reranker.py            # LLM batch re-ranking of retrieved chunks
│   ├── routers/
│   │   ├── agents.py              # /api/agents endpoints
│   │   ├── auth.py                # /api/auth endpoints
│   │   ├── chat.py                # /api/chat endpoints (conversational risk chat)
│   │   ├── dashboard.py           # /api/dashboard endpoints
│   │   ├── rag.py                 # /api/rag endpoints (PDF upload, collections)
│   │   └── stream.py              # SSE streaming analysis endpoint
│   ├── main.py                    # FastAPI app entry point
│   ├── seed_data.py               # Database seeder (users + sample analyses)
│   ├── requirements.txt           # Python dependencies
│   └── .env.example               # Environment variable template
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.jsx        # Landing page (hero, features, architecture)
│   │   │   ├── Login.jsx          # Auth page (login/register)
│   │   │   └── Dashboard.jsx      # Main dashboard (4 tabs)
│   │   ├── components/
│   │   │   ├── landing/
│   │   │   │   ├── Hero.jsx               # Hero section with CTA
│   │   │   │   ├── Features.jsx           # Agent & platform feature cards
│   │   │   │   ├── ArchitectureDiagram.jsx# Interactive SVG architecture diagram
│   │   │   │   └── TechStack.jsx          # Tech stack showcase
│   │   │   ├── dashboard/
│   │   │   │   ├── RiskScoreGauge.jsx     # Circular risk score gauge
│   │   │   │   ├── RiskCharts.jsx         # Trend, breakdown, distribution charts
│   │   │   │   ├── AgentAnalysisPanel.jsx # Expandable agent detail panels
│   │   │   │   ├── StreamingAgentIndicator.jsx # Real-time SSE agent status
│   │   │   │   ├── TrustScoreBadge.jsx    # Guardrails trust score display
│   │   │   │   ├── DebatePanel.jsx        # Devil's Advocate vs Judge UI
│   │   │   │   ├── ChatPanel.jsx          # Conversational risk chat
│   │   │   │   └── PDFUpload.jsx          # PDF upload for RAG
│   │   │   └── common/
│   │   │       ├── Navbar.jsx
│   │   │       └── Footer.jsx
│   │   ├── store/
│   │   │   └── authStore.js       # Zustand auth state management
│   │   ├── api/
│   │   │   └── client.js          # Axios client with JWT interceptors
│   │   ├── App.jsx                # Router setup with protected routes
│   │   ├── main.jsx               # React entry point
│   │   └── index.css              # Global styles + Tailwind config
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.example
├── docs/                          # HTML & PDF documentation
├── render.yaml                    # Render.com deployment config
└── README.md
```

---

## Deployment

### Backend on Render (Free Tier)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service → Connect your repo
3. Settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `OPENAI_API_KEY` — your OpenAI API key
   - `CORS_ORIGINS` — your Vercel frontend URL
5. Deploy

### Frontend on Vercel (Free Tier)

1. Go to [vercel.com](https://vercel.com) → Import Git Repository
2. Settings:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. Add environment variable:
   - `VITE_API_URL` — your Render backend URL (e.g., `https://bfsi-risk-api.onrender.com/api`)
4. Deploy

### Using render.yaml (One-Click)

The included `render.yaml` provides a pre-configured deployment blueprint for the backend.

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@bfsi.com | Admin@123 |
| Analyst | analyst@bfsi.com | Analyst@123 |
| Demo | demo@bfsi.com | Demo@123 |

### Pre-Seeded Risk Analyses

| Ticker | Company | Risk Level | Overall Score |
|--------|---------|------------|---------------|
| TCG | TechCorp Global | HIGH | 68.4 |
| FHL | FinanceHub Ltd | MEDIUM | 54.2 |
| EMX | EnergyMax Inc | MEDIUM | 41.7 |
| PCC | PharmaCare Corp | HIGH | 79.3 |
| RGC | RetailGiant Co | LOW | 28.5 |

---

## Environment Variables

### Backend (`backend/.env`)

```env
OPENAI_API_KEY=sk-your-openai-key-here
SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///./bfsi_risk.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CHROMA_PERSIST_DIR=./chroma_db
CORS_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
```

### Frontend (`frontend/.env`)

```env
VITE_API_URL=http://localhost:8000/api
```

---

## MCP Server (Standalone)

The platform includes an official FastMCP SDK server that can be connected to by any MCP client:

```bash
cd backend
python -m mcp_server.mcp_sdk_server
```

Or register in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bfsi-risk": {
      "command": "python",
      "args": ["-m", "mcp_server.mcp_sdk_server"],
      "cwd": "/path/to/BFSI/backend"
    }
  }
}
```

---

## License

This project is for educational and demonstration purposes.

---

**Built with LangGraph, LangChain, GPT-4o-mini, FastAPI, ChromaDB, MCP, React, and Tailwind CSS.**
