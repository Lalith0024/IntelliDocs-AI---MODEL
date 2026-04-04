from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

class ChatListResponse(BaseModel):
    id: str
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatQueryRequest(BaseModel):
    question: str
    chat_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
