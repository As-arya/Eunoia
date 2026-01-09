"""
Vercel Serverless Function - Full Flask Backend with PostgreSQL
This enables full functionality like localhost with persistent database
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

# Create Flask app
app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuration
DATABASE_URL = os.environ.get('DATABASE_URL', '')
# Fix for Neon/Supabase postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'euonia-secret-key-2024')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'euonia-jwt-secret-2024')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL if DATABASE_URL else 'sqlite:///euonia_demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ============ Models ============
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    status = db.Column(db.String(20), default='active')
    mood_score = db.Column(db.Float, default=0)
    primary_emotion = db.Column(db.String(50))
    questions_answered = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'status': self.status,
            'mood_score': self.mood_score,
            'primary_emotion': self.primary_emotion,
            'questions_answered': self.questions_answered,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    question_id = db.Column(db.Integer)
    option_id = db.Column(db.Integer)
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

# ============ PHQ-9/GAD-7 Based Questions (26 questions) ============
DEMO_QUESTIONS = [
    {'id': 1, 'text': 'Hai! Aku senang bisa berbicara denganmu. Bagaimana perasaanmu saat ini?', 'category': 'Opening', 'options': [
        {'id': 1, 'text': 'Luar biasa baik! 😊', 'score': 5}, {'id': 2, 'text': 'Biasa saja', 'score': 3},
        {'id': 3, 'text': 'Kurang baik...', 'score': 2}, {'id': 4, 'text': 'Sangat tidak baik', 'score': 1}
    ]},
    {'id': 2, 'text': 'Dalam 2 minggu terakhir, seberapa sering kamu merasa minat atau kesenangan berkurang?', 'category': 'Depression', 'options': [
        {'id': 1, 'text': 'Tidak pernah', 'score': 5}, {'id': 2, 'text': 'Beberapa hari', 'score': 4},
        {'id': 3, 'text': 'Lebih dari setengah waktu', 'score': 2}, {'id': 4, 'text': 'Hampir setiap hari', 'score': 1}
    ]},
    {'id': 3, 'text': 'Seberapa sering kamu merasa down, sedih, atau putus asa?', 'category': 'Depression', 'options': [
        {'id': 1, 'text': 'Tidak pernah', 'score': 5}, {'id': 2, 'text': 'Beberapa hari', 'score': 4},
        {'id': 3, 'text': 'Lebih dari setengah waktu', 'score': 2}, {'id': 4, 'text': 'Hampir setiap hari', 'score': 1}
    ]},
    {'id': 4, 'text': 'Bagaimana dengan tidurmu? Apakah kamu kesulitan tidur atau justru tidur terlalu banyak?', 'category': 'Sleep', 'options': [
        {'id': 1, 'text': 'Tidur normal', 'score': 5}, {'id': 2, 'text': 'Kadang susah tidur', 'score': 4},
        {'id': 3, 'text': 'Sering bermasalah', 'score': 2}, {'id': 4, 'text': 'Hampir selalu bermasalah', 'score': 1}
    ]},
    {'id': 5, 'text': 'Seberapa sering kamu merasa lelah atau kehilangan energi?', 'category': 'Energy', 'options': [
        {'id': 1, 'text': 'Energi baik', 'score': 5}, {'id': 2, 'text': 'Kadang lelah', 'score': 4},
        {'id': 3, 'text': 'Sering lelah', 'score': 2}, {'id': 4, 'text': 'Selalu lelah', 'score': 1}
    ]},
    {'id': 6, 'text': 'Apakah kamu pernah merasa buruk tentang dirimu sendiri?', 'category': 'Self', 'options': [
        {'id': 1, 'text': 'Tidak', 'score': 5}, {'id': 2, 'text': 'Kadang-kadang', 'score': 4},
        {'id': 3, 'text': 'Sering', 'score': 2}, {'id': 4, 'text': 'Hampir selalu', 'score': 1}
    ]},
    {'id': 7, 'text': 'Apakah kamu kesulitan berkonsentrasi pada hal-hal seperti membaca atau bekerja?', 'category': 'Focus', 'options': [
        {'id': 1, 'text': 'Tidak ada masalah', 'score': 5}, {'id': 2, 'text': 'Kadang sulit', 'score': 4},
        {'id': 3, 'text': 'Sering sulit', 'score': 2}, {'id': 4, 'text': 'Hampir tidak bisa konsentrasi', 'score': 1}
    ]},
    {'id': 8, 'text': 'Seberapa sering kamu merasa nervous, cemas, atau was-was?', 'category': 'Anxiety', 'options': [
        {'id': 1, 'text': 'Tidak pernah', 'score': 5}, {'id': 2, 'text': 'Beberapa hari', 'score': 4},
        {'id': 3, 'text': 'Lebih dari setengah waktu', 'score': 2}, {'id': 4, 'text': 'Hampir setiap hari', 'score': 1}
    ]},
    {'id': 9, 'text': 'Apakah kamu tidak bisa menghentikan atau mengontrol kekhawatiranmu?', 'category': 'Anxiety', 'options': [
        {'id': 1, 'text': 'Tidak', 'score': 5}, {'id': 2, 'text': 'Kadang', 'score': 4},
        {'id': 3, 'text': 'Sering', 'score': 2}, {'id': 4, 'text': 'Hampir selalu', 'score': 1}
    ]},
    {'id': 10, 'text': 'Seberapa sulit bagimu untuk rileks?', 'category': 'Anxiety', 'options': [
        {'id': 1, 'text': 'Mudah rileks', 'score': 5}, {'id': 2, 'text': 'Agak sulit', 'score': 4},
        {'id': 3, 'text': 'Sulit', 'score': 2}, {'id': 4, 'text': 'Sangat sulit/tidak bisa', 'score': 1}
    ]},
    {'id': 11, 'text': 'Apakah kamu mudah merasa kesal atau irritable?', 'category': 'Anxiety', 'options': [
        {'id': 1, 'text': 'Tidak', 'score': 5}, {'id': 2, 'text': 'Kadang', 'score': 4},
        {'id': 3, 'text': 'Sering', 'score': 2}, {'id': 4, 'text': 'Hampir selalu', 'score': 1}
    ]},
    {'id': 12, 'text': 'Ketika menghadapi tekanan, bagaimana biasanya kamu mengatasinya?', 'category': 'Stress', 'options': [
        {'id': 1, 'text': 'Bisa mengelola dengan baik', 'score': 5}, {'id': 2, 'text': 'Berusaha mencari cara', 'score': 4},
        {'id': 3, 'text': 'Sering merasa kewalahan', 'score': 2}, {'id': 4, 'text': 'Sangat sulit mengatasinya', 'score': 1}
    ]},
    {'id': 13, 'text': 'Apakah kamu merasa memiliki seseorang yang bisa kamu ajak bicara?', 'category': 'Social', 'options': [
        {'id': 1, 'text': 'Ya, banyak', 'score': 5}, {'id': 2, 'text': 'Ya, ada beberapa', 'score': 4},
        {'id': 3, 'text': 'Hanya satu atau dua orang', 'score': 2}, {'id': 4, 'text': 'Tidak ada', 'score': 1}
    ]},
    {'id': 14, 'text': 'Seberapa sulit masalah-masalah ini membuatmu menjalankan pekerjaan atau bergaul?', 'category': 'Functional', 'options': [
        {'id': 1, 'text': 'Tidak sulit sama sekali', 'score': 5}, {'id': 2, 'text': 'Agak sulit', 'score': 4},
        {'id': 3, 'text': 'Sangat sulit', 'score': 2}, {'id': 4, 'text': 'Extremely sulit', 'score': 1}
    ]},
    {'id': 15, 'text': 'Apakah nafsu makanmu berubah akhir-akhir ini?', 'category': 'Depression', 'options': [
        {'id': 1, 'text': 'Normal', 'score': 5}, {'id': 2, 'text': 'Sedikit berubah', 'score': 4},
        {'id': 3, 'text': 'Cukup berubah', 'score': 2}, {'id': 4, 'text': 'Sangat berubah', 'score': 1}
    ]},
    {'id': 16, 'text': 'Apakah kamu merasa sulit mengambil keputusan atau berpikir jernih?', 'category': 'Depression', 'options': [
        {'id': 1, 'text': 'Tidak', 'score': 5}, {'id': 2, 'text': 'Kadang', 'score': 4},
        {'id': 3, 'text': 'Sering', 'score': 2}, {'id': 4, 'text': 'Hampir selalu', 'score': 1}
    ]},
    {'id': 17, 'text': 'Apakah kamu merasa gerakan atau bicaramu melambat, atau sebaliknya lebih gelisah?', 'category': 'Energy', 'options': [
        {'id': 1, 'text': 'Normal', 'score': 5}, {'id': 2, 'text': 'Sedikit', 'score': 4},
        {'id': 3, 'text': 'Cukup terasa', 'score': 2}, {'id': 4, 'text': 'Sangat terasa', 'score': 1}
    ]},
    {'id': 18, 'text': 'Apakah kamu sering terbangun di tengah malam dan sulit tidur kembali?', 'category': 'Sleep', 'options': [
        {'id': 1, 'text': 'Tidak pernah', 'score': 5}, {'id': 2, 'text': 'Jarang', 'score': 4},
        {'id': 3, 'text': 'Sering', 'score': 2}, {'id': 4, 'text': 'Hampir setiap malam', 'score': 1}
    ]},
    {'id': 19, 'text': 'Apakah kamu sering merasa seolah akan terjadi sesuatu yang buruk?', 'category': 'Anxiety', 'options': [
        {'id': 1, 'text': 'Tidak', 'score': 5}, {'id': 2, 'text': 'Kadang', 'score': 4},
        {'id': 3, 'text': 'Sering', 'score': 2}, {'id': 4, 'text': 'Hampir selalu', 'score': 1}
    ]},
    {'id': 20, 'text': 'Apakah kamu mengalami gejala fisik seperti jantung berdebar atau gemetar saat cemas?', 'category': 'Anxiety', 'options': [
        {'id': 1, 'text': 'Tidak', 'score': 5}, {'id': 2, 'text': 'Kadang', 'score': 4},
        {'id': 3, 'text': 'Sering', 'score': 2}, {'id': 4, 'text': 'Hampir selalu', 'score': 1}
    ]},
    {'id': 21, 'text': 'Apakah kamu merasa waktu tidak pernah cukup untuk tugasmu?', 'category': 'Stress', 'options': [
        {'id': 1, 'text': 'Tidak', 'score': 5}, {'id': 2, 'text': 'Kadang', 'score': 4},
        {'id': 3, 'text': 'Sering', 'score': 2}, {'id': 4, 'text': 'Hampir selalu', 'score': 1}
    ]},
    {'id': 22, 'text': 'Bagaimana hubunganmu dengan orang-orang terdekat akhir-akhir ini?', 'category': 'Stress', 'options': [
        {'id': 1, 'text': 'Baik', 'score': 5}, {'id': 2, 'text': 'Agak tegang', 'score': 4},
        {'id': 3, 'text': 'Cukup bermasalah', 'score': 2}, {'id': 4, 'text': 'Sangat bermasalah', 'score': 1}
    ]},
    {'id': 23, 'text': 'Apakah kamu merasa kesepian meskipun dikelilingi orang?', 'category': 'Social', 'options': [
        {'id': 1, 'text': 'Tidak', 'score': 5}, {'id': 2, 'text': 'Kadang', 'score': 4},
        {'id': 3, 'text': 'Sering', 'score': 2}, {'id': 4, 'text': 'Hampir selalu', 'score': 1}
    ]},
    {'id': 24, 'text': 'Seberapa sering kamu menghindari aktivitas sosial karena perasaanmu?', 'category': 'Social', 'options': [
        {'id': 1, 'text': 'Tidak pernah', 'score': 5}, {'id': 2, 'text': 'Kadang', 'score': 4},
        {'id': 3, 'text': 'Sering', 'score': 2}, {'id': 4, 'text': 'Hampir selalu', 'score': 1}
    ]},
    {'id': 25, 'text': 'Apakah kamu memiliki aktivitas yang membuatmu merasa tenang dan bahagia?', 'category': 'Self', 'options': [
        {'id': 1, 'text': 'Ya, banyak', 'score': 5}, {'id': 2, 'text': 'Ya, beberapa', 'score': 4},
        {'id': 3, 'text': 'Sedikit', 'score': 2}, {'id': 4, 'text': 'Tidak ada', 'score': 1}
    ]},
    {'id': 26, 'text': 'Terakhir, apakah kamu tertarik untuk berbicara dengan profesional kesehatan mental?', 'category': 'Closing', 'options': [
        {'id': 1, 'text': 'Ya, saya ingin', 'score': 5}, {'id': 2, 'text': 'Mungkin, masih ragu', 'score': 4},
        {'id': 3, 'text': 'Belum siap', 'score': 2}, {'id': 4, 'text': 'Tidak perlu', 'score': 1}
    ]},
]

EMPATHY_RESPONSES = [
    "Terima kasih sudah berbagi. Perasaanmu valid dan aku menghargai keterbukaanmu. 💙",
    "Aku mendengarmu. Penting untuk mengakui perasaan kita, apapun itu. 🌟",
    "Terima kasih sudah jujur. Setiap perasaan adalah bagian dari perjalananmu. 💫",
    "Aku senang kamu mau berbagi. Kamu tidak sendirian dalam perjalanan ini. 🤗",
    "Perasaanmu penting. Terima kasih sudah mempercayakannya padaku. 💚",
    "Aku menghargai kejujuranmu. Mari kita lanjutkan eksplorasi bersama. ✨",
    "Setiap langkah kecil menuju kesadaran diri adalah kemajuan. Kamu hebat! 🌈",
    "Terima kasih sudah terbuka. Refleksi diri adalah tanda kekuatan. 💪",
]

SESSION_LENGTH = 25  # 25 questions per session
EMOTIONS = ['calm', 'happy', 'neutral', 'anxious', 'sad', 'stressed', 'hopeful']

# ============ CORS ============
@app.after_request
def cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# ============ Health ============
@app.route('/api/health')
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({'status': 'ok', 'database': 'connected'})
    except:
        return jsonify({'status': 'ok', 'database': 'demo_mode'})

# ============ Auth ============
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
            return jsonify({'error': 'Semua field harus diisi'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email sudah terdaftar'}), 409
        
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Registrasi berhasil',
            'user': user.to_dict(),
            'access_token': create_access_token(identity=str(user.id)),
            'refresh_token': create_refresh_token(identity=str(user.id))
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json() or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Email atau password salah'}), 401
        
        return jsonify({
            'message': 'Login berhasil',
            'user': user.to_dict(),
            'access_token': create_access_token(identity=str(user.id)),
            'refresh_token': create_refresh_token(identity=str(user.id))
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me')
@jwt_required()
def auth_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User tidak ditemukan'}), 404
    return jsonify(user.to_dict())

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    return jsonify({'access_token': create_access_token(identity=identity)})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out'})

# ============ Users ============
@app.route('/api/users/me', methods=['GET', 'PUT', 'OPTIONS'])
@jwt_required()
def users_me():
    if request.method == 'OPTIONS':
        return '', 200
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User tidak ditemukan'}), 404
    
    session_count = Session.query.filter_by(user_id=user_id, status='completed').count()
    return jsonify({
        **user.to_dict(),
        'completedSessions': session_count,
        'streak': min(session_count, 7),
        'joinDate': user.created_at.strftime('%Y-%m-%d') if user.created_at else '2024-01-01'
    })

@app.route('/api/users/me/preferences', methods=['GET', 'PUT'])
@jwt_required()
def preferences():
    return jsonify({'theme': 'dark', 'notifications': True})

@app.route('/api/users/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    return users_me()

# ============ Sessions ============
@app.route('/api/sessions', methods=['GET', 'POST', 'OPTIONS'])
@jwt_required()
def sessions():
    if request.method == 'OPTIONS':
        return '', 200
    user_id = int(get_jwt_identity())
    
    if request.method == 'POST':
        session = Session(
            user_id=user_id,
            title=f"Sesi {datetime.now().strftime('%d %b %Y')}",
            status='active'
        )
        db.session.add(session)
        db.session.commit()
        return jsonify(session.to_dict()), 201
    
    # GET
    sessions_list = Session.query.filter_by(user_id=user_id).order_by(Session.created_at.desc()).limit(20).all()
    return jsonify({
        'sessions': [s.to_dict() for s in sessions_list],
        'total': len(sessions_list)
    })

@app.route('/api/sessions/recent')
@jwt_required()
def recent_sessions():
    user_id = int(get_jwt_identity())
    sessions_list = Session.query.filter_by(user_id=user_id).order_by(Session.created_at.desc()).limit(5).all()
    return jsonify([s.to_dict() for s in sessions_list])

@app.route('/api/sessions/<int:sid>', methods=['GET', 'DELETE'])
@jwt_required()
def session_detail(sid):
    session = Session.query.get_or_404(sid)
    if request.method == 'DELETE':
        db.session.delete(session)
        db.session.commit()
        return jsonify({'message': 'Deleted'})
    return jsonify(session.to_dict())

@app.route('/api/sessions/<int:sid>/messages', methods=['GET', 'POST'])
@jwt_required()
def messages(sid):
    if request.method == 'POST':
        return jsonify({
            'id': random.randint(1, 1000),
            'content': random.choice(EMPATHY_RESPONSES),
            'role': 'assistant',
            'session_id': sid
        }), 201
    return jsonify([])

@app.route('/api/sessions/<int:sid>/end', methods=['POST'])
@jwt_required()
def end_session(sid):
    session = Session.query.get_or_404(sid)
    session.status = 'completed'
    session.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify(session.to_dict())

@app.route('/api/sessions/<int:sid>/insights')
@jwt_required()
def session_insights(sid):
    session = Session.query.get_or_404(sid)
    return jsonify({
        'session_id': sid,
        'status': session.status,
        'mood_score': session.mood_score or 7.5,
        'overall_mood': 'Neutral',
        'emotional_journey': {'start': 'Calm', 'end': 'Neutral', 'trend': 'stable'},
        'primary_emotion': session.primary_emotion or 'calm',
        'emotions': [
            {'emotion': 'calm', 'percentage': 40},
            {'emotion': 'happy', 'percentage': 30},
            {'emotion': 'neutral', 'percentage': 20},
            {'emotion': 'anxious', 'percentage': 10}
        ],
        'key_insights': [
            {'icon': '🌙', 'title': 'Pola Tidur', 'description': 'Kualitas tidurmu cukup baik.'},
            {'icon': '💪', 'title': 'Energi', 'description': 'Level energimu stabil.'},
        ],
        'summary': 'Kondisi mental secara keseluruhan baik.',
        'recommendation': 'Lanjutkan aktivitas positif.',
        'questions_answered': session.questions_answered or SESSION_LENGTH
    })

# ============ Screening ============
@app.route('/api/screening/questions')
def questions():
    return jsonify(DEMO_QUESTIONS[:3])

@app.route('/api/screening/sessions/<int:sid>/next-question')
@jwt_required()
def next_question(sid):
    session = Session.query.get_or_404(sid)
    idx = session.questions_answered % len(DEMO_QUESTIONS)
    question = DEMO_QUESTIONS[idx].copy()
    question['question_number'] = session.questions_answered + 1
    question['total_questions'] = SESSION_LENGTH
    
    return jsonify({
        'status': 'ongoing' if session.questions_answered < SESSION_LENGTH else 'completed',
        'progress': f'{session.questions_answered + 1}/{SESSION_LENGTH}',
        'question': question
    })

@app.route('/api/screening/sessions/<int:sid>/answer', methods=['POST'])
@jwt_required()
def submit_answer(sid):
    session = Session.query.get_or_404(sid)
    data = request.get_json() or {}
    
    # Save answer
    answer = Answer(
        session_id=sid,
        question_id=data.get('question_id'),
        option_id=data.get('option_id'),
        score=data.get('score', 3)
    )
    db.session.add(answer)
    
    # Update session
    session.questions_answered += 1
    answers = Answer.query.filter_by(session_id=sid).all()
    if answers:
        avg_score = sum(a.score or 3 for a in answers) / len(answers)
        session.mood_score = avg_score * 2  # Scale to 10
        session.primary_emotion = random.choice(EMOTIONS)
    
    # Check completion
    if session.questions_answered >= SESSION_LENGTH:
        session.status = 'completed'
        session.completed_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            'status': 'completed',
            'ai_empathy_reply': 'Sesi selesai! Terima kasih sudah berbagi. 🎉'
        })
    
    db.session.commit()
    
    # Get next question
    idx = session.questions_answered % len(DEMO_QUESTIONS)
    next_q = DEMO_QUESTIONS[idx].copy()
    next_q['question_number'] = session.questions_answered + 1
    next_q['total_questions'] = SESSION_LENGTH
    
    return jsonify({
        'ai_empathy_reply': random.choice(EMPATHY_RESPONSES),
        'status': 'ongoing',
        'progress': f'{session.questions_answered + 1}/{SESSION_LENGTH}',
        'question': next_q
    })

@app.route('/api/screening/sessions/<int:sid>/summary')
@jwt_required()
def screening_summary(sid):
    session = Session.query.get_or_404(sid)
    return jsonify({
        'session_id': sid,
        'total_score': int(session.mood_score * 10) if session.mood_score else 75,
        'wellness_score': int(session.mood_score * 10) if session.mood_score else 75,
        'summary': 'Kondisi mental baik. Tetap jaga keseimbangan!',
        'recommendation': 'Lanjutkan aktivitas positif.',
        'primary_trigger': session.primary_emotion or 'calm',
        'mood_improvement': random.randint(5, 15)
    })

@app.route('/api/screening/sessions/<int:sid>/end', methods=['POST'])
@jwt_required()
def end_screening(sid):
    session = Session.query.get_or_404(sid)
    session.status = 'completed'
    session.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({
        'session_id': sid,
        'status': 'completed',
        'summary': 'Sesi berhasil diakhiri.',
        'recommendation': 'Tetap jaga kesehatan mentalmu.'
    })

# ============ Insights ============
@app.route('/api/insights/dashboard')
@jwt_required()
def dashboard():
    user_id = int(get_jwt_identity())
    sessions = Session.query.filter_by(user_id=user_id, status='completed').order_by(Session.created_at.desc()).limit(7).all()
    mood_trend = [s.mood_score * 10 if s.mood_score else 70 for s in reversed(sessions)] or [70]
    return jsonify({
        'moodTrend': mood_trend,
        'sessionsCompleted': len(sessions),
        'currentStreak': min(len(sessions), 7),
        'averageMood': sum(mood_trend) / len(mood_trend) if mood_trend else 7
    })

@app.route('/api/insights/mood-trend')
@jwt_required()
def mood_trend():
    user_id = int(get_jwt_identity())
    sessions = Session.query.filter_by(user_id=user_id, status='completed').order_by(Session.created_at.desc()).limit(7).all()
    data_points = [{'date': s.created_at.strftime('%Y-%m-%d'), 'score': int(s.mood_score * 10) if s.mood_score else 70} for s in reversed(sessions)]
    return jsonify({
        'trend': 'improving' if len(data_points) > 1 else 'neutral',
        'change_percentage': random.randint(5, 15),
        'data_points': data_points or [{'date': datetime.now().strftime('%Y-%m-%d'), 'score': 70}]
    })

@app.route('/api/insights/emotions')
@jwt_required()
def emotions():
    return jsonify({
        'emotions': [
            {'emotion': 'calm', 'percentage': 35},
            {'emotion': 'happy', 'percentage': 30},
            {'emotion': 'neutral', 'percentage': 20},
            {'emotion': 'anxious', 'percentage': 10},
            {'emotion': 'sad', 'percentage': 5}
        ],
        'period': 'weekly'
    })

@app.route('/api/insights/observations')
@jwt_required()
def observations():
    return jsonify([
        {'id': 1, 'text': 'Mood kamu cenderung lebih baik di pagi hari.', 'type': 'positive', 'read': False},
        {'id': 2, 'text': 'Pola tidurmu sudah membaik. 🌟', 'type': 'positive', 'read': True}
    ])

@app.route('/api/insights/observations/<int:oid>/read', methods=['POST'])
@jwt_required()
def mark_read(oid):
    return jsonify({'success': True})

# ============ Catch-all ============
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def catch_all(path):
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'error': f'Endpoint /api/{path} tidak ditemukan'}), 404

# JWT Error Handlers
@jwt.invalid_token_loader
def invalid_token(error):
    return jsonify({'error': 'Token tidak valid'}), 401

@jwt.unauthorized_loader
def unauthorized(error):
    return jsonify({'error': 'Token diperlukan'}), 401

@jwt.expired_token_loader
def expired_token(header, payload):
    return jsonify({'error': 'Token kadaluarsa'}), 401
