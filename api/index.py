"""
Vercel API Entry Point for Flask Application
"""
import sys
import os
from pathlib import Path

try:
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
        
except Exception as e:
    # Log initialization errors
    print(f"Initialization Error: {str(e)}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    
    # Create a minimal Flask app for error handling
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/api/<path:path>')
    def error_handler(path=None):
        return jsonify({
            'error': 'Application initialization failed',
            'message': str(e)
        }), 500

# Export app for Vercel
if __name__ == '__main__':
    app.run()
