import os
import sys

# 1. CRITICAL: SQLite Shim for ChromaDB on Linux/Render
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("Successfully shimmed sqlite3 with pysqlite3-binary")
except ImportError:
    print("pysqlite3-binary not found, using system sqlite3")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, documents, chat
from app.db.database import create_tables

# 2. Ensure data directories exist
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/chroma", exist_ok=True)

print("Initializing database tables...")
create_tables()
print("Database initialized.")

app = FastAPI(title="Intellidocs AI", version="2.0.0")

# Create tables
create_tables()

app = FastAPI(title="Intellidocs AI", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chats", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Intellidocs AI Backend"}
