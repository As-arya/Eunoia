"""Session Service"""
from datetime import datetime
from app.extensions import db
from app.models import Session, SessionInsight

def create_session(user_id, title=None, session_type='screening'):
    session = Session(
        user_id=user_id,
        title=title or f'Session {datetime.now().strftime("%d %b")}',
        session_type=session_type
    )
    db.session.add(session)
    db.session.commit()
    return session

def get_sessions(user_id, page=1, per_page=20):
    p = Session.query.filter_by(user_id=user_id).order_by(Session.started_at.desc()).paginate(page=page, per_page=per_page)
    return {'sessions': [s.to_dict() for s in p.items], 'total': p.total, 'pages': p.pages}

def get_recent(user_id, limit=5):
    return [s.to_dict() for s in Session.query.filter_by(user_id=user_id).order_by(Session.started_at.desc()).limit(limit).all()]

def get_session(session_id, user_id):
    return Session.query.filter_by(id=session_id, user_id=user_id).first()

def delete_session(session_id, user_id):
    s = get_session(session_id, user_id)
    if s:
        db.session.delete(s)
        db.session.commit()
        return True
    return False

def end_session(session_id, user_id):
    s = get_session(session_id, user_id)
    if s:
        s.ended_at = datetime.utcnow()
        s.duration = max(1, int((s.ended_at - s.started_at).total_seconds() / 60)) if s.started_at else 1
        db.session.commit()
    return s

def get_insights(session_id, user_id):
    s = get_session(session_id, user_id)
    if not s:
        return None
    insight = SessionInsight.query.filter_by(session_id=session_id).first()
    if insight:
        return insight.to_dict()
    # Try to generate insights from screening service
    from app.services import screening_service
    generated = screening_service.get_summary(session_id, user_id)
    if generated and 'error' not in generated:
        return generated
    # Return default insights if generation failed
    return {
        'summary': 'Summary will be generated after completing the session.',
        'recommendation': 'Complete your session to receive personalized recommendations.',
        'primary_trigger': 'Not yet identified',
        'breakthrough': 'Keep sharing to discover insights',
        'mood_improvement': 0,
        'score': 0
    }
