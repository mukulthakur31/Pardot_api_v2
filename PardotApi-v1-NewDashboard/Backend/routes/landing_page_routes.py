from flask import Blueprint, request, jsonify, g
from services.Landing_page_service import get_landing_page_stats, get_filtered_landing_page_stats, get_date_range_from_filter
from middleware.auth_middleware import require_auth
from cache import get_cached_data, set_cached_data

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

@landing_page_bp.route("/get-filtered-landing-page-stats", methods=["GET"])
@require_auth
def get_filtered_landing_page_stats_route():
    try:
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        filtered_stats = get_filtered_landing_page_stats(g.access_token, filter_type, start_date, end_date)
        return jsonify(filtered_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@landing_page_bp.route("/get-landing-page-field-issues", methods=["GET"])
@require_auth
def get_landing_page_field_issues():
    try:
        severity = request.args.get("severity", "all").lower()
        issue_type = request.args.get("type", "all").lower()
        
        cached_stats = get_cached_data(f"landing_pages:{g.access_token[:20]}")
        if cached_stats:
            landing_page_stats = cached_stats
        else:
            landing_page_stats = get_landing_page_stats(g.access_token)
            set_cached_data(f"landing_pages:{g.access_token[:20]}", landing_page_stats, ttl=1800)
            
        field_issues = landing_page_stats.get('field_mapping_issues', {})
        
        if severity != "all" and severity in field_issues:
            filtered_issues = field_issues[severity]
        else:
            filtered_issues = field_issues.get('all_issues', [])
        
        if issue_type != "all":
            filtered_issues = [issue for issue in filtered_issues if issue.get('type') == issue_type]
        
        return jsonify({
            "field_mapping_issues": filtered_issues,
            "configuration_issues": landing_page_stats.get('configuration_issues', []),
            "summary": field_issues.get('summary', {}),
            "filters_applied": {
                "severity": severity,
                "type": issue_type
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500