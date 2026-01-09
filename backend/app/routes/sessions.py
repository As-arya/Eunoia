"""Sessions Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import session_service

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    page = request.args.get('page', 1, type=int)
    result = session_service.get_sessions(int(get_jwt_identity()), page)
    return jsonify(result), 200

@sessions_bp.route('/', methods=['POST'])
@jwt_required()
def create():
    data = request.get_json() or {}
    s = session_service.create_session(int(get_jwt_identity()), data.get('title'), data.get('session_type', 'screening'))
    return jsonify(s.to_dict()), 201

@sessions_bp.route('/recent', methods=['GET'])
@jwt_required()
def recent():
    limit = request.args.get('limit', 5, type=int)
    return jsonify({'sessions': session_service.get_recent(int(get_jwt_identity()), limit)}), 200

@sessions_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_one(id):
    s = session_service.get_session(id, int(get_jwt_identity()))
    if s:
        return jsonify(s.to_dict()), 200
    return jsonify({'error': 'Not found'}), 404

@sessions_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    if session_service.delete_session(id, int(get_jwt_identity())):
        return jsonify({'message': 'Deleted'}), 200
    return jsonify({'error': 'Not found'}), 404

@sessions_bp.route('/<int:id>/end', methods=['POST'])
@jwt_required()
def end(id):
    s = session_service.end_session(id, int(get_jwt_identity()))
    if s:
        return jsonify(s.to_dict()), 200
    return jsonify({'error': 'Not found'}), 404

@sessions_bp.route('/<int:id>/insights', methods=['GET'])
@jwt_required()
def insights(id):
    i = session_service.get_insights(id, int(get_jwt_identity()))
    if i is None:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify(i), 200

