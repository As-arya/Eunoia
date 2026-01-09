"""Users Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({'error': 'User not found - please re-login'}), 401
    return jsonify(user.to_dict()), 200

@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json() or {}
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    db.session.commit()
    return jsonify(user.to_dict()), 200

@users_bp.route('/me/avatar', methods=['PUT'])
@jwt_required()
def update_avatar():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json() or {}
    user.avatar_url = data.get('avatar_url')
    db.session.commit()
    return jsonify(user.to_dict()), 200

@users_bp.route('/me/preferences', methods=['GET'])
@jwt_required()
def get_prefs():
    return jsonify({'theme': 'dark', 'language': 'id'}), 200

@users_bp.route('/me/preferences', methods=['PUT'])
@jwt_required()
def update_prefs():
    return jsonify({'message': 'Updated'}), 200
