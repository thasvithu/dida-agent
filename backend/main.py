from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import routers
from routers import upload, analyze, clean, feature_engineering, report, chat, export, auth, ml_prep

# Create necessary directories
os.makedirs(os.getenv("UPLOAD_DIR", "./uploads"), exist_ok=True)
os.makedirs(os.getenv("TEMP_DIR", "./temp"), exist_ok=True)
os.makedirs("./reports", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 DIDA Backend starting up...")
    logger.info(f"Upload directory: {os.getenv('UPLOAD_DIR', './uploads')}")
    logger.info(f"Temp directory: {os.getenv('TEMP_DIR', './temp')}")
    yield
    logger.info("👋 DIDA Backend shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="DIDA - Domain-Aware Intelligent Data Scientist Agent",
    description="Multi-agent AI system for intelligent data analysis, cleaning, and feature engineering",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analysis"])
app.include_router(clean.router, prefix="/api/clean", tags=["Cleaning"])
app.include_router(feature_engineering.router, prefix="/api/feature-engineering", tags=["Feature Engineering"])
app.include_router(report.router, prefix="/api/report", tags=["Reporting"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(ml_prep.router)

# Mount static files for reports
app.mount("/reports", StaticFiles(directory="./reports"), name="reports")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DIDA - Domain-Aware Intelligent Data Scientist Agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    )
