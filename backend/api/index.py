"""
Vercel Serverless Function Entry Point for Euonia Backend
"""
import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create the Flask app instance for Vercel
app = create_app()

# Vercel looks for 'app' or 'handler' variable
# This is the WSGI application that Vercel will use
