from datetime import date
from fastapi import HTTPException
from app.models import AIUsage

DAILY_LIMIT = 2

def check_rate_limit(db, user_id):
    today = date.today()
    usage = db.query(AIUsage).filter(AIUsage.user_id == user_id,
                                     AIUsage.date == today).first()
    if not usage:
        usage = AIUsage(user_id = user_id,date=today, request_count=1)
        db.add(usage)
        db.commit()
        return
    if usage.request_count >= DAILY_LIMIT:
        raise HTTPException(status_code=429, detail="Daily AI limited reached")
    usage.request_count +=1
    db.commit()