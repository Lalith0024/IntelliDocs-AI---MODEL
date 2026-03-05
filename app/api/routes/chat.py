from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Chat, Message
from app.api.dependencies import get_current_user
from app.schemas.all import ChatQueryRequest, ChatResponse, ChatListResponse, MessageResponse
from app.services.rag.pipeline import search_documents
from app.services.rag.llm import generate_answer
from pydantic import BaseModel

router = APIRouter()

class ChatRenameRequest(BaseModel):
    title: str

@router.get("/", response_model=list[ChatListResponse])
def get_chats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chats = db.query(Chat).filter(Chat.user_id == current_user.id).order_by(Chat.created_at.desc()).all()
    return chats

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.post("/query")
def chat_query(req: ChatQueryRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not req.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Init or fetch Chat
    chat = None
    if req.chat_id:
        chat = db.query(Chat).filter(Chat.id == req.chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        title = req.question[:30] + "..." if len(req.question) > 30 else req.question
        chat = Chat(user_id=current_user.id, title=title)
        db.add(chat)
        db.commit()
        db.refresh(chat)
    
    # Save User Message
    user_msg = Message(chat_id=chat.id, role="user", content=req.question)
    db.add(user_msg)
    
    # RAG PIPELINE
    docs = search_documents(db, req.question, current_user.id)
    user_display_name = current_user.email.split('@')[0] if current_user.email else "Friend"
    answer = generate_answer(req.question, docs, user_name=user_display_name)
    
    # Save Assistant Message
    assistant_msg = Message(chat_id=chat.id, role="assistant", content=answer)
    db.add(assistant_msg)
    db.commit()
    
    return {
        "chat_id": chat.id,
        "answer": answer,
        "valid_count": len(docs),
        "docs": docs
    }

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
    # Delete all messages first
    db.query(Message).filter(Message.chat_id == chat.id).delete()
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted", "id": chat_id}
