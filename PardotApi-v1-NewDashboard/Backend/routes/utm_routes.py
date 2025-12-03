from flask import Blueprint, jsonify, g
from services.utm_service import get_utm_analysis
from middleware.auth_middleware import require_auth
<<<<<<< HEAD
from cache import get_cached_data, set_cached_data
=======
from cache import get_cached_data,set_cached_data
>>>>>>> f378ea016ddbaa9c4f5971c5d82480a01750cb70

utm_bp = Blueprint('utm', __name__)

@utm_bp.route("/get-utm-analysis", methods=["GET"])
@require_auth
def get_utm_analysis_route():
    try:
<<<<<<< HEAD
        cache_key = f"utm_analysis:{g.access_token[:20]}"
        
        # Check cache first
        cached_data = get_cached_data(cache_key)
        if cached_data:
            print(f"📦 UTM ANALYSIS: Retrieved from CACHE - Key: {cache_key}")
            return jsonify(cached_data)
        
        # Fetch fresh data from API
        print(f"🌐 UTM ANALYSIS: Fetching from API - Key: {cache_key}")
        analysis_data = get_utm_analysis(g.access_token)
        
        # Cache the analysis for 30 minutes
        set_cached_data(cache_key, analysis_data, ttl=1800)
        print(f"💾 UTM ANALYSIS: Cached for 30 minutes - Key: {cache_key}")
        
=======
        cache_key= f'UTM:{g.access_token[:20]}'

        cached_data= get_cached_data(cache_key)
        if cached_data:
            return jsonify(cached_data)
        
        analysis_data = get_utm_analysis(g.access_token)
        set_cached_data(cache_key,analysis_data,ttl=1800)
>>>>>>> f378ea016ddbaa9c4f5971c5d82480a01750cb70
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

