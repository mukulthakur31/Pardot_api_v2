from flask import Blueprint, request, jsonify, g
from services.email_service import get_email_stats
from middleware.auth_middleware import require_auth

email_bp = Blueprint('email', __name__)

@email_bp.route("/get-email-stats", methods=["GET"])
@require_auth
def get_email_stats_route():
    try:
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        stats_list = get_email_stats(g.access_token, filter_type, start_date, end_date)
        return jsonify(stats_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500