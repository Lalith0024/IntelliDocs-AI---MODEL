import os
import chromadb
from typing import Optional
from app.core.config import settings

CHROMA_DATA_PATH = "data/chroma"

_client: Optional[chromadb.PersistentClient] = None

def get_client():
    """Lazy load ChromaDB client."""
    global _client
    if _client is None:
        print("Initializing ChromaDB PersistentClient...")
        _client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    return _client

def get_collection():
    client = get_client()
    return client.get_or_create_collection(
        name="rag_documents",
        metadata={"hnsw:space": "cosine"}
    )
