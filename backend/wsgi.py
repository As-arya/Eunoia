"""
WSGI Configuration for PythonAnywhere
This file is used by PythonAnywhere to run the Flask app
"""
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/Eunoia/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['SECRET_KEY'] = 'euonia-secret-key-2024'
os.environ['JWT_SECRET_KEY'] = 'euonia-jwt-secret-2024'
os.environ['GEMINI_API_KEY'] = 'YOUR_GEMINI_API_KEY'  # Add your Gemini API key here

# Import the Flask app
from app import create_app

# Create the application instance
application = create_app()
