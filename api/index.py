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
    from backend.models import db, User
    
    # Create Flask app
    app = create_app()
    
    # Initialize database
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Initialize with default test user if needed
        if User.query.count() == 0:
            # Create a test admin user
            admin_user = User(
                username='admin',
                email='admin@example.com',
                phone='13800000000',
                balance=10000.00,
                is_admin=True
            )
            admin_user.set_password('admin123')
            
            # Create some test users
            test_user = User(
                username='user001',
                email='user001@example.com',
                phone='13800000001',
                balance=500.00,
                is_admin=False
            )
            test_user.set_password('123456')
            
            db.session.add(admin_user)
            db.session.add(test_user)
            db.session.commit()
            
            print("Default users initialized")
        
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
