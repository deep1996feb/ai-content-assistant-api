from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os
load_dotenv()
from app.database import engine, Base
from app import models
from app.routes import users
from dotenv import load_dotenv
from app.routes import users, ai_routes
from fastapi.responses import JSONResponse


app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")

def home():
    return {"message": "API is running"}

@app.get("/health")

def health():
    return {"status": "OK"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error"
        }
    )

app.include_router(users.router, prefix="/user", tags=["User"])
app.include_router(ai_routes.router, prefix="/ai", tags=["AI"])
