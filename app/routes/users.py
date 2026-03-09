from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.services.hash import hash_password
from app.core.security import create_access_token
from app.services.hash import verify_password
from app.models import User
from fastapi import Depends
from app.core.security import oauth2_scheme, verify_token
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import security
from app.services.ai_service import generate_content

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
    
# @router.post("/generate")
# def generate_ai_content(prompt: str):
#     result = generate_content(prompt)
#     return {"response": result}
    
        