"""
Run script for the ASL Model Training Hub
"""
import os
import sys
from flask_app.main import create_app

if __name__ == '__main__':
    # Set up the path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Create and run the app
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
