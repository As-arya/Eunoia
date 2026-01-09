"""Screening Service - Adaptive Question Selection"""
import random
from datetime import datetime
from app.extensions import db
from app.models import Session, ScreeningQuestion, AnswerOption, ScreeningResponse, SessionInsight, MoodEntry
from app.services.gemini_service import get_ai_response, generate_summary, get_recommendation

MAX_QUESTIONS = 25

def _truncate_text(text, max_length=500):
    """Truncate text at sentence boundary without cutting mid-word"""
    if not text or len(text) <= max_length:
        return text
    
    # Find last period within limit
    last_period = text[:max_length].rfind('.')
    if last_period > max_length * 0.5:  # Only use if period is in latter half
        return text[:last_period + 1]
    
    # Otherwise find last space
    last_space = text[:max_length].rfind(' ')
    if last_space > 0:
        return text[:last_space] + '...'
    
    return text[:max_length]

# Category priority based on emotional state
ADAPTIVE_CATEGORY_MAP = {
    'Depressed': ['Depression', 'Self', 'Energy', 'Social', 'Closing'],
    'Sad': ['Depression', 'Social', 'Self', 'Stress', 'Closing'],
    'Anxious': ['Anxiety', 'Stress', 'Focus', 'Sleep', 'Closing'],
    'Severely_anxious': ['Anxiety', 'Stress', 'Focus', 'Sleep', 'Closing'],
    'Overwhelmed': ['Stress', 'Anxiety', 'Energy', 'Sleep', 'Social'],
    'Stressed': ['Stress', 'Anxiety', 'Energy', 'Focus', 'Closing'],
    'Tired': ['Sleep', 'Energy', 'Depression', 'Stress', 'Closing'],
    'Exhausted': ['Sleep', 'Energy', 'Depression', 'Functional', 'Closing'],
    'Isolated': ['Social', 'Depression', 'Self', 'Anxiety', 'Closing'],
    'Distressed': ['Anxiety', 'Depression', 'Stress', 'Social', 'Closing'],
    # Default balanced approach
    'default': ['Opening', 'Depression', 'Anxiety', 'Sleep', 'Energy', 'Self', 'Focus', 'Stress', 'Social', 'Functional', 'Closing']
}

def get_next_question(session_id, user_id):
    session = Session.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return {'error': 'Not found'}
    
    answered_responses = ScreeningResponse.query.filter_by(session_id=session_id).all()
    answered_count = len(answered_responses)
    
    if answered_count >= MAX_QUESTIONS:
        return {'status': 'completed', 'progress': f'{MAX_QUESTIONS}/{MAX_QUESTIONS}'}
    
    answered_ids = [r.question_id for r in answered_responses]
    
    # Get last emotion to adapt question selection
    last_emotion = None
    cumulative_score = 0
    emotion_counts = {}
    
    for response in answered_responses:
        opt = AnswerOption.query.get(response.selected_option_id)
        if opt:
            cumulative_score += opt.option_value
            if opt.emotion_tag:
                emotion_counts[opt.emotion_tag] = emotion_counts.get(opt.emotion_tag, 0) + 1
                last_emotion = opt.emotion_tag
    
    # Determine dominant emotion for adaptive selection
    dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else last_emotion
    
    # Adaptive category priority based on dominant emotion
    priority_categories = ADAPTIVE_CATEGORY_MAP.get(dominant_emotion, ADAPTIVE_CATEGORY_MAP['default'])
    
    # Find next question adaptively
    next_question = None
    
    # Try priority categories first with randomization
    for category in priority_categories:
        query = ScreeningQuestion.query.filter(
            ScreeningQuestion.category == category
        )
        if answered_ids:
            query = query.filter(ScreeningQuestion.id.notin_(answered_ids))
        
        available = query.order_by(ScreeningQuestion.order).all()
        if available:
            # Add weighted randomization - prefer lower order questions but allow variation
            if len(available) > 1:
                weights = [max(1, 10 - (i * 2)) for i in range(len(available))]
                next_question = random.choices(available, weights=weights, k=1)[0]
            else:
                next_question = available[0]
            break
    
    # Fallback to any unanswered question
    if not next_question:
        query = ScreeningQuestion.query
        if answered_ids:
            query = query.filter(ScreeningQuestion.id.notin_(answered_ids))
        next_question = query.order_by(ScreeningQuestion.order).first()
    
    if not next_question:
        return {'status': 'completed', 'progress': f'{answered_count}/{MAX_QUESTIONS}'}
    
    return {
        'status': 'ongoing', 
        'progress': f'{answered_count+1}/{MAX_QUESTIONS}', 
        'question': next_question.to_dict(),
        'analysis': {
            'dominant_emotion': dominant_emotion,
            'cumulative_score': cumulative_score,
            'category_selected': next_question.category
        }
    }

def submit_answer(session_id, user_id, question_id, option_id):
    session = Session.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return {'error': 'Not found'}
    
    q = ScreeningQuestion.query.get(question_id)
    opt = AnswerOption.query.get(option_id)
    if not q or not opt:
        return {'error': 'Invalid'}
    
    # Check for existing response
    existing = ScreeningResponse.query.filter_by(session_id=session_id, question_id=question_id).first()
    if existing:
        existing.selected_option_id = option_id
    else:
        resp = ScreeningResponse(session_id=session_id, question_id=question_id, selected_option_id=option_id)
        db.session.add(resp)
    
    session.mood = opt.emotion_tag
    db.session.commit()
    
    ai = get_ai_response(opt.option_text, q.question_text, opt.emotion_tag)
    return {'message': 'Saved', 'ai_empathy_reply': ai, 'emotion': opt.emotion_tag}

def get_summary(session_id, user_id):
    session = Session.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return {'error': 'Not found'}
    
    # Check for existing insight
    existing = SessionInsight.query.filter_by(session_id=session_id).first()
    if existing:
        return existing.to_dict()
    
    # Generate new insight from responses
    responses = ScreeningResponse.query.filter_by(session_id=session_id).all()
    if not responses:
        return {'error': 'No responses', 'summary': 'Sesi belum memiliki respons.'}
    
    score = 0
    data = []
    emotions = {}
    
    for r in responses:
        opt = AnswerOption.query.get(r.selected_option_id)
        q = ScreeningQuestion.query.get(r.question_id)
        if opt and q:
            score += opt.option_value
            data.append({'q': q.question_text, 'a': opt.option_text})
            if opt.emotion_tag:
                emotions[opt.emotion_tag] = emotions.get(opt.emotion_tag, 0) + 1
    
    # Calculate primary emotion and mood improvement
    primary = max(emotions, key=emotions.get) if emotions else 'Neutral'
    total_responses = len(responses)
    max_possible_score = total_responses * 3  # Max 3 per question
    normalized_score = int((score / max(max_possible_score, 1)) * 100)
    mood_improvement = max(0, 50 - normalized_score)  # Higher score = worse, so invert
    
    # Generate summary and recommendation
    summary_text = generate_summary(data, score)
    rec = get_recommendation(score, primary)
    
    # Identify breakthrough based on positive responses
    positive_emotions = ['Happy', 'Calm', 'Relaxed', 'Supported', 'Confident', 'Functional']
    positive_count = sum(emotions.get(e, 0) for e in positive_emotions)
    
    if positive_count > total_responses / 2:
        breakthrough = f"Kamu menunjukkan kekuatan dalam {positive_count} area positif!"
    elif primary in ['Anxious', 'Severely_anxious']:
        breakthrough = "Langkah berani dengan mengakui kecemasan dan mencari bantuan."
    elif primary in ['Sad', 'Depressed']:
        breakthrough = "Berbagi perasaanmu adalah langkah pertama menuju penyembuhan."
    else:
        breakthrough = "Kesadaran diri adalah langkah penting dalam perjalanan kesehatan mental."
    
    # Create insight record
    insight = SessionInsight(
        session_id=session_id,
        summary=summary_text,
        score=score,
        recommendation=rec,
        primary_trigger=primary,
        breakthrough=breakthrough,
        mood_improvement=mood_improvement
    )
    db.session.add(insight)
    
    # Update session
    session.ended_at = datetime.utcnow()
    session.mood = primary
    session.summary = _truncate_text(summary_text, 500) if summary_text else "Sesi selesai."
    
    # Add mood entry for tracking
    db.session.add(MoodEntry(user_id=user_id, mood=primary))
    db.session.commit()
    
    return insight.to_dict()

def end_session_early(session_id, user_id):
    """End session early with minimum 3 responses required"""
    session = Session.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return {'error': 'Session not found'}
    
    responses = ScreeningResponse.query.filter_by(session_id=session_id).all()
    response_count = len(responses)
    
    # Minimum 3 responses required
    if response_count < 3:
        return {
            'error': 'Minimal 3 pertanyaan harus dijawab sebelum mengakhiri sesi',
            'current_count': response_count,
            'required_count': 3
        }
    
    # Check if already has insight (already completed)
    existing = SessionInsight.query.filter_by(session_id=session_id).first()
    if existing:
        return {
            'status': 'already_completed',
            'message': 'Sesi sudah selesai sebelumnya',
            **existing.to_dict()
        }
    
    # Generate summary for early completion
    score = 0
    data = []
    emotions = {}
    
    for r in responses:
        opt = AnswerOption.query.get(r.selected_option_id)
        q = ScreeningQuestion.query.get(r.question_id)
        if opt and q:
            score += opt.option_value
            data.append({'q': q.question_text, 'a': opt.option_text})
            if opt.emotion_tag:
                emotions[opt.emotion_tag] = emotions.get(opt.emotion_tag, 0) + 1
    
    primary = max(emotions, key=emotions.get) if emotions else 'Neutral'
    max_possible_score = response_count * 3
    normalized_score = int((score / max(max_possible_score, 1)) * 100)
    mood_improvement = max(0, 50 - normalized_score)
    
    # Generate summary and recommendation
    summary_text = generate_summary(data, score)
    rec = get_recommendation(score, primary)
    
    # Determine breakthrough
    positive_emotions = ['Happy', 'Calm', 'Relaxed', 'Supported', 'Confident', 'Functional']
    positive_count = sum(emotions.get(e, 0) for e in positive_emotions)
    
    if positive_count > response_count / 2:
        breakthrough = f"Kamu menunjukkan kekuatan dalam {positive_count} area positif!"
    elif primary in ['Anxious', 'Severely_anxious']:
        breakthrough = "Langkah berani dengan mengakui kecemasan dan mencari bantuan."
    elif primary in ['Sad', 'Depressed']:
        breakthrough = "Berbagi perasaanmu adalah langkah pertama menuju penyembuhan."
    else:
        breakthrough = "Kesadaran diri adalah langkah penting dalam perjalanan kesehatan mental."
    
    # Create insight record
    insight = SessionInsight(
        session_id=session_id,
        summary=summary_text,
        score=score,
        recommendation=rec,
        primary_trigger=primary,
        breakthrough=breakthrough,
        mood_improvement=mood_improvement
    )
    db.session.add(insight)
    
    # Update session
    session.ended_at = datetime.utcnow()
    session.mood = primary
    session.summary = _truncate_text(summary_text, 500) if summary_text else f"Sesi diakhiri lebih awal dengan {response_count} respons."
    
    # Add mood entry
    db.session.add(MoodEntry(user_id=user_id, mood=primary))
    db.session.commit()
    
    return {
        'status': 'completed',
        'message': f'Sesi berhasil diakhiri dengan {response_count} pertanyaan terjawab',
        'questions_answered': response_count,
        **insight.to_dict()
    }


