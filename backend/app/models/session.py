"""Session Models"""
from datetime import datetime
from app.extensions import db

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100))
    session_type = db.Column(db.String(50), default='screening')
    mood = db.Column(db.String(50))
    duration = db.Column(db.Integer)
    summary = db.Column(db.Text)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    
    responses = db.relationship('ScreeningResponse', backref='session', lazy='dynamic')
    insight = db.relationship('SessionInsight', backref='session', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'title': self.title,
            'session_type': self.session_type, 'mood': self.mood,
            'duration': self.duration, 'summary': self.summary,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None
        }

class SessionInsight(db.Model):
    __tablename__ = 'session_insights'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    summary = db.Column(db.Text)
    score = db.Column(db.Integer)
    recommendation = db.Column(db.Text)
    primary_trigger = db.Column(db.String(100))
    breakthrough = db.Column(db.String(255))
    mood_improvement = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id, 'session_id': self.session_id, 'summary': self.summary,
            'score': self.score, 'recommendation': self.recommendation,
            'primary_trigger': self.primary_trigger, 'breakthrough': self.breakthrough,
            'mood_improvement': self.mood_improvement
        }

class MoodEntry(db.Model):
    __tablename__ = 'mood_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mood = db.Column(db.String(50), nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
