"""Screening Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import screening_service

screening_bp = Blueprint('screening', __name__)

@screening_bp.route('/sessions/<int:id>/next-question', methods=['GET'])
@jwt_required()
def next_q(id):
    return jsonify(screening_service.get_next_question(id, int(get_jwt_identity()))), 200

@screening_bp.route('/sessions/<int:id>/answer', methods=['POST'])
@jwt_required()
def answer(id):
    data = request.get_json() or {}
    if not data.get('question_id') or not data.get('option_id'):
        return jsonify({'error': 'question_id and option_id required'}), 400
    return jsonify(screening_service.submit_answer(id, int(get_jwt_identity()), data['question_id'], data['option_id'])), 200

@screening_bp.route('/sessions/<int:id>/summary', methods=['GET'])
@jwt_required()
def summary(id):
    return jsonify(screening_service.get_summary(id, int(get_jwt_identity()))), 200

@screening_bp.route('/sessions/<int:id>/end', methods=['POST'])
@jwt_required()
def end_session(id):
    """End session early and generate summary from current responses"""
    return jsonify(screening_service.end_session_early(id, int(get_jwt_identity()))), 200

