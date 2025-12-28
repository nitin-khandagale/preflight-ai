"""FastAPI application setup."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

# Create FastAPI app
app = FastAPI(
    title="Preflight API",
    description="API for running preflight tests and retrieving results",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/v1")

# Health check at root
@app.get("/health")
async def root_health():
    """Root health check endpoint."""
    return {"status": "ok", "message": "Preflight API is running"}
