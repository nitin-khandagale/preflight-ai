"""
API Server entry point.

Run with: python api_server.py
Or: uvicorn api_server:app --reload
"""

import uvicorn
from preflight.api.main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
