from flask import Blueprint, jsonify, g
import logging
from services.engagement_service import get_engagement_programs_analysis, EngagementServiceError
from middleware.auth_middleware import require_auth
from cache import get_cached_data, set_cached_data

logger = logging.getLogger(__name__)

engagement_bp = Blueprint('engagement', __name__)

@engagement_bp.route("/get-engagement-programs-analysis", methods=["GET"])
@require_auth
def get_engagement_programs_analysis_route():
    try:
        cache_key = f"engagement_programs:{g.access_token[:20]}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            return jsonify(cached_data)
        
        engagement_data = get_engagement_programs_analysis(g.access_token)
        set_cached_data(cache_key, engagement_data, ttl=1800)
        return jsonify(engagement_data)
    except EngagementServiceError as e:
        logger.error(f"Engagement service error: {str(e)}")
        return jsonify({"error": "Failed to fetch engagement programs", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error in engagement programs: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500