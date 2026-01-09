"""Insights Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import insights_service

insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/mood-trend', methods=['GET'])
@jwt_required()
def mood_trend():
    return jsonify(insights_service.get_mood_trend(int(get_jwt_identity()), request.args.get('period', 'weekly'))), 200

@insights_bp.route('/emotions', methods=['GET'])
@jwt_required()
def emotions():
    return jsonify(insights_service.get_emotions(int(get_jwt_identity()), request.args.get('period', 'weekly'))), 200

@insights_bp.route('/observations', methods=['GET'])
@jwt_required()
def observations():
    return jsonify({'observations': insights_service.get_observations(int(get_jwt_identity()))}), 200
