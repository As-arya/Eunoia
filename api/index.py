"""
Vercel Serverless Function - Flask API for Euonia
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
import os
import hashlib

app = Flask(__name__)
app.url_map.strict_slashes = False  # Allow with or without trailing slash
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'euonia-secret-key-2024')
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'euonia-jwt-secret-2024')

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# In-memory storage (demo - resets on cold start)
USERS = {}

def create_token(user_id, expires_hours=1):
    return jwt.encode({'sub': str(user_id), 'exp': datetime.utcnow() + timedelta(hours=expires_hours)}, JWT_SECRET, algorithm='HS256')

def get_user_id():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        try:
            return jwt.decode(auth[7:], JWT_SECRET, algorithms=['HS256']).get('sub')
        except:
            pass
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

# ========== HEALTH ==========
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

# ========== AUTH ==========
@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json() or {}
        name, email, password = data.get('name', '').strip(), data.get('email', '').strip().lower(), data.get('password', '')
        if not all([name, email, password]):
            return jsonify({'error': 'All fields required'}), 400
        if email in USERS:
            return jsonify({'error': 'Email exists'}), 409
        uid = len(USERS) + 1
        USERS[email] = {'id': uid, 'name': name, 'email': email, 'pw': hashlib.sha256(password.encode()).hexdigest()}
        return jsonify({'message': 'Registered', 'user': {'id': uid, 'name': name, 'email': email}, 'access_token': create_token(uid), 'refresh_token': create_token(uid, 720)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json() or {}
        email, password = data.get('email', '').strip().lower(), data.get('password', '')
        user = USERS.get(email)
        if not user or user['pw'] != hashlib.sha256(password.encode()).hexdigest():
            return jsonify({'error': 'Invalid credentials'}), 401
        return jsonify({'message': 'Login successful', 'user': {'id': user['id'], 'name': user['name'], 'email': user['email']}, 'access_token': create_token(user['id']), 'refresh_token': create_token(user['id'], 720)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me')
@auth_required
def auth_me(uid):
    for u in USERS.values():
        if u['id'] == int(uid):
            return jsonify({'id': u['id'], 'name': u['name'], 'email': u['email']})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/auth/refresh', methods=['POST'])
def refresh():
    uid = get_user_id()
    return jsonify({'access_token': create_token(uid)}) if uid else (jsonify({'error': 'Invalid'}), 401)

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out'})

# ========== USERS (frontend calls /users/me) ==========
@app.route('/api/users/me', methods=['GET', 'PUT', 'OPTIONS'])
@auth_required
def users_me(uid):
    if request.method == 'OPTIONS':
        return '', 200
    for u in USERS.values():
        if u['id'] == int(uid):
            return jsonify({'id': u['id'], 'name': u['name'], 'email': u['email'], 'completedSessions': 0, 'streak': 0, 'joinDate': '2024-01-01'})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/users/me/preferences', methods=['GET', 'PUT'])
@auth_required
def preferences(uid):
    return jsonify({'theme': 'dark', 'notifications': True})

@app.route('/api/users/profile', methods=['GET', 'PUT'])
@auth_required
def profile(uid):
    for u in USERS.values():
        if u['id'] == int(uid):
            return jsonify({'id': u['id'], 'name': u['name'], 'email': u['email'], 'completedSessions': 0, 'streak': 0, 'joinDate': '2024-01-01'})
    return jsonify({'error': 'Not found'}), 404

# ========== SESSIONS ==========
@app.route('/api/sessions', methods=['GET', 'POST', 'OPTIONS'])
@auth_required
def sessions(uid):
    if request.method == 'OPTIONS':
        return '', 200
    if request.method == 'POST':
        return jsonify({'id': 1, 'status': 'active', 'messages': [], 'title': 'New Session', 'created_at': datetime.utcnow().isoformat()}), 201
    return jsonify({'sessions': [], 'total': 0, 'page': 1, 'per_page': 20})

@app.route('/api/sessions/recent', methods=['GET'])
@auth_required
def recent_sessions(uid):
    return jsonify([])

@app.route('/api/sessions/<int:sid>', methods=['GET', 'DELETE'])
@auth_required
def session_detail(uid, sid):
    if request.method == 'DELETE':
        return jsonify({'message': 'Deleted'})
    return jsonify({'id': sid, 'status': 'completed', 'messages': [], 'summary': 'Demo session', 'created_at': '2024-01-01T00:00:00Z', 'title': 'Session'})

@app.route('/api/sessions/<int:sid>/messages', methods=['GET', 'POST'])
@auth_required
def messages(uid, sid):
    if request.method == 'POST':
        return jsonify({'id': 1, 'content': 'This is a demo response. Full AI chatbot requires complete backend.', 'role': 'assistant', 'session_id': sid}), 201
    return jsonify([])

@app.route('/api/sessions/<int:sid>/end', methods=['POST'])
@auth_required
def end_session(uid, sid):
    return jsonify({'id': sid, 'status': 'completed', 'summary': 'Session completed'})

@app.route('/api/sessions/<int:sid>/insights', methods=['GET'])
@auth_required
def session_insights(uid, sid):
    return jsonify({'session_id': sid, 'mood_score': 7, 'emotions': [], 'recommendations': []})

# ========== SCREENING ==========
@app.route('/api/screening/questions')
def questions():
    return jsonify([
        {'id': 1, 'text': 'How are you feeling today?', 'category': 'mood', 'options': [
            {'id': 1, 'text': 'Great', 'score': 5},
            {'id': 2, 'text': 'Good', 'score': 4},
            {'id': 3, 'text': 'Okay', 'score': 3},
            {'id': 4, 'text': 'Not so good', 'score': 2},
            {'id': 5, 'text': 'Bad', 'score': 1}
        ]},
        {'id': 2, 'text': 'How well did you sleep last night?', 'category': 'sleep', 'options': [
            {'id': 1, 'text': 'Very well', 'score': 5},
            {'id': 2, 'text': 'Well', 'score': 4},
            {'id': 3, 'text': 'Average', 'score': 3},
            {'id': 4, 'text': 'Poorly', 'score': 2},
            {'id': 5, 'text': 'Very poorly', 'score': 1}
        ]}
    ])

@app.route('/api/screening/submit', methods=['POST'])
@auth_required
def submit_screening(uid):
    return jsonify({'score': 75, 'level': 'moderate', 'recommendations': []})

@app.route('/api/screening/sessions/<int:sid>/next-question', methods=['GET'])
@auth_required
def next_question(uid, sid):
    return jsonify({
        'status': 'ongoing',
        'progress': '1/25',
        'question': {
            'id': 1,
            'text': 'Bagaimana perasaanmu hari ini?',
            'category': 'mood',
            'question_number': 1,
            'total_questions': 25,
            'options': [
                {'id': 1, 'text': 'Sangat Baik', 'score': 5},
                {'id': 2, 'text': 'Baik', 'score': 4},
                {'id': 3, 'text': 'Biasa Saja', 'score': 3},
                {'id': 4, 'text': 'Kurang Baik', 'score': 2},
                {'id': 5, 'text': 'Buruk', 'score': 1}
            ]
        }
    })

@app.route('/api/screening/sessions/<int:sid>/answer', methods=['POST'])
@auth_required
def submit_answer(uid, sid):
    return jsonify({
        'ai_empathy_reply': 'Terima kasih sudah berbagi. Perasaanmu valid dan aku menghargai keterbukaanmu. 💙',
        'status': 'ongoing',
        'progress': '2/25',
        'question': {
            'id': 2,
            'text': 'Bagaimana kualitas tidurmu semalam?',
            'category': 'sleep',
            'question_number': 2,
            'total_questions': 25,
            'options': [
                {'id': 1, 'text': 'Sangat Nyenyak', 'score': 5},
                {'id': 2, 'text': 'Nyenyak', 'score': 4},
                {'id': 3, 'text': 'Cukup', 'score': 3},
                {'id': 4, 'text': 'Kurang Nyenyak', 'score': 2},
                {'id': 5, 'text': 'Tidak Bisa Tidur', 'score': 1}
            ]
        }
    })

@app.route('/api/screening/sessions/<int:sid>/summary', methods=['GET'])
@auth_required
def screening_summary(uid, sid):
    return jsonify({
        'session_id': sid,
        'total_score': 75,
        'phq9_score': 5,
        'gad7_score': 4,
        'wellness_score': 70,
        'mood_summary': 'Your overall mood appears stable.',
        'recommendations': ['Continue practicing self-care', 'Consider talking to a professional if needed']
    })

@app.route('/api/screening/sessions/<int:sid>/end', methods=['POST'])
@auth_required
def end_screening(uid, sid):
    return jsonify({
        'session_id': sid,
        'status': 'completed',
        'summary': 'Session ended successfully'
    })

# ========== INSIGHTS ==========
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

# ========== CATCH-ALL ==========
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def catch_all(path):
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'error': f'Endpoint /api/{path} not found'}), 404
