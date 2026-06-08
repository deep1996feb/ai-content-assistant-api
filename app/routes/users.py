from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.services.hash import hash_password
from app.core.security import create_access_token
from app.services.hash import verify_password
from app.models import User,PromptHistory
from fastapi import Depends
from app.core.security import oauth2_scheme, verify_token
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import security
from app.services.ai_service import generate_content
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM

router = APIRouter()

@router.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(password,user.password):
        raise HTTPException(status_code=400, detail="Invalid Password")
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
@router.get("/profile")
def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
    ):
    token = credentials.credentials.replace("Bearer ", "")
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return{
        "id": user.id,
        "name": user.name,
        "email": user.email
    }
    
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")

        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")


    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
    
@router.get("/history")
def get_prompt_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = db.query(PromptHistory).filter(
        PromptHistory.user_id==current_user.id).order_by(PromptHistory.created_at.desc()).all()
    return{
        "count": len(history),
        "history": [
            {
                "id": item.id,
                "prompt": item.prompt,
                "response": item.response,
                "created_at": item.created_at
            }
            for item in history
        ]
    }
    
@router.delete("/history/{history_id}")
def get_delete_prompt_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = db.query(PromptHistory).filter(PromptHistory.id == history_id,
        PromptHistory.user_id==current_user.id).first()
    if not history:
        raise HTTPException(
            status_code=404,
            detail="History record not found"
        )
    db.delete(history)
    db.commit()
    return {
        "message": "History deleted successfully"
    }
    
    
        