"""
FastAPI Main Application Entry Point
This file starts the server and connects all routes
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

# ==================== LIFESPAN EVENTS ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    from services.text_processor import TextProcessor
    
    # Create text_processor instance and warm up
    text_processor = TextProcessor()
    text_processor.process_text("warmup", use_ner=True)
    
    yield

# Create FastAPI app
app = FastAPI(
    title="Pillinfo API",
    description="Drug Information Chatbot - AI-powered medication identification and information system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ==================== CORS MIDDLEWARE ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== INCLUDE ROUTERS ====================
from api.routes import router
app.include_router(router, tags=["Drug Lookup"])

# ==================== ROOT ENDPOINT ====================
@app.get("/")
async def root():
    """Welcome endpoint - confirms server is running"""
    return {
        "message": "Welcome to Pillinfo API",
        "status": "running",
        "docs": "/docs",
        "version": "1.0.0",
        "endpoints": {
            "text_lookup": "POST /lookup/text",
            "image_lookup": "POST /lookup/image"
        }
    }

# ==================== RUN SERVER ====================
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT")),
        reload=True,
        log_level="info"
    )