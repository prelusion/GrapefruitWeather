from flask import Blueprint, jsonify, request
from app import db

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/tracks')
def get_racing_tracks():
    track_id = request.args.get("id")
    name = request.args.get("name")
    city = request.args.get("city")
    country = request.args.get("country")

    racing_tracks = db.get_racing_tracks(track_id, name, city, country)

    return jsonify({
        "data": racing_tracks,
        "total": len(racing_tracks),
        "offset": 0,
        "limit": 50,
    })
