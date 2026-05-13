# 🧬 IntelliDocs AI - Advanced Document Intelligence Platform

> **Enterprise-Grade RAG (Retrieval-Augmented Generation) Application** for professional-grade document interaction and analysis.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)](https://fastapi.tiangolo.com/)
[![React 18+](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [RAG Pipeline Deep Dive](#rag-pipeline-deep-dive)
- [Database Schema](#database-schema)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**IntelliDocs AI** is a cutting-edge document intelligence platform that combines:

1. **Advanced RAG Pipeline** - Retrieval-Augmented Generation using vector embeddings
2. **Real-time Streaming** - Server-Sent Events (SSE) for instant response generation
3. **Multi-Document Analysis** - Compare and synthesize insights across files
4. **Enterprise Security** - JWT authentication + Google OAuth 2.0
5. **Intelligent UI Components** - Auto-triggering interactive flashcards, code blocks, quizzes

### Why IntelliDocs?

- ✅ **One-Stop Intelligence**: Upload any document → Get instant answers
- ✅ **Hybrid Search**: Vector semantic search + keyword boosting for accuracy
- ✅ **Streaming Generation**: Real-time token-by-token responses (not chatbot)
- ✅ **Beautiful UX**: 3-pane workspace with smooth animations
- ✅ **Production-Ready**: Containerized, scalable, monitored

---

## 📂 Project Structure

```
Ml_internshipproject/
├── 📁 app/                          # Backend FastAPI application
│   ├── 📄 main.py                   # Application entry point
│   ├── 📁 api/                      # REST API routes
│   │   ├── routes/
│   │   │   ├── auth.py              # Authentication (signup, login, Google OAuth)
│   │   │   ├── chat.py              # Streaming chat endpoint (neural stream)
│   │   │   └── documents.py         # Document upload & management
│   │   └── dependencies.py          # JWT dependency injection
│   ├── 📁 core/                     # Core application logic
│   │   ├── config.py                # Environment & settings
│   │   ├── security.py              # Password hashing & JWT
│   │   └── google_auth.py           # Google token verification
│   ├── 📁 db/                       # Database layer
│   │   ├── database.py              # SQLAlchemy setup
│   │   └── models.py                # ORM models (User, Document, Chat, Message)
│   ├── 📁 services/                 # Business logic
│   │   └── rag/                     # RAG Pipeline
│   │       ├── pipeline.py          # Vector search & hybrid retrieval
│   │       ├── embedder.py          # FastEmbed (BAAI/bge-small-en-v1.5)
│   │       ├── loader.py            # PDF/JSON/CSV extraction
│   │       ├── llm.py               # LLM streaming (Groq/OpenAI)
│   │       ├── vector_db.py         # ChromaDB client
│   │       └── README.md            # RAG documentation
│   └── 📁 schemas/                  # Pydantic models (request/response)
│
├── 📁 Intellidocs AI - frontend/     # React frontend (Vite)
│   ├── 📄 index.html
│   ├── 📄 package.json              # Dependencies + scripts
│   ├── vite.config.ts               # Vite configuration
│   ├── tsconfig.json                # TypeScript config
│   ├── 📁 public/                   # Static assets
│   ├── 📁 src/
│   │   ├── 📄 main.tsx              # React entry point
│   │   ├── 📄 App.tsx               # Root component (providers setup)
│   │   ├── 📁 pages/                # Page components
│   │   │   ├── Login.tsx            # Auth page (signup/login/Google OAuth)
│   │   │   ├── Home.tsx             # Main dashboard
│   │   │   ├── Documents.tsx        # Document management
│   │   │   └── Files.tsx            # File browser
│   │   ├── 📁 components/           # Reusable UI components
│   │   │   ├── OnboardingModal.tsx  # 5-step onboarding flow
│   │   │   ├── GoogleLoginButton.tsx# Google OAuth button
│   │   │   ├── MarkdownRenderer.tsx # Dynamic markdown with artifacts
│   │   │   ├── InteractiveChart.tsx # Chart rendering
│   │   │   ├── InteractiveQuiz.tsx  # Quiz component
│   │   │   ├── Sidebar.tsx          # Navigation sidebar
│   │   │   ├── SearchBar.tsx        # Search interface
│   │   │   └── LoadingSkeleton.tsx  # Skeleton loader
│   │   ├── 📁 context/              # React Context state
│   │   │   ├── AuthContext.tsx      # Authentication state
│   │   │   ├── OnboardingContext.tsx# Onboarding state
│   │   │   └── ErrorContext.tsx     # Error handling
│   │   ├── 📁 services/             # API service layer
│   │   │   └── api.ts               # Axios instance + methods
│   │   ├── 📁 types/                # TypeScript interfaces
│   │   │   └── api.ts               # API response types
│   │   └── 📁 utils/                # Utility functions
│   │       └── cn.ts                # Class name merger
│   └── 📁 src/assets/               # Images, icons
│
├── 📁 data/                         # Runtime data
│   ├── uploads/                     # User uploaded files
│   └── chroma/                      # ChromaDB vector store
│
├── 📄 requirements.txt              # Python dependencies
├── 📄 Dockerfile                    # Docker configuration
├── 📄 render.yaml                   # Render deployment config
├── 📄 .env                          # Environment variables (don't commit)
├── 📄 .gitignore                    # Git ignore rules
├── 📄 DEPLOYMENT.md                 # Deployment guide
└── 📄 README.md                     # This file
```

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        A[React 18 Frontend<br/>Vite + TypeScript]
    end
    
    subgraph Auth["Authentication"]
        B1[JWT Tokens<br/>7-day expiry]
        B2[Google OAuth 2.0<br/>Auto-signup]
        B3[Password Hashing<br/>bcrypt]
    end
    
    subgraph API["API Layer - FastAPI"]
        C1[/api/auth<br/>Login/Signup]
        C2[/api/documents<br/>Upload/Retrieve]
        C3[/api/chats/query/stream<br/>Neural Stream]
    end
    
    subgraph RAG["RAG Pipeline"]
        D1["Document Loader<br/>PDF/JSON/CSV/TXT"]
        D2["Chunking<br/>500 tokens + overlap"]
        D3["Embeddings<br/>BAAI/bge-small-en-v1.5"]
        D4["Vector Store<br/>ChromaDB Persistent"]
        D5["Hybrid Search<br/>Vector + Keyword"]
    end
    
    subgraph Generation["Generation Layer"]
        E1["Intent Detection<br/>Query/Summary/Quiz"]
        E2["LLM Provider<br/>Groq Llama 3.1"]
        E3["Streaming<br/>Token-by-token SSE"]
        E4["Persona Engine<br/>Dynamic prompting"]
    end
    
    subgraph DB["Data Layer"]
        F1["SQLite/PostgreSQL<br/>User/Chat/Message"]
        F2["ChromaDB<br/>Vector embeddings"]
        F3["File Storage<br/>data/uploads"]
    end
    
    A -->|API calls| Auth
    Auth -->|Authenticated| API
    API -->|Process| RAG
    RAG -->|Retrieve context| D4
    D5 -->|Ranked docs| Generation
    Generation -->|Stream SSE| A
    API -->|Persist| DB
    RAG -->|Store chunks| F2
    D1 -->|Load files| F3
```

### Flow: User Question → AI Answer

1. **User uploads document** → Stored in `data/uploads/`
2. **Background indexing** → Extract text → Chunk → Embed → ChromaDB
3. **User asks question** → Intent detection (query/summary/quiz)
4. **Hybrid retrieval** → Vector search + keyword boost
5. **LLM generation** → Groq/OpenAI streams response
6. **SSE streaming** → Frontend receives token-by-token
7. **Smart rendering** → Auto-detect flashcards/code/charts
8. **Save to DB** → Store chat for history

---

## 🚀 Key Features

### 1. **3-Pane Dynamic Workspace**
- **Sidebar**: Document library + chat history
- **Main Panel**: Real-time chat interface
- **Artifact Panel**: Interactive code, flashcards, charts

### 2. **Intelligent RAG**
- Hybrid vector + keyword search
- Multi-document retrieval (top-K ranked)
- Dynamic chunking with context overlap

### 3. **Streaming Generation**
- Server-Sent Events (SSE) for real-time responses
- No wait time - start reading immediately
- Token-by-token synthesis

### 4. **Auto-Triggering Components**
Detects special blocks in LLM output:
- ````flashcard` - Interactive study cards
- ````chart` - Revenue/analytics visualizations
- ````quiz` - Multiple-choice questions
- ````code` - Syntax-highlighted snippets

### 5. **Multi-Authentication**
- Email/Password with bcrypt
- Google OAuth (1-click signup)
- 7-day JWT expiry

### 6. **Beautiful UX**
- Framer Motion animations
- Dark/Light theme toggle
- Responsive mobile design
- Loading skeletons

---

## 🛠️ Technology Stack

### Backend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | FastAPI 0.95+ | Async REST API |
| **Server** | Uvicorn | ASGI app server |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Metadata storage |
| **ORM** | SQLAlchemy | Database abstraction |
| **Vector Store** | ChromaDB | Embedding persistence |
| **Embeddings** | FastEmbed (BAAI/bge-small-en-v1.5) | Text→Vector (384 dims) |
| **LLM** | Groq (Llama 3.1) / OpenAI (GPT-4) | Text generation |
| **Auth** | PyJWT + bcrypt | Security |
| **OAuth** | google-auth + google-auth-oauthlib | Google login |
| **File Parsing** | PyMuPDF, csv, json | Document extraction |

### Frontend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | React 18 | UI library |
| **Language** | TypeScript | Type safety |
| **Build Tool** | Vite | Ultra-fast bundler |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **Animations** | Framer Motion 10 | Smooth transitions |
| **Icons** | Lucide React | Icon library |
| **HTTP Client** | Axios | API requests |
| **Routing** | React Router v6 | Navigation |
| **Auth** | React OAuth Google | Google login |
| **Context** | React Context API | State management |

### Deployment

| Environment | Service | Stack |
|-------------|---------|-------|
| **Local Dev** | Localhost | SQLite + Vite dev server |
| **Production** | Render | Docker + PostgreSQL |
| **Frontend** | Vercel | Next.js deployment |

---

## 📦 Installation & Setup

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (with npm)
- **git**

### Backend Setup

#### 1. Clone & Enter Project

```bash
git clone https://github.com/yourusername/IntelliDocs-AI.git
cd IntelliDocs-AI
```

#### 2. Create Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# LLM API Keys (choose one: Groq is free and fast)
GROQ_API_KEY="gsk_your_groq_key_here"
# OR for OpenAI:
# OPENAI_API_KEY="sk-your-openai-key-here"

# Google OAuth
GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:8000/api/auth/google/callback"

# JWT Secret (generate: openssl rand -hex 32)
SECRET_KEY="your-256-bit-secret-key"

# Database (default SQLite, change for prod)
DATABASE_URL="sqlite:///./sql_app.db"
```

#### 5. Initialize Database

```bash
python -c "from app.db.database import create_tables; create_tables()"
```

### Frontend Setup

#### 1. Navigate to Frontend Directory

```bash
cd "Intellidocs AI - frontend"
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Configure Environment Variables

Create `.env.local` in the frontend directory:

```env
VITE_GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
VITE_API_URL="http://localhost:8000"  # Backend URL
```

#### 4. Start Development Server

```bash
npm run dev
```

---

## 🎬 Running the Application

### Development Mode

#### Terminal 1: Start Backend

```bash
# From project root
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

Backend will be running at: **http://localhost:8000**

Swagger UI documentation: **http://localhost:8000/docs**

#### Terminal 2: Start Frontend

```bash
# From frontend directory
cd "Intellidocs AI - frontend"
npm run dev
```

Frontend will be running at: **http://localhost:5173**

#### Test the Application

1. Open **http://localhost:5173** in your browser
2. Click "Sign Up" → Create account with email/password OR use "Continue with Google"
3. Upload a PDF document
4. Ask a question about the document
5. Watch the AI stream real-time responses

---

## 📚 API Documentation

### Authentication

#### POST `/api/auth/signup`
Create a new user account

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST `/api/auth/token`
Login with email/password (OAuth2)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securePassword123"
```

#### POST `/api/auth/google/token`
Login with Google OAuth

**Request:**
```json
{
  "idToken": "google-id-token-from-frontend"
}
```

#### GET `/api/auth/me`
Get current user info

**Headers:**
```
Authorization: Bearer {access_token}
```

### Documents

#### POST `/api/documents/upload`
Upload a document

**Form Data:**
- `file`: Binary file (PDF, JSON, CSV, TXT, PNG, JPG)

**Response:**
```json
{
  "id": "doc-uuid",
  "filename": "report.pdf",
  "status": "processing",
  "created_at": "2024-05-05T10:30:00"
}
```

#### GET `/api/documents/`
List all user's documents

**Response:**
```json
[
  {
    "id": "doc-uuid",
    "filename": "report.pdf",
    "status": "ready",
    "created_at": "2024-05-05T10:30:00"
  }
]
```

#### DELETE `/api/documents/{document_id}`
Delete a document and its index

### Chat (Neural Stream)

#### POST `/api/chats/query/stream`
Stream real-time AI responses

**Request:**
```json
{
  "question": "What are the key findings?",
  "chat_id": "optional-existing-chat-uuid",
  "document_ids": ["doc-id-1", "doc-id-2"]
}
```

**Response:** Server-Sent Events (SSE)
```
data: {"chat_id": "chat-uuid", "intent": "query", "valid_count": 5, "docs": [...]}

data: {"content": "The"}

data: {"content": " key"}

data: {"content": " findings"}

...
```

#### POST `/api/chats/query`
Synchronous query (fallback)

#### GET `/api/chats/`
List all chats

#### GET `/api/chats/{chat_id}`
Get chat with full message history

---

## 🧠 RAG Pipeline Deep Dive

### 1. Document Ingestion

```
PDF/JSON/CSV File
    ↓
extract_text() → Raw text
    ↓
chunk_text() → 500-token chunks + 50-token overlap
    ↓
embed_texts() → BAAI/bge-small-en-v1.5 (FastEmbed)
    ↓
ChromaDB Store → Persistent vector index
```

**Why FastEmbed?**
- Lightweight (11MB vs ONNX's 350MB)
- Fast CPU inference (no GPU needed)
- Good semantic quality (384 dimensions)
- Perfect for production edge devices

### 2. Retrieval (Hybrid Search)

```
User Question
    ↓
embed_text() → Query embedding (384 dims)
    ↓
ChromaDB.query() → Top-K candidates (cosine similarity)
    ↓
hybrid_score_boost() → Keyword matching bonus
    ↓
Re-rank → Final Top-5 documents
```

**Hybrid Algorithm:**
- Vector Score: 1 - cosine_distance
- Keyword Boost: +0.1 per 3+ char match
- Final Score = Vector + Boost

### 3. Generation (Streaming)

```
Docs + Question
    ↓
Intent Detection → [query|summary|quiz|timeline|audit]
    ↓
Persona Prompt → Custom system message
    ↓
Groq API → Stream tokens
    ↓
SSE → Frontend (real-time)
    ↓
Parse Blocks → Flashcard/Chart/Quiz
```

**Artifact Blocks** (auto-detected):
```markdown
```flashcard
Front: What is RAG?
Back: Retrieval-Augmented Generation combines search + generation
```

```chart
title: Revenue Growth
data: [10, 20, 30, 45, 50]
```

```quiz
Q: What's the capital of France?
A) London
B) Paris ✓
C) Berlin
```
```

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR,  -- Nullable for OAuth users
    google_id VARCHAR UNIQUE,  -- Google OAuth ID
    profile_picture VARCHAR,   -- Google profile image
    created_at DATETIME DEFAULT NOW()
);
```

### Documents Table
```sql
CREATE TABLE documents (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR FOREIGN KEY → users.id,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    status VARCHAR DEFAULT "processing",  -- ready|failed
    created_at DATETIME DEFAULT NOW()
);
```

### Document Chunks Table
```sql
CREATE TABLE document_chunks (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR FOREIGN KEY → users.id,
    document_id VARCHAR FOREIGN KEY → documents.id,
    filename VARCHAR,
    chunk_index VARCHAR,
    content TEXT,
    embedding TEXT,  -- JSON array of 384 floats
    created_at DATETIME DEFAULT NOW()
);
```

### Chats Table
```sql
CREATE TABLE chats (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR FOREIGN KEY → users.id,
    title VARCHAR,
    created_at DATETIME DEFAULT NOW()
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id VARCHAR PRIMARY KEY,
    chat_id VARCHAR FOREIGN KEY → chats.id,
    role VARCHAR,  -- user|assistant
    content TEXT,
    created_at DATETIME DEFAULT NOW()
);
```

---

## 🚀 Deployment

### Production Backend (Render)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy: Production setup"
   git push origin main
   ```

2. **Create Render Service**
   - Go to https://render.com
   - New → Web Service
   - Connect GitHub repo
   - Runtime: Docker
   - Build: `docker build -t intellidocs-backend .`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port 10000`

3. **Set Environment Variables**
   ```
   GROQ_API_KEY=gsk_xxx
   GOOGLE_CLIENT_ID=xxx
   GOOGLE_CLIENT_SECRET=xxx
   GOOGLE_REDIRECT_URI=https://your-app.onrender.com/api/auth/google/callback
   DATABASE_URL=postgresql://...  # Use PostgreSQL in production
   ```

### Production Frontend (Vercel)

1. **Deploy Frontend**
   ```bash
   cd "Intellidocs AI - frontend"
   npm run build
   # Or use Vercel CLI:
   vercel deploy --prod
   ```

2. **Set Environment Variables in Vercel Dashboard**
   ```
   VITE_GOOGLE_CLIENT_ID=xxx
   VITE_API_URL=https://your-backend.onrender.com
   ```

---

## 🔑 Environment Variables Reference

### Backend (.env)

| Variable | Example | Notes |
|----------|---------|-------|
| `GROQ_API_KEY` | `gsk_xxx` | Free LLM API key from groq.com |
| `OPENAI_API_KEY` | `sk_xxx` | Alternative: OpenAI GPT-4 |
| `GOOGLE_CLIENT_ID` | `123.apps.googleusercontent.com` | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX_xxx` | From Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | `http://localhost:8000/...` | OAuth callback URL |
| `DATABASE_URL` | `sqlite:///./sql_app.db` | SQLite (dev) or PostgreSQL (prod) |
| `SECRET_KEY` | `(random 32-byte hex)` | JWT signing secret |

### Frontend (.env.local)

| Variable | Example | Notes |
|----------|---------|-------|
| `VITE_GOOGLE_CLIENT_ID` | `123.apps.googleusercontent.com` | Match backend value |
| `VITE_API_URL` | `http://localhost:8000` | Backend URL |

---

## 🐛 Troubleshooting

### Backend Issues

#### "No module named 'pydantic'"
```bash
pip install -r requirements.txt
```

#### "ChromaDB initialization failed"
```bash
# Delete old ChromaDB cache
rm -rf data/chroma
# Restart server to recreate
python -m uvicorn app.main:app --reload
```

#### "GROQ_API_KEY not found"
- Check `.env` file exists in project root
- Verify API key is correct from groq.com
- Restart backend after adding key

#### "Port 8000 already in use"
```bash
# macOS/Linux
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Frontend Issues

#### "VITE_API_URL is undefined"
- Check `.env.local` exists in `Intellidocs AI - frontend/` folder
- Ensure variable is set correctly
- Restart dev server: `npm run dev`

#### "npm: command not found"
- Install Node.js from https://nodejs.org/
- Verify installation: `node --version && npm --version`

#### "Google login not working"
- Verify `VITE_GOOGLE_CLIENT_ID` matches backend
- Check Google OAuth consent screen is configured
- Ensure `http://localhost:5173` is added to authorized origins

### Database Issues

#### "sqlite3.OperationalError: no such column"
Database schema mismatch. Reset:
```bash
rm sql_app.db
python -c "from app.db.database import create_tables; create_tables()"
```

#### "UNIQUE constraint failed: users.email"
User already exists with that email. Use different email for testing.

---

## 📖 Documentation

- **Backend README**: See `/app/README.md`
- **RAG Pipeline**: See `/app/services/rag/README.md`
- **Frontend README**: See `/Intellidocs AI - frontend/README.md`
- **Deployment Guide**: See `DEPLOYMENT.md`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👨‍💻 Author

**Lalith Kasula** - ML Intern @ IntelliDocs
- GitHub: [@Lalith0024](https://github.com/Lalith0024)
- Email: lalithkasula@example.com

---

## 🙏 Acknowledgments

- **Groq AI** for lightning-fast Llama 3.1 inference
- **Chroma** for vector database simplicity
- **FastAPI** for incredible developer experience
- **React** & **Tailwind** for UIs


---

**Built with ❤️ for intelligent document analysis.**
