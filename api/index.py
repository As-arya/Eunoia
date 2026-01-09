"""
Vercel Serverless Function - Demo API for Euonia
Enhanced demo with rotating questions and varied responses
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
import os
import hashlib
import random

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'euonia-secret-key-2024')
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'euonia-jwt-secret-2024')

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Demo user storage
USERS = {}

# Demo questions pool for rotating
DEMO_QUESTIONS = [
    {'id': 1, 'text': 'Bagaimana perasaanmu hari ini?', 'category': 'mood', 'options': [
        {'id': 1, 'text': 'Sangat Baik 😊', 'score': 5},
        {'id': 2, 'text': 'Baik', 'score': 4},
        {'id': 3, 'text': 'Biasa Saja', 'score': 3},
        {'id': 4, 'text': 'Kurang Baik', 'score': 2},
        {'id': 5, 'text': 'Buruk 😔', 'score': 1}
    ]},
    {'id': 2, 'text': 'Bagaimana kualitas tidurmu semalam?', 'category': 'sleep', 'options': [
        {'id': 1, 'text': 'Sangat Nyenyak', 'score': 5},
        {'id': 2, 'text': 'Nyenyak', 'score': 4},
        {'id': 3, 'text': 'Cukup', 'score': 3},
        {'id': 4, 'text': 'Kurang Nyenyak', 'score': 2},
        {'id': 5, 'text': 'Tidak Bisa Tidur', 'score': 1}
    ]},
    {'id': 3, 'text': 'Seberapa sering kamu merasa cemas akhir-akhir ini?', 'category': 'anxiety', 'options': [
        {'id': 1, 'text': 'Tidak Pernah', 'score': 5},
        {'id': 2, 'text': 'Jarang', 'score': 4},
        {'id': 3, 'text': 'Kadang-kadang', 'score': 3},
        {'id': 4, 'text': 'Sering', 'score': 2},
        {'id': 5, 'text': 'Sangat Sering', 'score': 1}
    ]},
    {'id': 4, 'text': 'Apakah kamu merasa memiliki energi yang cukup?', 'category': 'energy', 'options': [
        {'id': 1, 'text': 'Sangat Berenergi', 'score': 5},
        {'id': 2, 'text': 'Cukup Berenergi', 'score': 4},
        {'id': 3, 'text': 'Normal', 'score': 3},
        {'id': 4, 'text': 'Kurang Berenergi', 'score': 2},
        {'id': 5, 'text': 'Sangat Lelah', 'score': 1}
    ]},
    {'id': 5, 'text': 'Bagaimana hubunganmu dengan orang-orang terdekat?', 'category': 'social', 'options': [
        {'id': 1, 'text': 'Sangat Baik', 'score': 5},
        {'id': 2, 'text': 'Baik', 'score': 4},
        {'id': 3, 'text': 'Biasa Saja', 'score': 3},
        {'id': 4, 'text': 'Kurang Baik', 'score': 2},
        {'id': 5, 'text': 'Bermasalah', 'score': 1}
    ]},
    {'id': 6, 'text': 'Apakah kamu merasa mampu mengelola stres dengan baik?', 'category': 'stress', 'options': [
        {'id': 1, 'text': 'Sangat Mampu', 'score': 5},
        {'id': 2, 'text': 'Mampu', 'score': 4},
        {'id': 3, 'text': 'Kadang Sulit', 'score': 3},
        {'id': 4, 'text': 'Sering Sulit', 'score': 2},
        {'id': 5, 'text': 'Tidak Mampu', 'score': 1}
    ]},
    {'id': 7, 'text': 'Seberapa puas kamu dengan hidupmu saat ini?', 'category': 'satisfaction', 'options': [
        {'id': 1, 'text': 'Sangat Puas', 'score': 5},
        {'id': 2, 'text': 'Puas', 'score': 4},
        {'id': 3, 'text': 'Cukup Puas', 'score': 3},
        {'id': 4, 'text': 'Kurang Puas', 'score': 2},
        {'id': 5, 'text': 'Tidak Puas', 'score': 1}
    ]},
    {'id': 8, 'text': 'Apakah kamu merasa termotivasi untuk melakukan aktivitas?', 'category': 'motivation', 'options': [
        {'id': 1, 'text': 'Sangat Termotivasi', 'score': 5},
        {'id': 2, 'text': 'Termotivasi', 'score': 4},
        {'id': 3, 'text': 'Biasa Saja', 'score': 3},
        {'id': 4, 'text': 'Kurang Termotivasi', 'score': 2},
        {'id': 5, 'text': 'Tidak Termotivasi', 'score': 1}
    ]}
]

# Empathy responses pool
EMPATHY_RESPONSES = [
    "Terima kasih sudah berbagi. Perasaanmu valid dan aku menghargai keterbukaanmu. 💙",
    "Aku mendengarmu. Penting untuk mengakui perasaan kita, apapun itu. 🌟",
    "Terima kasih sudah jujur. Setiap perasaan adalah bagian dari perjalananmu. 💫",
    "Aku senang kamu mau berbagi. Kamu tidak sendirian dalam perjalanan ini. 🤗",
    "Perasaanmu penting. Terima kasih sudah mempercayakannya padaku. 💚",
    "Aku menghargai kejujuranmu. Mari kita lanjutkan eksplorasi bersama. ✨",
    "Setiap langkah kecil menuju kesadaran diri adalah kemajuan. Kamu hebat! 🌈",
    "Terima kasih sudah terbuka. Refleksi diri adalah tanda kekuatan. 💪"
]

# Track demo question index (simple rotation)
question_tracker = {'current': 0, 'answered': 0}

def create_token(user_id, expires_hours=24):
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
    return jsonify({'status': 'ok', 'demo': True})

# ========== AUTH ==========
@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip() or 'Demo User'
        email = data.get('email', '').strip().lower() or 'demo@euonia.app'
        password = data.get('password', '') or 'demo123'
        
        uid = random.randint(1000, 9999)
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
        
        # Demo: always allow login with any credentials
        uid = random.randint(1000, 9999)
        name = email.split('@')[0].title() if email else 'Demo User'
        
        return jsonify({
            'message': 'Login successful',
            'user': {'id': uid, 'name': name, 'email': email or 'demo@euonia.app'},
            'access_token': create_token(uid),
            'refresh_token': create_token(uid, 720)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me')
@auth_required
def auth_me(uid):
    return jsonify({'id': int(uid), 'name': 'Demo User', 'email': 'demo@euonia.app'})

@app.route('/api/auth/refresh', methods=['POST'])
def refresh():
    uid = get_user_id() or random.randint(1000, 9999)
    return jsonify({'access_token': create_token(uid)})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out'})

# ========== USERS ==========
@app.route('/api/users/me', methods=['GET', 'PUT', 'OPTIONS'])
@auth_required
def users_me(uid):
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'id': int(uid), 'name': 'Demo User', 'email': 'demo@euonia.app',
        'completedSessions': 5, 'streak': 3, 'joinDate': '2024-01-01'
    })

@app.route('/api/users/me/preferences', methods=['GET', 'PUT'])
@auth_required
def preferences(uid):
    return jsonify({'theme': 'dark', 'notifications': True})

@app.route('/api/users/profile', methods=['GET', 'PUT'])
@auth_required
def profile(uid):
    return jsonify({
        'id': int(uid), 'name': 'Demo User', 'email': 'demo@euonia.app',
        'completedSessions': 5, 'streak': 3, 'joinDate': '2024-01-01'
    })

# ========== SESSIONS ==========
@app.route('/api/sessions', methods=['GET', 'POST', 'OPTIONS'])
@auth_required
def sessions(uid):
    if request.method == 'OPTIONS':
        return '', 200
    if request.method == 'POST':
        # Reset question tracker for new session
        question_tracker['current'] = 0
        question_tracker['answered'] = 0
        return jsonify({
            'id': random.randint(100, 999),
            'status': 'active',
            'messages': [],
            'title': f'Sesi {datetime.now().strftime("%d %b %Y")}',
            'created_at': datetime.utcnow().isoformat()
        }), 201
    # GET - return demo sessions
    return jsonify({'sessions': [
        {'id': 1, 'title': 'Sesi 8 Jan', 'status': 'completed', 'mood_score': 7, 'created_at': '2024-01-08T10:00:00Z'},
        {'id': 2, 'title': 'Sesi 7 Jan', 'status': 'completed', 'mood_score': 6, 'created_at': '2024-01-07T14:30:00Z'}
    ], 'total': 2, 'page': 1, 'per_page': 20})

@app.route('/api/sessions/recent', methods=['GET'])
@auth_required
def recent_sessions(uid):
    return jsonify([
        {'id': 1, 'title': 'Sesi 8 Jan', 'status': 'completed', 'mood_score': 7, 'primary_emotion': 'Tenang', 'created_at': '2024-01-08T10:00:00Z'},
        {'id': 2, 'title': 'Sesi 7 Jan', 'status': 'completed', 'mood_score': 6, 'primary_emotion': 'Netral', 'created_at': '2024-01-07T14:30:00Z'}
    ])

@app.route('/api/sessions/<int:sid>', methods=['GET', 'DELETE'])
@auth_required
def session_detail(uid, sid):
    if request.method == 'DELETE':
        return jsonify({'message': 'Deleted'})
    return jsonify({
        'id': sid, 'status': 'completed', 'messages': [],
        'summary': 'Sesi screening selesai dengan hasil positif.',
        'created_at': '2024-01-08T10:00:00Z', 'title': 'Sesi Demo'
    })

@app.route('/api/sessions/<int:sid>/messages', methods=['GET', 'POST'])
@auth_required
def messages(uid, sid):
    if request.method == 'POST':
        return jsonify({
            'id': random.randint(1, 100),
            'content': random.choice(EMPATHY_RESPONSES),
            'role': 'assistant',
            'session_id': sid
        }), 201
    return jsonify([])

@app.route('/api/sessions/<int:sid>/end', methods=['POST'])
@auth_required
def end_session(uid, sid):
    return jsonify({
        'id': sid, 'status': 'completed',
        'summary': 'Sesi telah selesai. Terima kasih sudah berbagi!',
        'recommendation': 'Tetap jaga kesehatan mentalmu dengan aktivitas yang menyenangkan.'
    })

@app.route('/api/sessions/<int:sid>/insights', methods=['GET'])
@auth_required
def session_insights(uid, sid):
    return jsonify({
        'session_id': sid, 'mood_score': 7,
        'emotions': [{'name': 'Tenang', 'percentage': 40}, {'name': 'Bahagia', 'percentage': 35}],
        'recommendations': ['Lanjutkan kebiasaan positif', 'Pertahankan pola tidur yang baik']
    })

# ========== SCREENING (Demo with rotating questions) ==========
@app.route('/api/screening/questions')
def questions_list():
    return jsonify(DEMO_QUESTIONS[:3])

@app.route('/api/screening/submit', methods=['POST'])
@auth_required
def submit_screening(uid):
    return jsonify({'score': 75, 'level': 'moderate', 'recommendations': []})

@app.route('/api/screening/sessions/<int:sid>/next-question', methods=['GET'])
@auth_required
def next_question(uid, sid):
    # Get current question index (rotate through questions)
    idx = question_tracker['answered'] % len(DEMO_QUESTIONS)
    question = DEMO_QUESTIONS[idx].copy()
    question['question_number'] = question_tracker['answered'] + 1
    question['total_questions'] = 25
    
    return jsonify({
        'status': 'ongoing',
        'progress': f'{question_tracker["answered"] + 1}/25',
        'question': question
    })

@app.route('/api/screening/sessions/<int:sid>/answer', methods=['POST'])
@auth_required
def submit_answer(uid, sid):
    # Increment answered count
    question_tracker['answered'] += 1
    
    # Check if session should complete (after 25 questions for demo, we'll use 5)
    if question_tracker['answered'] >= 25:
        return jsonify({
            'status': 'completed',
            'ai_empathy_reply': 'Sesi screening telah selesai! Terima kasih sudah berbagi perasaanmu. 🎉'
        })
    
    # Get next question
    idx = question_tracker['answered'] % len(DEMO_QUESTIONS)
    next_q = DEMO_QUESTIONS[idx].copy()
    next_q['question_number'] = question_tracker['answered'] + 1
    next_q['total_questions'] = 25
    
    return jsonify({
        'ai_empathy_reply': random.choice(EMPATHY_RESPONSES),
        'status': 'ongoing',
        'progress': f'{question_tracker["answered"] + 1}/25',
        'question': next_q
    })

@app.route('/api/screening/sessions/<int:sid>/summary', methods=['GET'])
@auth_required
def screening_summary(uid, sid):
    return jsonify({
        'session_id': sid,
        'total_score': 78,
        'phq9_score': 4,
        'gad7_score': 3,
        'wellness_score': 75,
        'summary': 'Kondisi mental kamu secara keseluruhan baik. Tetap jaga keseimbangan hidup!',
        'recommendation': 'Lanjutkan aktivitas positif dan jaga pola tidur yang teratur.',
        'primary_trigger': 'Tenang',
        'mood_improvement': 12
    })

@app.route('/api/screening/sessions/<int:sid>/end', methods=['POST'])
@auth_required
def end_screening(uid, sid):
    return jsonify({
        'session_id': sid,
        'status': 'completed',
        'summary': 'Sesi berhasil diakhiri. Kamu sudah melakukan refleksi yang baik!',
        'recommendation': 'Tetap jaga kesehatan mentalmu dengan aktivitas yang menyenangkan.'
    })

# ========== INSIGHTS ==========
@app.route('/api/insights/dashboard')
@auth_required
def dashboard(uid):
    return jsonify({
        'moodTrend': [65, 70, 68, 75, 72, 78, 80],
        'sessionsCompleted': 5,
        'currentStreak': 3,
        'averageMood': 7.2
    })

@app.route('/api/insights/mood-trend')
@auth_required
def mood_trend(uid):
    return jsonify({
        'trend': 'improving',
        'change_percentage': 12,
        'data_points': [
            {'date': '2024-01-03', 'score': 65},
            {'date': '2024-01-04', 'score': 70},
            {'date': '2024-01-05', 'score': 68},
            {'date': '2024-01-06', 'score': 75},
            {'date': '2024-01-07', 'score': 72},
            {'date': '2024-01-08', 'score': 78},
            {'date': '2024-01-09', 'score': 80}
        ]
    })

@app.route('/api/insights/emotions')
@auth_required
def emotions(uid):
    return jsonify({
        'emotions': [
            {'emotion': 'calm', 'percentage': 35, 'color': '#4ade80'},
            {'emotion': 'happy', 'percentage': 30, 'color': '#fbbf24'},
            {'emotion': 'neutral', 'percentage': 20, 'color': '#60a5fa'},
            {'emotion': 'anxious', 'percentage': 10, 'color': '#f87171'},
            {'emotion': 'sad', 'percentage': 5, 'color': '#a78bfa'}
        ],
        'period': 'weekly'
    })

@app.route('/api/insights/observations')
@auth_required
def observations(uid):
    return jsonify([
        {'id': 1, 'text': 'Mood kamu cenderung lebih baik di pagi hari. Coba manfaatkan waktu ini untuk aktivitas penting!', 'type': 'positive', 'read': False},
        {'id': 2, 'text': 'Pola tidurmu sudah membaik minggu ini. Pertahankan! 🌟', 'type': 'positive', 'read': True}
    ])

@app.route('/api/insights/observations/<int:oid>/read', methods=['POST'])
@auth_required
def mark_read(uid, oid):
    return jsonify({'success': True})

# ========== CATCH-ALL ==========
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def catch_all(path):
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'error': f'Endpoint /api/{path} not found', 'demo': True}), 404
