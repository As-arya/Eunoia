"""Auth Service"""
from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db
from app.models import User

class AuthError(Exception):
    def __init__(self, msg, code=400):
        self.message = msg
        self.status_code = code

def register(name, email, password):
    if not all([name, email, password]):
        raise AuthError('All fields required', 400)
    if User.query.filter_by(email=email).first():
        raise AuthError('Email exists', 409)
    
    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return {
        'user': user.to_dict(),
        'access_token': create_access_token(identity=str(user.id)),
        'refresh_token': create_refresh_token(identity=str(user.id))
    }

def login(email, password):
    if not email or not password:
        raise AuthError('Email and password required', 400)
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise AuthError('Invalid credentials', 401)
    
    return {
        'user': user.to_dict(),
        'access_token': create_access_token(identity=str(user.id)),
        'refresh_token': create_refresh_token(identity=str(user.id))
    }

def refresh(user_id):
    return create_access_token(identity=str(user_id))

def get_user(user_id):
    return User.query.get(user_id)
