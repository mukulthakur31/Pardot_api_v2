from flask import Blueprint, request, jsonify, g
from services.email_service import get_email_stats
from middleware.auth_middleware import require_auth
from cache import get_cached_data, set_cached_data

email_bp = Blueprint('email', __name__)

@email_bp.route("/get-email-stats", methods=["GET"])
@require_auth
def get_email_stats_route():
    try:
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        cache_key = f"emails:{g.access_token[:20]}:{filter_type or 'all'}:{start_date or ''}:{end_date or ''}"
        
        # Check cache first
        cached_data = get_cached_data(cache_key)
        if cached_data:
            print(f"📦 EMAIL DATA: Retrieved from CACHE - Key: {cache_key}")
            return jsonify(cached_data)
        
        # Fetch fresh data from API
        print(f"🌐 EMAIL DATA: Fetching from API - Key: {cache_key}")
        stats_list = get_email_stats(g.access_token, filter_type, start_date, end_date)
        
        # Cache the data for 30 minutes
        set_cached_data(cache_key, stats_list, ttl=1800)
        print(f"💾 EMAIL DATA: Cached for 30 minutes - Key: {cache_key}")
        
        return jsonify(stats_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500