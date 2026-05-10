import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    created_at = Column(DateTime, default=utc_now)
    
    # Google OAuth fields
    google_id = Column(String, unique=True, nullable=True, index=True)
    profile_picture = Column(String, nullable=True)

    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="documents")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    chunk_index = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)

    document = relationship("Document")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    chat_id = Column(String, ForeignKey("chats.id"), nullable=False)
    role = Column(String, nullable=False) # user or assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    chat = relationship("Chat", back_populates="messages")
