from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import User
from app.schemas.all import UserCreate, UserResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.google_auth import verify_google_token, GoogleTokenError
from app.api.dependencies import get_current_user

# Pydantic model for Google login request
class GoogleLoginRequest(BaseModel):
    idToken: str

router = APIRouter()

@router.post("/signup", response_model=Token)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Generate token for the new user
    access_token = create_access_token(subject=db_user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/google/token", response_model=Token)
def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Google OAuth login endpoint.
    Accepts Google ID token, verifies it, and returns JWT access token.
    """
    try:
        # Verify Google token
        user_info = verify_google_token(request.idToken)
    except GoogleTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
    # Find or create user
    db_user = db.query(User).filter(User.email == user_info['email']).first()
    
    is_new_user = False
    
    if not db_user:
        # Create new user from Google info
        db_user = User(
            email=user_info['email'],
            google_id=user_info['google_id'],
            profile_picture=user_info.get('picture', ''),
            hashed_password=None  # OAuth users don't need password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        is_new_user = True
    else:
        # Update existing user with Google info if not already set
        if not db_user.google_id:
            db_user.google_id = user_info['google_id']
        if not db_user.profile_picture and user_info.get('picture'):
            db_user.profile_picture = user_info['picture']
        db.commit()
    
    # Generate JWT token
    access_token = create_access_token(subject=db_user.id)
    return {"access_token": access_token, "token_type": "bearer", "is_new_user": is_new_user}

