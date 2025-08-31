#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from api.rag_api import app

# For WSGI servers like Gunicorn
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
