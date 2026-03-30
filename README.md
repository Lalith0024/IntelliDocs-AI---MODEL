# IntelliDocs AI - Engine & RAG Pipeline

A production-grade, asynchronous Retrieval-Augmented Generation (RAG) backend API. Built with **FastAPI** to handle high-throughput, low-latency vector search and intelligent document synthesis via Server-Sent Events (SSE).

## 🚀 Core Architecture

- **Protocol**: REST API & SSE (Server-Sent Events)
- **Framework**: FastAPI (Python 3.12+)
- **Vector Database**: ChromaDB Persistent Client
- **Relational Store**: SQLite (via SQLAlchemy ORM)
- **LLM Integration**: Provider-Agnostic LLM Routing (Groq/OpenAI fallback)
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)

---

## 🧠 System Capabilities

### 1. Hybrid Ingestion Pipeline
- Supports dynamic text parsing (`.txt`, `.pdf`, `.csv`, `.json`).
- Automatically chunks large text and streams high-dimensional vector embeddings into local ChromaDB shards.
- Cross-references metadata with SQLite to establish explicit ownership mappings.

### 2. Intent-Based Routing
The engine performs a sub-millisecond intent evaluation on every query:
- `summary`: Triggers 12-doc retrieval for broad aggregations.
- `audit`: Triggers 12-doc retrieval prioritizing gap-analysis logic.
- `timeline`: Focuses on chronological event extractions.
- `default`: Executes standard 6-doc high-precision dense retrieval.

### 3. Asynchronous Neural Streaming
The engine natively bridges the LLM processing pipeline to an asynchronous event loop via `generate_answer_stream`.
- **Word-by-Word Yielding**: Bypasses heavy response build times by streaming raw JSON buffers to the client instantly.
- **Dynamic Context Follow-ups**: Seamlessly triggers secondary logic flows to compute intelligent multi-turn next steps (Dynamic Suggestions) right before terminating the event stream.

---

## 🔧 Installation & Deployment

1. **Virtual Environment Setup**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Dependency Resolution**
```bash
pip install -r requirements.txt
```

3. **Environment Geometry**
Create a `.env` file at the root:
```env
OPENAI_API_KEY=""
GROQ_API_KEY="your_api_key_here"
```

4. **Launch Engine**
```bash
uvicorn app.main:app --reload --port 8000
```
*The interactive API documentation is automatically generated at `/docs`.*