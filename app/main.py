"""
AI Text Cleaning API
Main application entry point with all routes, middleware, and startup logic.
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from app.database import engine
from app.models.base import Base
from app.routes import auth, clean, subscriptions, api_keys
from app.config import get_settings

from contextlib import asynccontextmanager


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app

app = FastAPI(
    title="AI Text Cleaning API",
    description="Production-grade text cleaning and autocorrection service with subscription management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ============================================================================
# Middleware
# ============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Routes
# ============================================================================

app.include_router(auth.router)
app.include_router(clean.router)
app.include_router(subscriptions.router)
app.include_router(api_keys.router)


# ============================================================================
# Health & Status Endpoints
# ============================================================================



@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "service": "AI Text Cleaning API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/", tags=["info"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Text Cleaning API",
        "version": "1.0.0",
        "description": "Production-grade text cleaning and autocorrection service",
        "docs": "/docs",
        "api_base": "/",
        "endpoints": {
            "auth": "/auth/*",
            "text_cleaning": "/clean/*",
            "subscriptions": "/subscriptions/*",
            "api_keys": "/api-keys/*",
            "health": "/health",
        },
    }


# ============================================================================
# Startup & Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Startup event: seed default plans if they don't exist."""
    logger.info("Starting AI Text Cleaning API...")
    
    # TODO: Seed default plans (free, starter, pro, enterprise)
    # This would run database migrations and create default data
    logger.info("Application started successfully")
