import os
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
import hashlib

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

_client = None


def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return _client


def get_embedding_fn():
    if OPENAI_API_KEY:
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name="text-embedding-3-small",
        )
    return embedding_functions.DefaultEmbeddingFunction()


def extract_text_from_pdf(file_path: str) -> list[dict]:
    reader = PdfReader(file_path)
    chunks = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        # Split into ~500 char chunks with overlap
        words = text.split()
        chunk_size = 150
        overlap = 20
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:
                chunks.append({
                    "text": chunk,
                    "page": page_num + 1,
                    "chunk_index": i // (chunk_size - overlap),
                })
    return chunks


def ingest_pdf(file_path: str, collection_name: str, metadata: dict = None) -> int:
    client = get_chroma_client()
    ef = get_embedding_fn()
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    chunks = extract_text_from_pdf(file_path)
    if not chunks:
        return 0
    documents = [c["text"] for c in chunks]
    ids = [
        hashlib.md5(f"{collection_name}-{c['page']}-{c['chunk_index']}".encode()).hexdigest()
        for c in chunks
    ]
    metas = [
        {
            "page": c["page"],
            "source": os.path.basename(file_path),
            **(metadata or {}),
        }
        for c in chunks
    ]
    collection.upsert(documents=documents, ids=ids, metadatas=metas)
    return len(chunks)


def query_collection(collection_name: str, query: str, n_results: int = 5) -> list[dict]:
    client = get_chroma_client()
    ef = get_embedding_fn()
    try:
        collection = client.get_collection(name=collection_name, embedding_function=ef)
    except Exception:
        return []
    results = collection.query(query_texts=[query], n_results=n_results)
    output = []
    for i, doc in enumerate(results["documents"][0]):
        output.append({
            "text": doc,
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return output


def list_collections() -> list[str]:
    client = get_chroma_client()
    return [c.name for c in client.list_collections()]


def delete_collection(collection_name: str):
    client = get_chroma_client()
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
