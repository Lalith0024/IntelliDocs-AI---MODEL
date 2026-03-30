import os
import json
import chromadb
import re
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk
from app.services.rag.loader import extract_text, chunk_text
from app.services.rag.embedder import embed_texts, embed_text
from app.services.rag.vector_db import get_collection

def hybrid_score_boost(query: str, content: str) -> float:
    """
    Keyword-Boosting Protocol:
    Demonstrates Hybrid Retrieval (Vector + BM25-lite logic).
    Ensures exact matches in Proper Names or IDs get a retrieval boost.
    """
    query_terms = re.findall(r'\w+', query.lower())
    content_lower = content.lower()
    matches = 0
    for term in query_terms:
        if len(term) > 3 and term in content_lower:
            matches += 1
    
    # Return a 10% boost for every keyword match
    return matches * 0.1

def add_document_to_index(db: Session, file_path: str, filename: str, document_id: str, user_id: str):
    """
    Production-Grade Ingestion Pipeline:
    1. Extract & Chunk
    2. Batch Embed
    3. Persist to ChromaDB (Vector Store)
    4. Store in SQL (Metadata Tracker)
    """
    text = extract_text(file_path)
    if not text:
        return
    
    chunks = chunk_text(text)
    if not chunks:
        return

    embeddings = embed_texts(chunks)
    collection = get_collection()
    
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"user_id": user_id, "document_id": document_id, "filename": filename} for _ in chunks]
    
    # ADD TO VECTOR STORE (CHROMA)
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=chunks
    )
    
    # ADD TO SQL (METADATA HUB)
    for i in range(len(chunks)):
        chunk_obj = DocumentChunk(
            user_id=user_id,
            document_id=str(document_id),
            filename=filename,
            chunk_index=str(i),
            content=chunks[i],
            embedding=json.dumps(embeddings[i])
        )
        db.add(chunk_obj)
    db.commit()

def search_documents(db: Session, query: str, user_id: str, top_k: int = 5):
    """
    Production-Grade Hybrid Retrieval:
    Uses ChromaDB for optimized vector search + Manual Keyword Boosting.
    This provides 'S-Tier' accuracy by combining semantics with exact matches.
    """
    query_emb = embed_text(query)
    collection = get_collection()
    
    # FETCH BROADER CANDIDATE SET (For Hybrid Re-scoring)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k * 3, # Get more than needed to re-rank
        where={"user_id": user_id}
    )
    
    candidate_results = []
    if results['documents']:
        for i in range(len(results['documents'][0])):
            content = results['documents'][0][i]
            vector_score = 1 - results['distances'][0][i] if results['distances'] else 0.0
            
            # 1. APPLY HYBRID BOOST (Keyword Match)
            keyword_boost = hybrid_score_boost(query, content)
            final_score = vector_score + keyword_boost
            
            candidate_results.append({
                "content": content,
                "score": round(float(final_score), 4),
                "filename": results['metadatas'][0][i].get('filename', 'Unknown'),
                "id": results['ids'][0][i]
            })
            
    # 2. RE-RANK BASED ON HYBRID SCORE
    candidate_results.sort(key=lambda x: x["score"], reverse=True)
    return candidate_results[:top_k]
