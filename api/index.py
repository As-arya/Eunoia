"""
Vercel Serverless Function - Flask API
"""
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
import os
import hashlib

# Create Flask app - Vercel looks for 'app' variable
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'euonia-secret-key-2024')
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'euonia-jwt-secret-2024')

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# In-memory storage (demo only - resets on cold start)
USERS = {}

def create_token(user_id, expires_hours=1):
    payload = {
        'sub': str(user_id),
        'exp': datetime.utcnow() + timedelta(hours=expires_hours),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload.get('sub')
    except:
        return None

def get_user_id():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return verify_token(auth[7:])
    return None

def auth_required(f):
    def wrapper(*args, **kwargs):
        uid = get_user_id()
        if not uid:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(uid, *args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.after_request
def cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Health
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

# Auth
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
            return jsonify({'error': 'Email exists'}), 409
        
        uid = len(USERS) + 1
        USERS[email] = {'id': uid, 'name': name, 'email': email, 'pw': hashlib.sha256(password.encode()).hexdigest()}
        
        return jsonify({
            'message': 'Registered',
            'user': {'id': uid, 'name': name, 'email': email},
            'access_token': create_token(uid),
            'refresh_token': create_token(uid, 720)
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
        
        user = USERS.get(email)
        if not user or user['pw'] != hashlib.sha256(password.encode()).hexdigest():
            return jsonify({'error': 'Invalid credentials'}), 401
        
        return jsonify({
            'message': 'Login successful',
            'user': {'id': user['id'], 'name': user['name'], 'email': user['email']},
            'access_token': create_token(user['id']),
            'refresh_token': create_token(user['id'], 720)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me')
@auth_required
def me(uid):
    for u in USERS.values():
        if u['id'] == int(uid):
            return jsonify({'id': u['id'], 'name': u['name'], 'email': u['email']})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/auth/refresh', methods=['POST'])
def refresh():
    uid = get_user_id()
    if not uid:
        return jsonify({'error': 'Invalid token'}), 401
    return jsonify({'access_token': create_token(uid)})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out'})

# User
@app.route('/api/users/profile')
@auth_required
def profile(uid):
    for u in USERS.values():
        if u['id'] == int(uid):
            return jsonify({'id': u['id'], 'name': u['name'], 'email': u['email'], 'completedSessions': 0, 'streak': 0, 'joinDate': '2024-01-01'})
    return jsonify({'error': 'Not found'}), 404

# Sessions
@app.route('/api/sessions')
@auth_required
def sessions(uid):
    return jsonify([])

@app.route('/api/sessions', methods=['POST'])
@auth_required
def create_session(uid):
    return jsonify({'id': 1, 'status': 'active', 'messages': []}), 201

@app.route('/api/sessions/<int:sid>')
@auth_required
def get_session(uid, sid):
    return jsonify({'id': sid, 'status': 'completed', 'messages': [], 'summary': 'Demo', 'created_at': '2024-01-01T00:00:00Z'})

@app.route('/api/sessions/<int:sid>/messages', methods=['POST'])
@auth_required
def send_msg(uid, sid):
    return jsonify({'id': 1, 'content': 'Demo response', 'role': 'assistant', 'session_id': sid}), 201

# Screening
@app.route('/api/screening/questions')
def questions():
    return jsonify([{'id': 1, 'text': 'How are you feeling?', 'category': 'mood'}])

# Insights
@app.route('/api/insights/dashboard')
@auth_required
def dashboard(uid):
    return jsonify({'moodTrend': [], 'sessionsCompleted': 0, 'currentStreak': 0, 'averageMood': 0})

@app.route('/api/insights/mood-trend')
@auth_required
def mood_trend(uid):
    return jsonify({'trend': 'neutral', 'change_percentage': 0, 'data_points': []})

@app.route('/api/insights/emotions')
@auth_required
def emotions(uid):
    return jsonify({'emotions': [], 'period': 'weekly'})

@app.route('/api/insights/observations')
@auth_required
def observations(uid):
    return jsonify([])

@app.route('/api/insights/observations/<int:oid>/read', methods=['POST'])
@auth_required
def mark_read(uid, oid):
    return jsonify({'success': True})

# Catch-all
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def catch_all(path):
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'error': f'Not found: /api/{path}'}), 404
