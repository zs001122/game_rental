"""
Vercel API Entry Point for Flask Application
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app import create_app

# Create Flask app
app = create_app()

# Initialize database
with app.app_context():
    from backend.models import db
    # Create tables if they don't exist
    db.create_all()

# Export app for Vercel
if __name__ == '__main__':
    app.run()
