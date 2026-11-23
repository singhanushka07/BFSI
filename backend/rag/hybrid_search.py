"""
Hybrid RAG Search: combines ChromaDB dense vector search with BM25 sparse keyword search.
Weighted combination gives better recall for financial terminology (Basel III, IFRS 9, etc.)
that semantic search alone can miss.
"""
import numpy as np
from rag.pipeline import query_collection

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False


def _normalize(arr: np.ndarray) -> np.ndarray:
    """Min-max normalize to [0, 1]."""
    rng = arr.max() - arr.min()
    if rng < 1e-9:
        return np.ones_like(arr) * 0.5
    return (arr - arr.min()) / rng


def hybrid_rag_search(
    collection_name: str,
    query: str,
    n_results: int = 5,
    alpha: float = 0.6,
) -> list[dict]:
    """
    Hybrid search combining dense (ChromaDB cosine) + sparse (BM25 keyword) retrieval.

    Args:
        collection_name: ChromaDB collection to search
        query: natural language query
        n_results: final number of chunks to return
        alpha: weight for dense search (1-alpha used for BM25); 0.6 recommended

    Returns:
        List of chunks sorted by hybrid_score descending, each with:
          hybrid_score, dense_score, bm25_score added to metadata
    """
    # Retrieve more candidates than needed so re-ranking has options
    candidates = query_collection(collection_name, query, n_results=min(n_results * 4, 20))

    if not candidates:
        return []

    # Dense similarity scores from ChromaDB (distance → similarity)
    dense_scores = np.array([max(0.0, 1.0 - c.get("distance", 1.0)) for c in candidates])

    if BM25_AVAILABLE:
        # BM25 sparse scores over the candidate set
        tokenized_corpus = [c["text"].lower().split() for c in candidates]
        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores = np.array(bm25.get_scores(query.lower().split()), dtype=float)
    else:
        # Graceful degradation: pure dense search when rank_bm25 not installed
        bm25_scores = dense_scores.copy()
        alpha = 1.0

    dense_norm = _normalize(dense_scores)
    bm25_norm = _normalize(bm25_scores)
    combined = alpha * dense_norm + (1.0 - alpha) * bm25_norm

    top_indices = np.argsort(combined)[::-1][:n_results]

    results = []
    for i in top_indices:
        chunk = dict(candidates[i])
        chunk["hybrid_score"] = round(float(combined[i]), 4)
        chunk["dense_score"] = round(float(dense_norm[i]), 4)
        chunk["bm25_score"] = round(float(bm25_norm[i]), 4)
        chunk["search_method"] = "hybrid_bm25_dense" if BM25_AVAILABLE else "dense_only"
        results.append(chunk)

    return results


def bm25_available() -> bool:
    return BM25_AVAILABLE
