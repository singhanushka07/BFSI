"""
LLM-based batch re-ranker.
Sends all retrieved chunks to GPT in a single prompt and asks it to score
each chunk's relevance (0-10) to the analysis query. One API call, no extra packages.
Falls back to hybrid scores if LLM is unavailable or parsing fails.
"""
import os
import re
import json
from langchain_openai import ChatOpenAI


def rerank_chunks(
    query: str,
    chunks: list[dict],
    top_k: int = 4,
) -> list[dict]:
    """
    Re-ranks retrieved chunks using a single GPT batch scoring call.

    GPT receives all chunks at once and returns relevance scores [0-10].
    Chunks are then sorted by score and the top_k are returned, each
    with a 'rerank_score' (0.0–1.0) added.

    Falls back to returning top_k by hybrid_score / position if LLM fails.
    """
    if not chunks:
        return []

    if len(chunks) <= top_k:
        for c in chunks:
            c.setdefault("rerank_score", round(c.get("hybrid_score", 0.5), 4))
        return chunks

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        _tag_fallback(chunks, top_k)
        return chunks[:top_k]

    # Format chunks for batch scoring — truncate to keep prompt manageable
    numbered_chunks = "\n\n".join([
        f"[CHUNK {i + 1}] Source: {c['metadata'].get('source', 'doc')} "
        f"p.{c['metadata'].get('page', '?')}\n{c['text'][:350]}"
        for i, c in enumerate(chunks[:10])
    ])

    prompt = (
        f"You are a financial document relevance scorer.\n"
        f"Query: \"{query}\"\n\n"
        f"Score each chunk's relevance to this financial risk analysis query (0=irrelevant, 10=highly relevant).\n"
        f"Reply ONLY with a JSON array of integers, one per chunk. Example: [8, 3, 9, 2, 7]\n\n"
        f"{numbered_chunks}\n\n"
        f"Scores:"
    )

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
        response = llm.invoke(prompt)
        raw = response.content.strip()

        # Extract JSON array from response
        match = re.search(r'\[[\d,\s]+\]', raw)
        if not match:
            raise ValueError(f"No array found in: {raw}")

        scores = json.loads(match.group())
        scores = [max(0, min(10, int(s))) for s in scores]

        # Pair, sort, slice
        paired = list(zip(scores, chunks[:len(scores)]))
        paired.sort(key=lambda x: -x[0])

        results = []
        for score, chunk in paired[:top_k]:
            c = dict(chunk)
            c["rerank_score"] = round(score / 10.0, 3)
            results.append(c)
        return results

    except Exception:
        _tag_fallback(chunks, top_k)
        return chunks[:top_k]


def _tag_fallback(chunks: list[dict], top_k: int):
    """Tag top_k chunks with a fallback rerank_score when LLM scoring fails."""
    for i, c in enumerate(chunks[:top_k]):
        c["rerank_score"] = round(c.get("hybrid_score", (top_k - i) / top_k), 4)
