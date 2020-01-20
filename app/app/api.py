from flask import Blueprint, jsonify, request


api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/tracks')
def get_racing_tracks():
    return jsonify([1, 2, 3])
