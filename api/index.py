"""
Vercel Serverless Function - Main API Entry Point
Simplified version for Vercel Python runtime
"""
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
import os
import json
import hashlib

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'euonia-secret-key-2024')
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'euonia-jwt-secret-2024')

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Simple in-memory storage (will reset on each cold start)
# For demo purposes only
USERS = {}

def create_token(user_id, expires_hours=1):
    """Create a simple JWT token"""
    payload = {
        'sub': str(user_id),
        'exp': datetime.utcnow() + timedelta(hours=expires_hours),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload.get('sub')
    except:
        return None

def get_current_user_id():
    """Get user ID from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        return verify_token(token)
    return None

def require_auth(f):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(user_id, *args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# CORS preflight handler
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# ============ ROUTES ============

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'platform': 'vercel'})

# Auth routes
@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not all([name, email, password]):
            return jsonify({'error': 'All fields required'}), 400
        
        if email in USERS:
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create user
        user_id = len(USERS) + 1
        USERS[email] = {
            'id': user_id,
            'name': name,
            'email': email,
            'password': hashlib.sha256(password.encode()).hexdigest()
        }
        
        # Create tokens
        access_token = create_token(user_id, expires_hours=1)
        refresh_token = create_token(user_id, expires_hours=720)  # 30 days
        
        return jsonify({
            'message': 'Registered',
            'user': {'id': user_id, 'name': name, 'email': email},
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json() or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = USERS.get(email)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if user['password'] != hashlib.sha256(password.encode()).hexdigest():
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_token(user['id'], expires_hours=1)
        refresh_token = create_token(user['id'], expires_hours=720)
        
        return jsonify({
            'message': 'Login successful',
            'user': {'id': user['id'], 'name': user['name'], 'email': user['email']},
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def me(user_id):
    for user in USERS.values():
        if user['id'] == int(user_id):
            return jsonify({'id': user['id'], 'name': user['name'], 'email': user['email']})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/auth/refresh', methods=['POST'])
def refresh():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'error': 'Invalid refresh token'}), 401
    return jsonify({'access_token': create_token(user_id, expires_hours=1)}), 200

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out'}), 200

# User routes
@app.route('/api/users/profile', methods=['GET'])
@require_auth
def get_profile(user_id):
    for user in USERS.values():
        if user['id'] == int(user_id):
            return jsonify({
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'completedSessions': 0,
                'streak': 0,
                'joinDate': '2024-01-01'
            })
    return jsonify({'error': 'Not found'}), 404

# Sessions routes
@app.route('/api/sessions', methods=['GET'])
@require_auth
def get_sessions(user_id):
    return jsonify([])

@app.route('/api/sessions', methods=['POST'])
@require_auth
def create_session(user_id):
    return jsonify({'id': 1, 'status': 'active', 'messages': []}), 201

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
@require_auth
def get_session(user_id, session_id):
    return jsonify({
        'id': session_id,
        'status': 'completed',
        'messages': [],
        'summary': 'Demo session',
        'created_at': '2024-01-01T00:00:00Z'
    })

@app.route('/api/sessions/<int:session_id>/messages', methods=['POST'])
@require_auth
def send_message(user_id, session_id):
    return jsonify({
        'id': 1,
        'content': 'This is a demo response. Full chatbot requires the complete backend.',
        'role': 'assistant',
        'session_id': session_id
    }), 201

# Screening routes
@app.route('/api/screening/questions', methods=['GET'])
def get_questions():
    return jsonify([
        {'id': 1, 'text': 'How are you feeling today?', 'category': 'mood'},
        {'id': 2, 'text': 'How well did you sleep last night?', 'category': 'sleep'},
    ])

# Insights routes
@app.route('/api/insights/dashboard', methods=['GET'])
@require_auth
def get_dashboard(user_id):
    return jsonify({
        'moodTrend': [],
        'sessionsCompleted': 0,
        'currentStreak': 0,
        'averageMood': 0
    })

@app.route('/api/insights/mood-trend', methods=['GET'])
@require_auth
def get_mood_trend(user_id):
    return jsonify({
        'trend': 'neutral',
        'change_percentage': 0,
        'data_points': []
    })

@app.route('/api/insights/emotions', methods=['GET'])
@require_auth
def get_emotions(user_id):
    return jsonify({
        'emotions': [],
        'period': 'weekly'
    })

@app.route('/api/insights/observations', methods=['GET'])
@require_auth
def get_observations(user_id):
    return jsonify([])

@app.route('/api/insights/observations/<int:observation_id>/read', methods=['POST'])
@require_auth
def mark_observation_read(user_id, observation_id):
    return jsonify({'success': True})

# Catch-all for unknown routes
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def catch_all(path):
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'error': f'Endpoint /api/{path} not found', 'path': path}), 404

# Vercel handler - this is the entry point for Vercel
def handler(event, context):
    """Vercel handler for Python"""
    return app
