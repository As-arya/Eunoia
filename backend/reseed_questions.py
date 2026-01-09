"""Reseed screening questions - Run this to update the database with new questions"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import ScreeningQuestion, AnswerOption

def reseed_questions():
    """Delete existing questions and reseed with new ones"""
    app = create_app()
    
    with app.app_context():
        # Delete existing answers and questions
        print("Deleting existing questions and options...")
        AnswerOption.query.delete()
        ScreeningQuestion.query.delete()
        db.session.commit()
        print("✓ Cleared existing data")
        
        # Seed new questions
        from app.seeds.questions import seed_questions
        seed_questions()
        print("✓ Reseeded with new varied questions!")

if __name__ == '__main__':
    reseed_questions()
