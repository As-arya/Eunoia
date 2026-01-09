"""Gemini AI Service - Enhanced with Evidence-Based Mental Health Support"""
import os
import json
import random
import google.generativeai as genai

# Load JSON datasets
def load_json_data(filename):
    """Load JSON file from data directory"""
    try:
        # Data folder is at backend/data/, not backend/app/data/
        # __file__ is app/services/gemini_service.py
        # Go up 3 levels to backend/, then into data/
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"[Gemini] Data file not found: {filepath}")
    except Exception as e:
        print(f"[Gemini] Error loading {filename}: {e}")
    return None

# Load datasets at module level
EMPATHY_RESPONSES = load_json_data('empathy_responses.json') or {}
CRISIS_DATA = load_json_data('crisis_detection.json') or {}

# Emotion mapping: Maps 50+ emotion tags to 8 main categories
EMOTION_MAPPING = {
    # Happy category
    'Happy': 'Happy', 'Stable': 'Happy', 'Energetic': 'Happy', 'Confident': 'Happy',
    'Rested': 'Happy', 'Balanced': 'Happy', 'Functional': 'Happy', 'Productive': 'Happy',
    'Connected': 'Happy', 'Supported': 'Happy', 'Resourceful': 'Happy', 'Resilient': 'Happy',
    'Social': 'Happy', 'Calm': 'Happy', 'Relaxed': 'Happy', 'Focused': 'Happy',
    'Clear': 'Happy', 'Managed': 'Happy', 'Open': 'Happy', 'Even_tempered': 'Happy',
    
    # Anxious category
    'Anxious': 'Anxious', 'Severely_anxious': 'Anxious', 'Occasionally_anxious': 'Anxious',
    'Worried': 'Anxious', 'Somewhat_worried': 'Anxious', 'Overwhelmed_by_worry': 'Anxious',
    'Tense': 'Anxious', 'Very_tense': 'Anxious', 'Cannot_relax': 'Anxious',
    'Uneasy': 'Anxious', 'Catastrophizing': 'Anxious', 'Mild_symptoms': 'Anxious',
    'Moderate_symptoms': 'Anxious', 'Severe_symptoms': 'Anxious', 'Controlled': 'Anxious',
    
    # Sad category
    'Sad': 'Sad', 'Occasionally_sad': 'Sad', 'Depressed': 'Sad', 'Low': 'Sad',
    'Lonely': 'Sad', 'Very_lonely': 'Sad', 'Occasionally_lonely': 'Sad',
    'Guilty': 'Sad', 'Worthless': 'Sad', 'Self_doubt': 'Sad',
    
    # Stressed category
    'Stressed': 'Stressed', 'Stress': 'Stressed', 'Sometimes_busy': 'Stressed',
    'Strained': 'Stressed', 'Conflicted': 'Stressed', 'Affected': 'Stressed',
    'Mildly_affected': 'Stressed', 'Severely_affected': 'Stressed',
    
    # Tired category
    'Tired': 'Tired', 'Fatigued': 'Tired', 'Exhausted': 'Tired', 'Severely_fatigued': 'Tired',
    'Disturbed_sleep': 'Tired', 'Insomnia': 'Tired',
    
    # Overwhelmed category
    'Overwhelmed': 'Overwhelmed', 'Distressed': 'Overwhelmed', 'Scattered': 'Overwhelmed',
    'Unfocused': 'Overwhelmed', 'Distracted': 'Overwhelmed', 'Foggy': 'Overwhelmed',
    'Confused': 'Overwhelmed', 'Moderate_difficulty': 'Overwhelmed', 'Severe_difficulty': 'Overwhelmed',
    'Mild_difficulty': 'Overwhelmed',
    
    # Angry category
    'Angry': 'Angry', 'Irritable': 'Angry', 'Very_irritable': 'Angry',
    'Occasionally_irritable': 'Angry',
    
    # Hopeless category
    'Hopeless': 'Hopeless', 'Isolated': 'Hopeless', 'Limited_support': 'Hopeless',
    'Withdrawn': 'Hopeless', 'Avoiding': 'Hopeless', 'Occasionally_avoiding': 'Hopeless',
    'Limited_coping': 'Hopeless', 'No_coping': 'Hopeless', 'Low_resilience': 'Hopeless',
    'Not_resilient': 'Hopeless', 'Ambivalent': 'Hopeless', 'Resistant': 'Hopeless',
    'Dismissive': 'Hopeless', 'Moderate_resilience': 'Hopeless',
    
    # Neutral defaults
    'Neutral': 'default', 'Coping': 'default', 'Somewhat_supported': 'default',
}

def get_mapped_emotion(emotion: str) -> str:
    """Map detailed emotion tags to main empathy categories"""
    if not emotion:
        return 'default'
    return EMOTION_MAPPING.get(emotion, 'default')

def get_sample_responses_for_prompt(emotion: str, count: int = 2) -> str:
    """Get sample empathy responses to include in Gemini prompt as style reference"""
    mapped_emotion = get_mapped_emotion(emotion)
    responses = EMPATHY_RESPONSES.get(mapped_emotion, EMPATHY_RESPONSES.get('default', []))
    
    if not responses:
        return ""
    
    # Get random samples
    samples = random.sample(responses, min(count, len(responses)))
    sample_texts = [s.get('response', '') for s in samples if isinstance(s, dict)]
    
    if sample_texts:
        return "\n".join([f"- \"{text}\"" for text in sample_texts])
    return ""

def configure_gemini():
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key and api_key != 'your-gemini-api-key-here':
        genai.configure(api_key=api_key)
        print("✓ Gemini configured with API key")
        return True
    print("⚠ No valid GEMINI_API_KEY - using fallback responses")
    return False

def detect_crisis(message: str) -> tuple:
    """Detect crisis keywords and return (is_crisis, risk_level, response)"""
    if not CRISIS_DATA or not message:
        return False, "none", None
    
    message_lower = message.lower()
    
    # Check high risk keywords
    high_risk_keywords = CRISIS_DATA.get('crisis_keywords', {}).get('high_risk', {}).get('keywords', [])
    for keyword in high_risk_keywords:
        if keyword in message_lower:
            crisis_response = CRISIS_DATA.get('crisis_responses', {}).get('immediate_safety', {})
            return True, "high", crisis_response.get('response')
    
    # Check moderate risk
    moderate_keywords = CRISIS_DATA.get('crisis_keywords', {}).get('moderate_risk', {}).get('keywords', [])
    for keyword in moderate_keywords:
        if keyword in message_lower:
            return True, "moderate", CRISIS_DATA.get('crisis_responses', {}).get('supportive_exploration', {}).get('response')
    
    return False, "none", None

def get_empathy_response(emotion: str = None, intensity: str = None) -> str:
    """Get a varied empathetic response based on emotion from JSON dataset"""
    mapped_emotion = get_mapped_emotion(emotion)
    
    if EMPATHY_RESPONSES:
        responses = EMPATHY_RESPONSES.get(mapped_emotion, EMPATHY_RESPONSES.get('default', []))
        
        if responses:
            if intensity:
                filtered = [r for r in responses if r.get('intensity') == intensity]
                if filtered:
                    responses = filtered
            
            choice = random.choice(responses)
            return choice.get('response', choice) if isinstance(choice, dict) else choice
    
    # Fallback responses
    fallbacks = {
        'Happy': "Senang mendengar itu! Semoga hal baik terus datang untukmu. 🌟",
        'Anxious': "Kecemasan itu berat. Kamu tidak sendirian. 💙",
        'Sad': "Aku turut merasakan bebanmu. Tidak apa-apa untuk bersedih.",
        'Stressed': "Tekanan yang kamu rasakan itu nyata. Mari cari cara mengatasinya.",
        'Tired': "Kelelahan bisa sangat overwhelming. Sudahkah kamu beristirahat?",
        'Overwhelmed': "Beban yang kamu tanggung sangat berat. Kamu sudah sangat kuat. 💙",
    }
    return fallbacks.get(mapped_emotion, "Terima kasih sudah berbagi. Aku mendengarmu. 💙")

def get_ai_response(user_answer: str, question: str = "", emotion: str = None) -> str:
    """Generate empathetic AI response with style reference from curated dataset"""
    # First check for crisis
    is_crisis, risk_level, crisis_response = detect_crisis(user_answer)
    if is_crisis and risk_level == "high":
        return crisis_response or "Keselamatanmu adalah prioritas. Hubungi 119 ext 8 (24 jam) SEKARANG."
    
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your-gemini-api-key-here':
            return get_empathy_response(emotion)
        
        # Get sample responses as style reference
        mapped_emotion = get_mapped_emotion(emotion)
        sample_responses = get_sample_responses_for_prompt(emotion, count=2)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""Kamu adalah Eunoia, AI companion empatik yang hangat untuk kesehatan mental.

Pertanyaan yang ditanyakan: "{question}"
Jawaban user: "{user_answer}"
Emosi terdeteksi: {mapped_emotion}

CONTOH GAYA RESPONS YANG DIINGINKAN (gunakan sebagai inspirasi, JANGAN salin langsung):
{sample_responses}

Tugas:
1. Berikan respons yang empatik dan personal, terinspirasi dari gaya contoh di atas
2. Tunjukkan bahwa kamu benar-benar mendengar dan memahami
3. Berikan validasi yang sesuai dengan emosi {mapped_emotion}
4. Gunakan bahasa Indonesia yang hangat dan natural
5. Maksimal 2-3 kalimat
6. Boleh gunakan emoji 1x jika sesuai (💙 atau 🌟)

PENTING:
- Jangan pernah memulai dengan "Terima kasih sudah berbagi" atau respons generik
- Buat respons yang unik dan personal untuk situasi user
- Jadikan contoh sebagai referensi gaya, bukan template
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[Gemini Error] {e}")
        return get_empathy_response(emotion)

def generate_summary(responses: list, score: int) -> str:
    """Generate session summary with score interpretation, deep analysis, and strong reasoning"""
    total_questions = len(responses)
    
    # PHQ-9 style interpretation with more nuanced analysis
    if score <= 7:
        severity = "minimal"
        base_summary = f"""Berdasarkan {total_questions} pertanyaan screening, kondisi emosionalmu menunjukkan kesejahteraan yang baik. 
Skor rendahmu mengindikasikan bahwa kamu memiliki kemampuan coping yang efektif dan stabilitas emosional yang solid. 
Ini adalah fondasi yang kuat untuk kesehatan mental jangka panjang. Tetap jaga kebiasaan positif yang sudah kamu bangun."""
    elif score <= 14:
        severity = "mild"
        base_summary = f"""Dari analisis {total_questions} respons, aku melihat ada beberapa area yang mungkin perlu perhatian ekstra. 
Secara umum kamu menunjukkan kemampuan mengelola emosi dengan baik, namun ada momen-momen di mana tekanan terasa lebih berat. 
Ini normal dan menunjukkan kesadaran diri yang baik. Fokus pada self-care dan jangan ragu untuk mencari dukungan saat diperlukan."""
    elif score <= 21:
        severity = "moderate"
        base_summary = f"""Berdasarkan {total_questions} respons yang kamu berikan, aku melihat beberapa tantangan signifikan yang sedang kamu hadapi. 
Pola responsmu menunjukkan bahwa beban emosional ini mempengaruhi beberapa aspek kehidupanmu. 
Ini bukan kelemahan - mengenali ini adalah kekuatan. Pertimbangkan untuk berbicara dengan profesional kesehatan mental yang dapat memberikan dukungan lebih terarah."""
    else:
        severity = "moderately_severe"
        base_summary = f"""Dari {total_questions} pertanyaan, kondisimu menunjukkan bahwa kamu sedang menanggung beban emosional yang cukup berat. 
Respondsmu mengindikasikan dampak yang konsisten pada berbagai area kehidupan, dari tidur hingga hubungan sosial. 
Ini memerlukan perhatian serius, dan mencari bantuan profesional bukan tanda kelemahan tapi langkah berani menuju pemulihan. 
Sangat disarankan untuk segera konsultasi dengan psikolog atau psikiater."""
    
    # Analyze emotion patterns for better insight
    emotion_counts = {}
    for r in responses:
        answer = r.get('a', '').lower()
        if 'sering' in answer or 'selalu' in answer:
            emotion_counts['high_frequency'] = emotion_counts.get('high_frequency', 0) + 1
        if 'tidak' in answer or 'baik' in answer:
            emotion_counts['positive'] = emotion_counts.get('positive', 0) + 1
    
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your-gemini-api-key-here':
            return base_summary
        
        # Get sample empathy responses for style guidance
        sample_responses = get_sample_responses_for_prompt('default', count=2)
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        text = "\n".join([f"Q: {r['q']}\nA: {r['a']}" for r in responses])
        
        prompt = f"""Kamu adalah Eunoia, AI companion empatik untuk kesehatan mental Indonesia.

Berdasarkan screening kesehatan mental dengan severity level: {severity}
Total pertanyaan: {total_questions}
Skor total: {score}

RESPONS USER:
{text}

CONTOH GAYA PENULISAN YANG DIINGINKAN:
{sample_responses}

Buat RINGKASAN KOMPREHENSIF dengan format berikut (5-7 kalimat WAJIB):

1. OBSERVASI UTAMA: Satu kalimat yang merangkum kondisi emosional keseluruhan berdasarkan pola respons.

2. ANALISIS POLA: Identifikasi 1-2 pola yang muncul dari jawaban user (misalnya: kesulitan tidur yang mempengaruhi energi, atau kecemasan yang berkaitan dengan tekanan sosial). Jelaskan hubungan sebab-akibat jika ada.

3. KEKUATAN TERIDENTIFIKASI: Sebutkan minimal satu hal positif atau kekuatan yang terlihat dari respons user.

4. AREA PERHATIAN: Satu area spesifik yang perlu perhatian lebih, dengan alasan mengapa.

5. PESAN SUPORTIF: Tutup dengan kalimat yang memvalidasi dan memberi harapan.

ATURAN PENTING:
- Gunakan bahasa Indonesia yang hangat, natural, dan profesional
- JANGAN sebutkan skor numerik secara langsung
- Gunakan "kamu" bukan "Anda" untuk kesan lebih personal
- Boleh gunakan maksimal 1 emoji (💙 atau 🌟) di akhir
- Hasil harus 5-7 kalimat yang mengalir dengan baik
- Berikan reasoning yang jelas untuk setiap observasi"""

        result = model.generate_content(prompt)
        return result.text.strip()
    except Exception as e:
        print(f"[Gemini Summary Error] {e}")
        return base_summary

def get_recommendation(score: int, emotion: str) -> str:
    """Generate evidence-based recommendation with mapped emotion"""
    # Map emotion first
    mapped_emotion = get_mapped_emotion(emotion)
    
    # Score-based recommendations
    if score <= 7:
        recommendations = [
            "Pertahankan rutinitas positifmu! Olahraga teratur dan tidur cukup adalah kunci.",
            "Terus jaga keseimbangan emosimu dengan aktivitas yang membuatmu bahagia.",
        ]
        return random.choice(recommendations)
    elif score <= 14:
        recommendations = {
            'Anxious': "Coba latihan pernapasan 4-7-8: tarik napas 4 detik, tahan 7 detik, buang 8 detik. Ini membantu menenangkan sistem saraf.",
            'Sad': "Habiskan 10-15 menit di luar rumah hari ini. Cahaya matahari membantu memperbaiki mood.",
            'Stressed': "Prioritaskan satu tugas kecil yang bisa kamu selesaikan hari ini. Pencapaian kecil mengurangi overwhelm.",
            'Tired': "Tetapkan jadwal tidur konsisten selama seminggu. Hindari layar 1 jam sebelum tidur.",
            'Overwhelmed': "Ambil jeda sejenak. Fokus pada satu hal kecil yang bisa kamu kontrol hari ini.",
            'Hopeless': "Kamu tidak sendirian. Pertimbangkan untuk berbicara dengan seseorang yang kamu percaya.",
            'Angry': "Coba teknik grounding: identifikasi 5 hal yang bisa kamu lihat, 4 yang bisa disentuh, 3 yang didengar.",
            'default': "Luangkan 15 menit untuk aktivitas yang membuatmu tenang dan bahagia hari ini."
        }
        return recommendations.get(mapped_emotion, recommendations.get('default'))
    elif score <= 21:
        return "Pertimbangkan untuk berbicara dengan psikolog atau konselor. Kamu bisa menghubungi Hotline Kesehatan Jiwa 119 ext 8 untuk konsultasi awal."
    else:
        return "Sangat disarankan untuk segera konsultasi dengan psikolog atau psikiater. Hubungi Hotline Kesehatan Jiwa 119 ext 8 (24 jam) atau Yayasan Pulih +62 811-1711-555."



