import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Document
from app.api.dependencies import get_current_user
from app.schemas.all import DocumentResponse
from app.services.rag.pipeline import add_document_to_index

router = APIRouter()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentResponse)
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed_extensions = {".txt", ".pdf", ".json", ".csv", ".png", ".jpg", ".jpeg"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Extension {ext} not supported. We accept .txt, .pdf, .json, .csv, and images (.png, .jpg)."
        )
    
    # Create DB Entry
    db_doc = Document(user_id=current_user.id, filename=file.filename, file_path="")
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Save physically using doc ID to prevent overrides
    file_path = os.path.join(UPLOAD_DIR, f"{db_doc.id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_doc.file_path = file_path
    db_doc.status = "processing"
    db.commit()

    # Add to RAG Index
    try:
        add_document_to_index(db=db, file_path=file_path, filename=file.filename, document_id=db_doc.id, user_id=current_user.id)
        db_doc.status = "ready"
    except Exception as e:
        print("Vector Index Error:", e)
        db_doc.status = "failed"
    
    db.commit()
    db.refresh(db_doc)
    return db_doc

@router.get("/", response_model=list[DocumentResponse])
def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    docs = db.query(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc()).all()
    return docs

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except:
        pass

    # Ideally remove from ChromaDB here:
    from app.services.rag.vector_db import get_collection
    collection = get_collection()
    collection.delete(where={"document_id": document_id})

    db.delete(doc)
    db.commit()
    return {"status": "deleted"}
