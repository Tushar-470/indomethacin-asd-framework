"""
FastAPI application entry point for the ASD Framework Web Application.

This is a THIN presentation layer on top of the frozen asd_mcda v1.0.0 computational engine.
All scientific calculations are performed by importing asd_mcda directly.

Usage:
    python -m backend.main
    # or
    uvicorn backend.main:app --reload --port 8000
"""

import sys
from pathlib import Path

# Ensure the project root is in sys.path so asd_mcda and backend can be imported
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SRC_DIR = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api import drugs, polymers, screening, history
from backend.services.engine_adapter import get_engine_version

app = FastAPI(
    title="PharmaPolySCOPE API",
    description=(
        "Pharmaceutical Polymer Screening and Computational Optimization Platform API. "
        "A Four-Criterion Computational Framework for Rational Polymer Selection in Amorphous Solid Dispersions. "
        "Computational engine powered by asd_mcda v" + get_engine_version()
    ),
    version="1.5.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS for local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(drugs.router)
app.include_router(polymers.router)
app.include_router(screening.router)
app.include_router(history.router)


@app.get("/api/version")
async def version():
    """Return engine and web app version information."""
    return {
        "engine_version": get_engine_version(),
        "web_version": "1.0.0",
        "framework": "ASD Computational Polymer Screening Framework",
        "status": "Computational Phase Complete — Experimental Phase Pending",
    }


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "engine": get_engine_version()}


# Serve frontend static files in production mode
frontend_dist = PROJECT_ROOT / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(PROJECT_ROOT / "backend")],
    )
