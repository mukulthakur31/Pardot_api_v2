from flask import Blueprint, jsonify, g
from services.engagement_service import get_engagement_programs_analysis, get_engagement_programs_performance
from middleware.auth_middleware import require_auth
from cache import get_cached_data, set_cached_data

engagement_bp = Blueprint('engagement', __name__)

@engagement_bp.route("/get-engagement-programs-analysis", methods=["GET"])
@require_auth
def get_engagement_programs_analysis_route():
    try:
        analysis_data = get_engagement_programs_analysis(g.access_token)
        set_cached_data(f"engagement:{g.access_token[:20]}", analysis_data, ttl=1800)
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@engagement_bp.route("/get-engagement-programs-performance", methods=["GET"])
@require_auth
def get_engagement_programs_performance_route():
    try:
        cached_data = get_cached_data(f"engagement:{g.access_token[:20]}")
        if cached_data:
            performance_data = cached_data
        else:
            performance_data = get_engagement_programs_performance(g.access_token)
            set_cached_data(f"engagement:{g.access_token[:20]}", performance_data, ttl=1800)
        return jsonify(performance_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500