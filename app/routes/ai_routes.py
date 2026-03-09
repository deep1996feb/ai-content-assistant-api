from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.services.ai_service import generate_content
from app.database import get_db
from app.core.security import oauth2_scheme, verify_token,security
from pydantic import BaseModel
from app.models import User, PromptHistory
from app.services.rate_limiter import check_rate_limit

router = APIRouter(prefix="/ai")

class PromptRequest(BaseModel):
    prompt: str
    mode: str
    count: int = 1

@router.post("/generate")
def generate_ai(
    request: PromptRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == email).first()
    check_rate_limit(db, user.id)
    output = generate_content(request.prompt, request.mode, request.count)
    history = PromptHistory(
        user_id = user.id,
        prompt = request.prompt,
        response="\n".join(output) if isinstance(output, list) else output
    )
    db.add(history)
    db.commit()
    return {"response": output}

