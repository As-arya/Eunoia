"""
Vercel Serverless Function - Main API Entry Point
This file handles all /api/* routes for Vercel Python runtime
"""
import sys
import os

# Add backend app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from datetime import timedelta
import json

# Create minimal Flask app for Vercel serverless
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'euonia-secret-key-2024')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'euonia-jwt-secret-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize extensions
CORS(app, origins=["*"], supports_credentials=True)
jwt = JWTManager(app)

# In-memory storage for serverless (demo purposes)
users_db = {}
sessions_db = {}
user_counter = [0]

# JWT handlers
@jwt.invalid_token_loader
def invalid_token(error):
    return jsonify({'error': 'Invalid token'}), 401

@jwt.unauthorized_loader
def unauthorized(error):
    return jsonify({'error': 'Missing token'}), 401

@jwt.expired_token_loader
def expired_token(header, payload):
    return jsonify({'error': 'Token expired'}), 401

# Health check
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'platform': 'vercel'})

# Auth routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not all([name, email, password]):
        return jsonify({'error': 'All fields required'}), 400
    
    if email in users_db:
        return jsonify({'error': 'Email already exists'}), 409
    
    user_counter[0] += 1
    user_id = user_counter[0]
    
    users_db[email] = {
        'id': user_id,
        'name': name,
        'email': email,
        'password': password  # In production, hash this!
    }
    
    user = users_db[email]
    return jsonify({
        'message': 'Registered',
        'user': {'id': user['id'], 'name': user['name'], 'email': user['email']},
        'access_token': create_access_token(identity=str(user_id)),
        'refresh_token': create_refresh_token(identity=str(user_id))
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = users_db.get(email)
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'user': {'id': user['id'], 'name': user['name'], 'email': user['email']},
        'access_token': create_access_token(identity=str(user['id'])),
        'refresh_token': create_refresh_token(identity=str(user['id']))
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    for user in users_db.values():
        if user['id'] == user_id:
            return jsonify({'id': user['id'], 'name': user['name'], 'email': user['email']})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    return jsonify({'access_token': create_access_token(identity=identity)}), 200

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logged out'}), 200

# User routes
@app.route('/api/users/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    for user in users_db.values():
        if user['id'] == user_id:
            return jsonify({
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'completedSessions': 0,
                'streak': 0,
                'joinDate': '2024-01-01'
            })
    return jsonify({'error': 'Not found'}), 404

# Sessions routes (minimal for demo)
@app.route('/api/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    return jsonify([])

@app.route('/api/sessions', methods=['POST'])
@jwt_required()
def create_session():
    return jsonify({'id': 1, 'status': 'active', 'messages': []}), 201

# Screening routes (minimal)
@app.route('/api/screening/questions', methods=['GET'])
def get_questions():
    return jsonify([
        {'id': 1, 'text': 'How are you feeling today?', 'category': 'mood'},
        {'id': 2, 'text': 'How well did you sleep last night?', 'category': 'sleep'},
    ])

# Insights routes (complete)
@app.route('/api/insights/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    return jsonify({
        'moodTrend': [],
        'sessionsCompleted': 0,
        'currentStreak': 0,
        'averageMood': 0
    })

@app.route('/api/insights/mood-trend', methods=['GET'])
@jwt_required()
def get_mood_trend():
    return jsonify({
        'trend': 'neutral',
        'change_percentage': 0,
        'data_points': []
    })

@app.route('/api/insights/emotions', methods=['GET'])
@jwt_required()
def get_emotions():
    return jsonify({
        'emotions': [],
        'period': 'weekly'
    })

@app.route('/api/insights/observations', methods=['GET'])
@jwt_required()
def get_observations():
    return jsonify([])

@app.route('/api/insights/observations/<int:observation_id>/read', methods=['POST'])
@jwt_required()
def mark_observation_read(observation_id):
    return jsonify({'success': True})

# Sessions routes (complete)
@app.route('/api/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    return jsonify({
        'id': session_id,
        'status': 'completed',
        'messages': [],
        'summary': 'Demo session',
        'created_at': '2024-01-01T00:00:00Z'
    })

@app.route('/api/sessions/<int:session_id>/messages', methods=['POST'])
@jwt_required()
def send_message(session_id):
    data = request.get_json() or {}
    return jsonify({
        'id': 1,
        'content': 'This is a demo response. The full chatbot functionality requires the complete backend deployment.',
        'role': 'assistant',
        'session_id': session_id
    }), 201

# Catch-all for API routes
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def catch_all(path):
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'error': f'Endpoint /api/{path} not found'}), 404

# Vercel handler
def handler(request):
    return app(request.environ, request.start_response)
