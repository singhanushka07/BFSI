from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging

load_dotenv()

from models.database import create_tables
from routers.auth import router as auth_router
from routers.agents import router as agents_router
from routers.rag import router as rag_router
from routers.dashboard import router as dashboard_router
from routers.stream import router as stream_router
from routers.chat import router as chat_router
from mcp_server.server import mcp_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="BFSI Multi-Agent Financial Risk Assessment Platform",
    description="AI-driven risk analysis using LangGraph, LangChain, GPT, ChromaDB RAG, and MCP",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(stream_router)
app.include_router(chat_router)
app.include_router(rag_router)
app.include_router(dashboard_router)
app.include_router(mcp_router)


def _bootstrap_rag_collection():
    """
    Auto-generate sample financial PDFs and ingest into ChromaDB if the
    default 'sample_financial_docs' collection does not yet exist.
    This ensures RAG is always active on every analysis run.
    """
    try:
        from rag.pipeline import list_collections, ingest_pdf
        from data.generate_sample_pdfs import generate_all_sample_pdfs

        existing = list_collections()
        if "sample_financial_docs" in existing:
            logger.info("[RAG Bootstrap] sample_financial_docs collection already exists — skipping generation.")
            return

        logger.info("[RAG Bootstrap] Generating sample financial PDFs for ChromaDB pre-loading...")
        pdfs = generate_all_sample_pdfs()

        total_chunks = 0
        for path, company, doc_type in pdfs:
            if os.path.exists(path):
                chunks = ingest_pdf(path, "sample_financial_docs", {"company": company, "doc_type": doc_type})
                total_chunks += chunks
                logger.info(f"[RAG Bootstrap] Ingested {chunks} chunks from {os.path.basename(path)}")
            else:
                logger.warning(f"[RAG Bootstrap] PDF not found: {path}")

        logger.info(f"[RAG Bootstrap] ChromaDB collection 'sample_financial_docs' ready — {total_chunks} total chunks.")

    except Exception as e:
        logger.error(f"[RAG Bootstrap] Failed to bootstrap RAG collection: {e}")


@app.on_event("startup")
async def startup():
    create_tables()
    os.makedirs("./uploads", exist_ok=True)
    os.makedirs("./chroma_db", exist_ok=True)
    os.makedirs("./sample_pdfs", exist_ok=True)

    # Pre-load ChromaDB with sample financial documents so RAG is always active
    _bootstrap_rag_collection()


@app.get("/api/health")
def health():
    from rag.pipeline import list_collections
    collections = list_collections()
    return {
        "status": "healthy",
        "platform": "BFSI Multi-Agent Financial Risk Assessment Platform",
        "version": "1.0.0",
        "agents": ["Market Risk", "Sentiment Analysis", "Financial Report (RAG)", "Regulatory Compliance", "Devil's Advocate", "Judge"],
        "features": ["SSE Streaming", "Guardrails + Hallucination Detection", "Multi-Agent Debate", "Conversational Risk Chat"],
        "stack": ["LangGraph", "LangChain", "GPT-4o-mini", "FastAPI", "ChromaDB", "MCP", "SQLAlchemy", "JWT", "SSE"],
        "rag": {
            "collections": collections,
            "sample_financial_docs_loaded": "sample_financial_docs" in collections,
        },
        "mcp": {
            "tools": ["get_stock_data", "get_financial_metrics", "get_news_sentiment", "get_regulatory_rules", "rag_query"],
            "status": "active",
        },
    }
