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
        
        cache_key = f"landing_pages:{g.access_token[:20]}:{filter_type or 'all'}:{start_date or ''}:{end_date or ''}"
        
        # Check cache first (with fallback if Redis unavailable)
        try:
            cached_data = get_cached_data(cache_key)
            if cached_data:
                print(f"📦 LANDING PAGE DATA: Retrieved from CACHE - Key: {cache_key}")
                return jsonify(cached_data)
        except Exception as e:
            print(f"⚠️ Cache retrieval failed, proceeding without cache: {e}")
        
        # Fetch fresh data from API
        print(f"🌐 LANDING PAGE DATA: Fetching from API - Key: {cache_key}")
        landing_page_stats = get_landing_page_stats(g.access_token, start_date, end_date)
        
        # Cache the data for 30 minutes (with fallback if Redis unavailable)
        try:
            set_cached_data(cache_key, landing_page_stats, ttl=1800)
            print(f"💾 LANDING PAGE DATA: Cached for 30 minutes - Key: {cache_key}")
        except Exception as e:
            print(f"⚠️ Cache storage failed, continuing without caching: {e}")
        
        return jsonify(landing_page_stats)
    except Exception as e:
        print(f"❌ Landing page route error: {str(e)}")
        return jsonify({"error": str(e)}), 500

