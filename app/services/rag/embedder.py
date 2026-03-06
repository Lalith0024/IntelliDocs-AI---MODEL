_embedding_model = None

def get_model():
    """Lazy load the embedding model to save RAM at startup."""
    global _embedding_model
    if _embedding_model is None:
        print("Loading Embedding Model into RAM...")
        from fastembed import TextEmbedding
        _embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")
    return _embedding_model

def embed_text(text: str) -> list[float]:
    """Generate embedding for a single string."""
    model = get_model()
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple strings."""
    model = get_model()
    embeddings = list(model.embed(texts))
    return [e.tolist() for e in embeddings]
