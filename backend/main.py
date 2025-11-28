from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .database import engine, Base
from .routers import stories
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Valedictory Storytelling App")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media directory
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

# Include routers
app.include_router(stories.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Valedictory Storytelling App Backend is running"}

class PasswordRequest(BaseModel):
    password: str

@app.post("/api/verify-password")
def verify_password(request: PasswordRequest):
    edit_password = os.getenv("EDIT_PASSWORD")
    if not edit_password:
        return {"success": False, "message": "Password not configured"}
    
    if request.password == edit_password:
        return {"success": True}
    else:
        return {"success": False, "message": "Incorrect password"}
