import time
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Chat, Message
from app.api.dependencies import get_current_user
from app.schemas.all import ChatQueryRequest, ChatResponse, ChatListResponse
from app.services.rag.pipeline import search_documents
from app.services.rag.llm import generate_answer, generate_answer_stream
from pydantic import BaseModel

router = APIRouter()

class ChatRenameRequest(BaseModel):
    title: str

@router.post("/query/stream")
async def chat_query_stream(req: ChatQueryRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Production-Grade 'Neural Stream' Endpoint:
    Yields word-by-word synthesis via SSE (Server-Sent Events).
    Demonstrates High-Performance Async I/O & Event-Driven Architecture.
    """
    if not req.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # 1. CHAT SESSION MANAGEMENT
    chat = None
    if req.chat_id:
        chat = db.query(Chat).filter(Chat.id == req.chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        title = req.question[:30] + "..." if len(req.question) > 30 else req.question
        chat = Chat(user_id=current_user.id, title=title)
        db.add(chat)
        db.commit()
        db.refresh(chat)
    
    # 2. SAVE OPERATOR INTENT
    user_msg = Message(chat_id=chat.id, role="user", content=req.question)
    db.add(user_msg)
    
    # 3. INTENT DETECTION & AGENTIC ROUTING
    intent = "query"
    query_lower = req.question.lower()
    if any(k in query_lower for k in ["summarize", "summary", "brief"]):
        intent = "summary"
    elif any(k in query_lower for k in ["missing", "missing info", "gaps", "audit"]):
        intent = "audit"
    elif any(k in query_lower for k in ["timeline", "events", "when"]):
        intent = "timeline"
    elif any(k in query_lower for k in ["quiz", "test", "mcq", "questions"]):
        intent = "quiz"

    # 4. HIGH-DENSITY RETRIEVAL (ASYNC-LITE)
    top_k = 12 if intent in ["summary", "audit"] else 6
    docs = [d for d in search_documents(db, req.question, current_user.id, top_k=top_k, document_ids=req.document_ids)]
    
    user_display_name = current_user.email.split('@')[0] if current_user.email else "Friend"

    # 5. STREAMING GENERATION (THE DIFFERENTIATION FACTOR)
    async def stream_generator():
        full_answer = ""
        # We start by sending the metadata (intent, docs, chat_id)
        yield f"data: {json.dumps({'chat_id': chat.id, 'intent': intent, 'valid_count': len(docs), 'docs': docs})}\n\n"
        
        async for chunk in generate_answer_stream(req.question, docs, user_name=user_display_name, intent=intent):
            # Parse the inner chunk data
            if chunk.startswith("data:"):
                raw = chunk.replace("data: ", "").strip()
                if raw == "[DONE]":
                    break
                try:
                    parsed = json.loads(raw)
                    if 'content' in parsed:
                        full_answer += parsed['content']
                except:
                    pass
            yield chunk

        # Generate dynamic follow-up suggestions using the LLM
        from app.services.rag.llm import generate_dynamic_suggestions
        suggestions = generate_dynamic_suggestions(req.question, full_answer)
        yield f"data: {json.dumps({'suggestions': suggestions})}\n\n"
        yield "data: [DONE]\n\n"

        # Final persistent save
        assistant_msg = Message(chat_id=chat.id, role="assistant", content=full_answer)
        db.add(assistant_msg)
        db.commit()

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no"}
    )

@router.post("/query")
def chat_query_sync(req: ChatQueryRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Synchronous Fallback Endpoint for Legacy Queries.
    """
    if not req.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    start_time = time.time()
    chat = None
    if req.chat_id:
        chat = db.query(Chat).filter(Chat.id == req.chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        title = req.question[:30] + "..." if len(req.question) > 30 else req.question
        chat = Chat(user_id=current_user.id, title=title)
        db.add(chat)
        db.commit()
        db.refresh(chat)
    
    # Save User
    user_msg = Message(chat_id=chat.id, role="user", content=req.question)
    db.add(user_msg)
    
    docs = search_documents(db, req.question, current_user.id, document_ids=req.document_ids)
    user_display_name = current_user.email.split('@')[0] if current_user.email else "Friend"
    answer = generate_answer(req.question, docs, user_name=user_display_name)
    
    # Save Assistant
    assistant_msg = Message(chat_id=chat.id, role="assistant", content=answer)
    db.add(assistant_msg)
    db.commit()
    
    total_latency_ms = (time.time() - start_time) * 1000
    
    return {
        "chat_id": chat.id,
        "answer": answer,
        "docs": docs,
        "latency_ms": round(total_latency_ms, 2),
        "valid_count": len(docs)
    }

@router.get("/", response_model=list[ChatListResponse])
def get_chats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Chat).filter(Chat.user_id == current_user.id).order_by(Chat.created_at.desc()).all()

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.put("/{chat_id}/rename")
def rename_chat(chat_id: str, req: ChatRenameRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    chat.title = req.title
    db.commit()
    return {"message": "Chat renamed", "id": chat.id, "title": chat.title}

@router.delete("/{chat_id}")
def delete_chat(chat_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.query(Message).filter(Message.chat_id == chat.id).delete()
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted", "id": chat_id}
