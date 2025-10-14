"""
FastAPI Main Application Entry Point
This file starts the server and connects all routes
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Pillinfo API",
    description="Drug Information Chatbot - AI-powered medication identification and information system",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc"  # ReDoc at http://localhost:8000/redoc
)

# ==================== CORS MIDDLEWARE ====================
# This allows your frontend (React) to communicate with the backend

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:3000",  # Create React App default port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# ==================== INCLUDE ROUTERS ====================
# Connect your API routes

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
            "image_lookup": "POST /lookup/image",
            "manual_lookup": "POST /lookup/manual",
            "health_check": "GET /health",
            "seed_cache": "POST /cache/seed"
        }
    }

# ==================== STARTUP EVENT ====================

@app.on_event("startup")
async def startup_event():
    """Runs when the server starts"""
    print("=" * 60)
    print("PILLINFO API SERVER STARTING...")
    print("=" * 60)
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("Ready to identify drugs")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the server shuts down"""
    print("\n" + "=" * 60)
    print("PILLINFO API SERVER SHUTTING DOWN...")
    print("=" * 60)

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    # This runs if you execute: python backend/main.py
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )