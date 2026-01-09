"""Routes Package"""
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.sessions import sessions_bp
from app.routes.screening import screening_bp
from app.routes.insights import insights_bp

__all__ = ['auth_bp', 'users_bp', 'sessions_bp', 'screening_bp', 'insights_bp']
