"""
Vercel API Entry Point for Flask Application
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app

# Create Flask app
app = create_app()

# Initialize database
with app.app_context():
    from backend.models import db
    db.create_all()
