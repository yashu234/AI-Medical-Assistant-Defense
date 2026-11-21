"""
FastAPI Main Application.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ai_medical_assistant")


@asynccontextmanager
async def lifespan(app: FastAPI):
    mode_str = "Local Simulated Demo Mode (no API key)" if settings.is_local_demo_mode else f"OpenAI API ({settings.OPENAI_MODEL})"
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Operating Mode: {mode_str}")
    logger.info(f"Safety Disclaimer: {settings.PERSISTENT_SAFETY_DISCLAIMER}")
    yield
    logger.info("Shutting down AI Medical Assistant.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Educational demo healthcare chatbot with transparent intent routing, "
        "strict emergency detection, PDF report explanation, and specialist guidance."
    ),
    lifespan=lifespan,
)

# Configure CORS for local frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "disclaimer": settings.PERSISTENT_SAFETY_DISCLAIMER,
        "docs_url": "/docs",
        "health_url": "/health",
    }
