"""Screening Models"""
from datetime import datetime
from app.extensions import db

class ScreeningQuestion(db.Model):
    __tablename__ = 'screening_questions'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=0)
    options = db.relationship('AnswerOption', backref='question', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id, 'category': self.category,
            'text': self.question_text, 'order': self.order,
            'options': [o.to_dict() for o in self.options]
        }

class AnswerOption(db.Model):
    __tablename__ = 'answer_options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('screening_questions.id'), nullable=False)
    option_text = db.Column(db.String(200), nullable=False)
    option_value = db.Column(db.Integer, default=0)
    emotion_tag = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id, 'text': self.option_text,
            'option_value': self.option_value, 'emotion_tag': self.emotion_tag
        }

class ScreeningResponse(db.Model):
    __tablename__ = 'screening_responses'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('screening_questions.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('answer_options.id'), nullable=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    question = db.relationship('ScreeningQuestion')
    selected_option = db.relationship('AnswerOption')
