"""
Main entry point for Render deployment.
Exports the Flask application instance 'app' for WSGI servers like Gunicorn.
Usage: gunicorn main:app or gunicorn app:app
"""

import os
import sys
from pathlib import Path

# Ensure project root is at the head of sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
