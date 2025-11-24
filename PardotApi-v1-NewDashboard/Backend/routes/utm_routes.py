from flask import Blueprint, request, jsonify, g
from services.utm_service import get_utm_analysis, get_campaign_engagement_analysis
from middleware.auth_middleware import require_auth

utm_bp = Blueprint('utm', __name__)

@utm_bp.route("/get-utm-analysis", methods=["GET"])
@require_auth
def get_utm_analysis_route():
    
    try:
        analysis_data = get_utm_analysis(g.access_token)
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@utm_bp.route("/get-campaign-engagement-analysis", methods=["GET"])
def get_campaign_engagement_analysis_route():
    try:
        months = request.args.get("months", "6")
        analysis_data = get_campaign_engagement_analysis(months)
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500