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
        # Determine mood based on mood_score
        score = self.mood_score or 5
        if score >= 8:
            mood = 'happy'
        elif score >= 6:
            mood = 'calm'
        elif score >= 4:
            mood = 'neutral'
        elif score >= 2:
            mood = 'anxious'
        else:
            mood = 'sad'
        
        return {
            'id': self.id,
            'title': self.title or f'Sesi {self.created_at.strftime("%d %b %Y") if self.created_at else ""}',
            'status': self.status,
            'mood': mood,
            'mood_score': self.mood_score,
            'primary_emotion': self.primary_emotion or mood,
            'questions_answered': self.questions_answered,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'summary': 'Chat conversation'
        }

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    question_id = db.Column(db.Integer)
    option_id = db.Column(db.Integer)
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SessionInsight(db.Model):
    __tablename__ = 'session_insights'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    summary = db.Column(db.Text)
    score = db.Column(db.Integer, default=0)
    recommendation = db.Column(db.Text)
    primary_trigger = db.Column(db.String(100))
    breakthrough = db.Column(db.Text)
    mood_improvement = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'summary': self.summary,
            'score': self.score,
            'recommendation': self.recommendation,
            'primary_trigger': self.primary_trigger,
            'breakthrough': self.breakthrough,
            'mood_improvement': self.mood_improvement
        }

# ============ Gemini AI Integration ============
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_ENABLED = True
    else:
        GEMINI_ENABLED = False
except ImportError:
    GEMINI_ENABLED = False

def generate_ai_summary(answers_data, total_score, primary_emotion):
    """Generate detailed AI summary using Gemini"""
    if not GEMINI_ENABLED:
        return generate_fallback_summary(total_score, primary_emotion)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Determine severity
        num_answers = len(answers_data)
        max_score = num_answers * 3
        if total_score <= max_score * 0.25:
            severity = "minimal"
        elif total_score <= max_score * 0.5:
            severity = "mild"
        elif total_score <= max_score * 0.75:
            severity = "moderate"
        else:
            severity = "moderately_severe"
        
        qa_text = "\n".join([f"Q: {a.get('q', '')}\nA: {a.get('a', '')}" for a in answers_data])
        
        prompt = f"""Kamu adalah Eunoia, AI companion empatik untuk kesehatan mental Indonesia.

Berdasarkan screening dengan severity: {severity}
Emosi dominan: {primary_emotion}
Total pertanyaan: {num_answers}

RESPONS USER:
{qa_text}

Buat RINGKASAN KOMPREHENSIF (5-7 kalimat):

1. OBSERVASI UTAMA: Kondisi emosional keseluruhan
2. ANALISIS POLA: Identifikasi pola dari jawaban
3. KEKUATAN: Hal positif yang terlihat
4. AREA PERHATIAN: Area yang perlu perhatian
5. PESAN SUPORTIF: Validasi dan harapan

Gunakan bahasa Indonesia yang hangat, personal ("kamu" bukan "Anda"). Maksimal 1 emoji di akhir (💙 atau 🌟)."""

        result = model.generate_content(prompt)
        return result.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return generate_fallback_summary(total_score, primary_emotion)

def generate_fallback_summary(total_score, primary_emotion):
    """Fallback summary when Gemini is not available"""
    if total_score <= 10:
        return f"""Berdasarkan sesi ini, kondisi emosionalmu menunjukkan kesejahteraan yang baik. 
Kamu memiliki kemampuan coping yang efektif dan stabilitas emosional yang solid. 
Ini adalah fondasi yang kuat untuk kesehatan mental jangka panjang. 
Tetap jaga kebiasaan positif yang sudah kamu bangun! 🌟"""
    elif total_score <= 20:
        return f"""Dari analisis sesi ini, ada beberapa area yang mungkin perlu perhatian ekstra. 
Secara umum kamu menunjukkan kemampuan mengelola emosi dengan baik, namun ada momen-momen tekanan. 
Ini normal dan menunjukkan kesadaran diri yang baik. 
Fokus pada self-care dan jangan ragu untuk mencari dukungan saat diperlukan. 💙"""
    elif total_score <= 35:
        return f"""Berdasarkan responsmu, aku melihat beberapa tantangan signifikan yang sedang kamu hadapi. 
Pola responsmu menunjukkan beban emosional yang mempengaruhi beberapa aspek kehidupanmu.
Mengenali ini adalah kekuatan. Pertimbangkan untuk berbicara dengan profesional kesehatan mental 
yang dapat memberikan dukungan lebih terarah. 💙"""
    else:
        return f"""Dari sesi ini, kondisimu menunjukkan beban emosional yang cukup berat.
Responsmu mengindikasikan dampak konsisten pada berbagai area kehidupan.
Mencari bantuan profesional adalah langkah berani menuju pemulihan.
Sangat disarankan untuk segera konsultasi dengan psikolog atau psikiater.
Hubungi Hotline Kesehatan Jiwa 119 ext 8 (24 jam). 💙"""

def get_recommendation(score, emotion):
    """Get evidence-based recommendation"""
    if score <= 10:
        return "Pertahankan rutinitas positifmu! Olahraga teratur dan tidur cukup adalah kunci kesehatan mental."
    elif score <= 20:
        recs = {
            'anxious': "Coba latihan pernapasan 4-7-8: tarik napas 4 detik, tahan 7 detik, buang 8 detik.",
            'sad': "Habiskan 10-15 menit di luar rumah hari ini. Cahaya matahari membantu memperbaiki mood.",
            'stressed': "Prioritaskan satu tugas kecil yang bisa kamu selesaikan hari ini.",
            'tired': "Tetapkan jadwal tidur konsisten. Hindari layar 1 jam sebelum tidur."
        }
        return recs.get(emotion.lower(), "Luangkan 15 menit untuk aktivitas yang membuatmu tenang hari ini.")
    elif score <= 35:
        return "Pertimbangkan berbicara dengan psikolog. Hubungi Hotline Kesehatan Jiwa 119 ext 8."
    else:
        return "Sangat disarankan segera konsultasi dengan profesional. Hubungi 119 ext 8 (24 jam) atau Yayasan Pulih +62 811-1711-555."

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
    answers = Answer.query.filter_by(session_id=sid).order_by(Answer.created_at).all()
    
    # Build answers data for AI summary
    answers_data = []
    emotion_counts = {}
    for i, a in enumerate(answers):
        q = DEMO_QUESTIONS[a.question_id - 1] if a.question_id and a.question_id <= len(DEMO_QUESTIONS) else None
        if q:
            opt = next((o for o in q.get('options', []) if o.get('id') == a.option_id), None)
            answers_data.append({
                'q': q.get('text', ''),
                'a': opt.get('text', '') if opt else '',
                'score': a.score
            })
            # Track emotions based on score
            emotion = 'sad' if (a.score or 3) <= 2 else 'happy' if (a.score or 3) >= 4 else 'neutral'
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Calculate scores
    if answers:
        total_score = sum(a.score or 3 for a in answers)
        avg_score = total_score / len(answers)
        max_possible = len(answers) * 5
        wellness_percentage = int((total_score / max_possible) * 100)
        mood_score = avg_score * 2
    else:
        total_score = 0
        avg_score = 3
        wellness_percentage = 60
        mood_score = 6
    
    # Determine primary emotion
    primary_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'neutral'
    
    # Calculate emotional journey data points (for graph)
    journey_points = []
    running_score = 0
    for i, a in enumerate(answers):
        running_score = ((running_score * i) + (a.score or 3)) / (i + 1)
        journey_points.append(round(running_score, 2))
    
    # Determine mood level
    if avg_score >= 4:
        overall_mood = 'Positive'
        trend = 'improving'
        mood_improvement = random.randint(15, 30)
        breakthrough = "Kamu menunjukkan kekuatan yang luar biasa dalam menjaga kesehatan mentalmu!"
    elif avg_score >= 3:
        overall_mood = 'Neutral'
        trend = 'stable'
        mood_improvement = random.randint(-5, 10)
        breakthrough = "Kesadaran diri adalah langkah penting dalam perjalanan kesehatan mental."
    elif avg_score >= 2:
        overall_mood = 'Concerning'
        trend = 'declining'
        mood_improvement = random.randint(-15, 0)
        breakthrough = "Berbagi perasaanmu adalah langkah berani menuju penyembuhan."
    else:
        overall_mood = 'Needs Support'
        trend = 'needs_attention'
        mood_improvement = random.randint(-30, -10)
        breakthrough = "Mencari bantuan adalah tanda kekuatan, bukan kelemahan."
    
    # Generate AI summary (uses Gemini if available)
    ai_summary = generate_ai_summary(answers_data, total_score, primary_emotion)
    ai_recommendation = get_recommendation(total_score, primary_emotion)
    
    # Build emotions distribution from actual data
    total_emotions = sum(emotion_counts.values()) or 1
    emotions = [{'emotion': e, 'percentage': round((c / total_emotions) * 100)} 
                for e, c in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)][:5]
    if not emotions:
        emotions = [{'emotion': 'neutral', 'percentage': 100}]
    
    # Build key insights based on analysis
    key_insights = []
    if primary_emotion in ['happy', 'calm', 'positive']:
        key_insights.append({'icon': '🌟', 'title': 'Mood Positif', 'description': 'Kamu memiliki pandangan yang positif dan stabil!'})
    if emotion_counts.get('anxious', 0) > len(answers) * 0.3:
        key_insights.append({'icon': '😰', 'title': 'Kecemasan Terdeteksi', 'description': 'Ada tanda-tanda kecemasan yang perlu diperhatikan.'})
    if emotion_counts.get('sad', 0) > len(answers) * 0.3:
        key_insights.append({'icon': '😢', 'title': 'Kesedihan Mendalam', 'description': 'Perasaan sedih terdeteksi cukup signifikan.'})
    if emotion_counts.get('tired', 0) > len(answers) * 0.2:
        key_insights.append({'icon': '😴', 'title': 'Kelelahan', 'description': 'Pastikan kamu mendapat istirahat yang cukup.'})
    # Default insights if none detected
    if not key_insights:
        key_insights = [
            {'icon': '💭', 'title': 'Refleksi Diri', 'description': 'Luangkan waktu untuk refleksi dan self-care.'},
            {'icon': '🌱', 'title': 'Pertumbuhan', 'description': 'Setiap langkah kecil adalah kemajuan.'}
        ]
    
    return jsonify({
        'session_id': sid,
        'status': session.status,
        'mood_score': round(mood_score, 1),
        'overall_mood': overall_mood,
        'emotional_journey': {
            'start': 'Calm' if journey_points and journey_points[0] >= 3 else 'Low',
            'end': overall_mood,
            'trend': trend,
            'data_points': journey_points  # For graph rendering
        },
        'primary_emotion': primary_emotion,
        'primary_trigger': primary_emotion,  # For compatibility
        'emotions': emotions,
        'key_insights': key_insights,
        'wellness_score': wellness_percentage,
        'phq9_score': max(0, 27 - int(avg_score * 6.75)),
        'gad7_score': max(0, 21 - int(avg_score * 5.25)),
        'score': total_score,
        'summary': ai_summary,
        'recommendation': ai_recommendation,
        'breakthrough': breakthrough,
        'mood_improvement': mood_improvement,
        'questions_answered': session.questions_answered or len(answers),
        'created_at': session.created_at.isoformat() if session.created_at else None,
        '_debug': {
            'total_answers': len(answers),
            'total_score': total_score,
            'avg_score': round(avg_score, 2),
            'gemini_enabled': GEMINI_ENABLED,
            'emotion_counts': emotion_counts
        }
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
    try:
        session = Session.query.get_or_404(sid)
        data = request.get_json() or {}
        
        # Save answer (without emotion_tag to avoid migration issues)
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
    
    data_points = []
    for s in reversed(sessions):
        score = int((s.mood_score or 5) * 10)  # Default to 50 if None
        score = max(10, min(100, score))  # Clamp between 10-100
        data_points.append({
            'date': s.created_at.strftime('%Y-%m-%d') if s.created_at else datetime.now().strftime('%Y-%m-%d'),
            'score': score,
            'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][s.created_at.weekday()] if s.created_at else 'Today'
        })
    
    # Always return at least 7 days of data for the chart
    if len(data_points) < 7:
        for i in range(7 - len(data_points)):
            d = datetime.now() - timedelta(days=6-i-len(data_points))
            data_points.insert(0, {
                'date': d.strftime('%Y-%m-%d'),
                'score': 60,  # Default neutral score
                'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][d.weekday()]
            })
    
    return jsonify({
        'trend': 'improving' if len(sessions) > 1 else 'stable',
        'change_percentage': random.randint(5, 15) if sessions else 0,
        'data': data_points,
        'data_points': data_points,  # For compatibility
        'period': 'weekly'
    })

@app.route('/api/insights/emotions')
@jwt_required()
def emotions():
    user_id = int(get_jwt_identity())
    sessions = Session.query.filter_by(user_id=user_id, status='completed').order_by(Session.created_at.desc()).limit(10).all()
    
    # Calculate emotion distribution from actual answers
    emotion_counts = {'happy': 0, 'calm': 0, 'neutral': 0, 'sad': 0, 'anxious': 0}
    total = 0
    
    for s in sessions:
        answers = Answer.query.filter_by(session_id=s.id).all()
        for a in answers:
            total += 1
            score = a.score or 3
            if score >= 4:
                emotion_counts['happy'] += 1
            elif score >= 3:
                if random.random() > 0.5:
                    emotion_counts['calm'] += 1
                else:
                    emotion_counts['neutral'] += 1
            elif score >= 2:
                emotion_counts['anxious'] += 1
            else:
                emotion_counts['sad'] += 1
    
    # Calculate percentages
    if total > 0:
        emotions_list = [{'emotion': e, 'percentage': round((c / total) * 100)} 
                        for e, c in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)]
    else:
        # Default if no data
        emotions_list = [
            {'emotion': 'calm', 'percentage': 35},
            {'emotion': 'happy', 'percentage': 30},
            {'emotion': 'neutral', 'percentage': 20},
            {'emotion': 'anxious', 'percentage': 10},
            {'emotion': 'sad', 'percentage': 5}
        ]
    
    return jsonify({
        'emotions': emotions_list,
        'period': 'weekly'
    })

@app.route('/api/insights/observations')
@jwt_required()
def observations():
    user_id = int(get_jwt_identity())
    sessions = Session.query.filter_by(user_id=user_id, status='completed').order_by(Session.created_at.desc()).limit(10).all()
    
    obs_list = []
    for s in sessions:
        # Try to get score from answers first, fallback to session mood_score
        answers = Answer.query.filter_by(session_id=s.id).all()
        if answers:
            total_score = sum(a.score or 3 for a in answers)
            avg_score = total_score / len(answers)
        else:
            # Fallback to session mood_score (scale 0-10, convert to 1-5)
            avg_score = (s.mood_score or 5) / 2
        
        # Generate observation based on score
        if avg_score >= 4:
            obs = {
                'id': s.id,
                'type': 'positive',
                'title': 'Mood Positif! 🌟',
                'description': f'Sesi pada {s.created_at.strftime("%d %b")} menunjukkan kondisi emosional yang sangat baik.',
                'session_id': s.id,
                'read': False,
                'date': s.created_at.isoformat() if s.created_at else None
            }
        elif avg_score >= 3:
            obs = {
                'id': s.id,
                'type': 'neutral',
                'title': 'Kondisi Stabil ⚖️',
                'description': f'Sesi {s.created_at.strftime("%d %b")} menunjukkan keseimbangan emosional.',
                'session_id': s.id,
                'read': False,
                'date': s.created_at.isoformat() if s.created_at else None
            }
        elif avg_score >= 2:
            obs = {
                'id': s.id,
                'type': 'pattern',
                'title': 'Pola Perlu Perhatian 💭',
                'description': f'Ada tanda-tanda yang perlu diperhatikan pada sesi {s.created_at.strftime("%d %b")}.',
                'session_id': s.id,
                'read': False,
                'date': s.created_at.isoformat() if s.created_at else None
            }
        else:
            obs = {
                'id': s.id,
                'type': 'alert',
                'title': 'Perhatian Diperlukan 💙',
                'description': f'Sesi {s.created_at.strftime("%d %b")} menunjukkan kondisi yang memerlukan dukungan.',
                'session_id': s.id,
                'read': False,
                'date': s.created_at.isoformat() if s.created_at else None
            }
        obs_list.append(obs)
    
    # If no sessions at all, return encouraging message
    if not obs_list:
        obs_list = [
            {'id': 0, 'type': 'info', 'title': 'Mulai Perjalananmu 🌱', 'description': 'Selesaikan sesi pertamamu untuk melihat AI observations.', 'read': False}
        ]
    
    return jsonify(obs_list)

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
