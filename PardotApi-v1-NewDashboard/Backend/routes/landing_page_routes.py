from flask import Blueprint, request, jsonify, g
from services.Landing_page_service import get_landing_page_stats, get_date_range_from_filter
from middleware.auth_middleware import require_auth
from cache import get_cached_data, set_cached_data
from datetime import datetime

landing_page_bp = Blueprint('landing_page', __name__)

@landing_page_bp.route("/get-landing-page-stats", methods=["GET"])
@require_auth
def get_landing_page_stats_route():
    try:
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        if filter_type and not start_date and not end_date:
            start_date, end_date = get_date_range_from_filter(filter_type)
        
        landing_page_stats = get_landing_page_stats(g.access_token, start_date, end_date)
        set_cached_data(f"landing_pages:{g.access_token[:20]}", landing_page_stats, ttl=1800)
        return jsonify(landing_page_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

