"""Auth Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import auth_service
from app.services.auth_service import AuthError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    try:
        result = auth_service.register(data.get('name'), data.get('email'), data.get('password'))
        return jsonify({'message': 'Registered', **result}), 201
    except AuthError as e:
        return jsonify({'error': e.message}), e.status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    try:
        result = auth_service.login(data.get('email'), data.get('password'))
        return jsonify({'message': 'Login successful', **result}), 200
    except AuthError as e:
        return jsonify({'error': e.message}), e.status_code

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    token = auth_service.refresh(get_jwt_identity())
    return jsonify({'access_token': token}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logged out'}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = auth_service.get_user(int(get_jwt_identity()))
    return jsonify(user.to_dict()) if user else jsonify({'error': 'Not found'}), 404
