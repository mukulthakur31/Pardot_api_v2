from flask import Blueprint, request, jsonify, g
from services.database_health_service import get_database_health_stats
from middleware.auth_middleware import require_auth
from cache import get_cached_data, set_cached_data

database_health_bp = Blueprint('database_health', __name__)

@database_health_bp.route("/get-database-health-stats", methods=["GET"])
@require_auth
def get_database_health_stats_route():
    try:
        # Get filter parameters
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        cache_key = f"database_health:{g.access_token[:20]}:{filter_type or 'all'}:{start_date or ''}:{end_date or ''}"
        
        # Check cache first
        cached_data = get_cached_data(cache_key)
        if cached_data:
            print(f"📦 DATABASE HEALTH: Retrieved from CACHE - Key: {cache_key}")
            return jsonify(cached_data)
        
        # Fetch fresh data from API with filters
        print(f"🌐 DATABASE HEALTH: Fetching from API - Key: {cache_key}")
        health_stats = get_database_health_stats(g.access_token, filter_type, start_date, end_date)
        
        # Cache the data for 1 hour (3600 seconds)
        set_cached_data(cache_key, health_stats, ttl=3600)
        print(f"💾 DATABASE HEALTH: Cached for 1 hour - Key: {cache_key}")
        
        return jsonify(health_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@database_health_bp.route("/get-database-health-table", methods=["GET"])
@require_auth
def get_database_health_table():
    """Get just the table data for quick display"""
    try:
        cache_key = f"database_health:{g.access_token[:20]}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data and 'database_health_table' in cached_data:
            return jsonify({
                "table": cached_data['database_health_table'],
                "summary": cached_data.get('summary', {})
            })
        
        # If no cache, return error asking to fetch full data first
        return jsonify({"error": "Please fetch database health stats first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@database_health_bp.route("/get-database-health-charts", methods=["GET"])
@require_auth
def get_database_health_charts():
    """Get chart data for visualizations"""
    try:
        cache_key = f"database_health:{g.access_token[:20]}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data and 'chart_data' in cached_data:
            return jsonify(cached_data['chart_data'])
        
        return jsonify({"error": "Please fetch database health stats first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@database_health_bp.route("/get-database-health-recommendations", methods=["GET"])
@require_auth
def get_database_health_recommendations():
    """Get recommendations based on database health"""
    try:
        cache_key = f"database_health:{g.access_token[:20]}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data and 'recommendations' in cached_data:
            return jsonify({"recommendations": cached_data['recommendations']})
        
        return jsonify({"error": "Please fetch database health stats first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@database_health_bp.route("/get-prospect-health-data", methods=["GET"])
@require_auth
def get_prospect_health_data():
    """Get comprehensive prospect health data with three sections"""
    try:
        # Get filter parameters
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        cache_key = f"prospect_health:{g.access_token[:20]}:{filter_type or 'all'}:{start_date or ''}:{end_date or ''}"
        
        # Check cache first
        cached_data = get_cached_data(cache_key)
        if cached_data:
            print(f"📦 PROSPECT HEALTH: Retrieved from CACHE - Key: {cache_key}")
            return jsonify(cached_data)
        
        # Fetch fresh data from API with filters
        print(f"🌐 PROSPECT HEALTH: Fetching from API - Key: {cache_key}")
        prospect_health_data = get_database_health_stats(g.access_token, filter_type, start_date, end_date)
        
        # Cache the data for 1 hour
        set_cached_data(cache_key, prospect_health_data, ttl=3600)
        print(f"💾 PROSPECT HEALTH: Cached for 1 hour - Key: {cache_key}")
        
        return jsonify(prospect_health_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@database_health_bp.route("/get-active-contacts", methods=["GET"])
@require_auth
def get_active_contacts():
    """Get active contacts section data"""
    try:
        cache_key = f"prospect_health:{g.access_token[:20]}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data and 'active_contacts' in cached_data:
            return jsonify(cached_data['active_contacts'])
        
        return jsonify({"error": "Please fetch prospect health data first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@database_health_bp.route("/get-inactive-contacts", methods=["GET"])
@require_auth
def get_inactive_contacts():
    """Get inactive contacts section data"""
    try:
        cache_key = f"prospect_health:{g.access_token[:20]}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data and 'inactive_contacts' in cached_data:
            return jsonify(cached_data['inactive_contacts'])
        
        return jsonify({"error": "Please fetch prospect health data first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@database_health_bp.route("/get-empty-details", methods=["GET"])
@require_auth
def get_empty_details():
    """Get empty details section data"""
    try:
        cache_key = f"prospect_health:{g.access_token[:20]}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data and 'empty_details' in cached_data:
            return jsonify(cached_data['empty_details'])
        
        return jsonify({"error": "Please fetch prospect health data first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@database_health_bp.route("/get-pdf-modal-options", methods=["GET"])
@require_auth
def get_pdf_modal_options():
    """Get comprehensive PDF sections for modal selection"""
    try:
        # Check if prospect health data is available
        cache_key = f"prospect_health:{g.access_token[:20]}"
        cached_data = get_cached_data(cache_key)
        
        # Define comprehensive modal options with detailed subsections
        modal_options = {
            "title": "Customize Your Prospect Health PDF Report",
            "description": "Select which sections and metrics to include in your comprehensive report:",
            "sections": [
                {
                    "id": "active_contacts",
                    "label": "Active Contacts Analysis",
                    "description": "Engagement metrics and activity data",
                    "enabled": True,
                    "default": True,
                    "subsections": [
                        {"id": "total_database", "label": "Total Database Count", "default": True},
                        {"id": "active_leads_6m", "label": "Active Leads (6 months)", "default": True},
                        {"id": "marketable_leads", "label": "Marketable Leads", "default": True},
                        {"id": "form_submissions", "label": "Form Submissions", "default": True},
                        {"id": "email_opens", "label": "Email Opens", "default": True},
                        {"id": "email_deliveries", "label": "Email Deliveries", "default": True},
                        {"id": "page_views", "label": "Page Views", "default": True},
                        {"id": "leads_30_days", "label": "Leads Created (30 days)", "default": True},
                        {"id": "leads_60_days", "label": "Leads Created (60 days)", "default": True},
                        {"id": "leads_90_days", "label": "Leads Created (90 days)", "default": True}
                    ]
                },
                {
                    "id": "inactive_contacts",
                    "label": "Inactive Contacts Analysis",
                    "description": "Unsubscribed leads and inactive periods",
                    "enabled": True,
                    "default": True,
                    "subsections": [
                        {"id": "inactive_leads", "label": "Inactive Leads", "default": True},
                        {"id": "unsubscribed_leads", "label": "Unsubscribed Leads", "default": True},
                        {"id": "inactive_6m", "label": "Inactive 6 Months", "default": True},
                        {"id": "inactive_12m", "label": "Inactive 12 Months", "default": True},
                        {"id": "inactive_2y", "label": "Inactive 2 Years", "default": True},
                        {"id": "email_delivered_not_opened", "label": "Emails Delivered Not Opened", "default": True},
                        {"id": "email_opened_not_clicked", "label": "Emails Opened Not Clicked", "default": True}
                    ]
                },
                {
                    "id": "data_quality",
                    "label": "Data Quality & Issues",
                    "description": "Empty fields, duplicates, and data quality issues",
                    "enabled": True,
                    "default": True,
                    "subsections": [
                        {"id": "junk_leads", "label": "Junk/Test Leads", "default": True},
                        {"id": "duplicate_leads", "label": "Duplicate Leads", "default": True},
                        {"id": "email_empty", "label": "Empty Email Addresses", "default": True},
                        {"id": "first_name_empty", "label": "Empty First Names", "default": True},
                        {"id": "last_name_empty", "label": "Empty Last Names", "default": True},
                        {"id": "company_empty", "label": "Empty Company Names", "default": True},
                        {"id": "industry_empty", "label": "Empty Industry", "default": True},
                        {"id": "country_empty", "label": "Empty Country", "default": True},
                        {"id": "phone_empty", "label": "Empty Phone Numbers", "default": True},
                        {"id": "job_title_empty", "label": "Empty Job Titles", "default": True},
                        {"id": "city_empty", "label": "Empty City", "default": True}
                    ]
                },
                {
                    "id": "scoring_issues",
                    "label": "Lead Scoring Issues",
                    "description": "Scoring problems and grade inconsistencies",
                    "enabled": True,
                    "default": True,
                    "subsections": [
                        {"id": "no_score", "label": "Prospects with No Score", "default": True},
                        {"id": "negative_scores", "label": "Negative Scores", "default": True},
                        {"id": "grade_score_mismatch", "label": "Grade/Score Mismatches", "default": True},
                        {"id": "stale_scores", "label": "Stale/Outdated Scores", "default": True},
                        {"id": "high_score_inactive", "label": "High Score but Inactive", "default": True}
                    ]
                },
                {
                    "id": "charts",
                    "label": "Charts & Visualizations",
                    "description": "Trend charts and visual analytics",
                    "enabled": True,
                    "default": True,
                    "subsections": [
                        {"id": "lead_creation_trend", "label": "Lead Creation Trend Chart", "default": True},
                        {"id": "engagement_breakdown", "label": "Engagement Breakdown Chart", "default": True},
                        {"id": "inactive_breakdown", "label": "Inactive Breakdown Chart", "default": True},
                        {"id": "data_quality_chart", "label": "Data Quality Issues Chart", "default": True},
                        {"id": "scoring_distribution", "label": "Score Distribution Chart", "default": True}
                    ]
                },
                {
                    "id": "recommendations",
                    "label": "Strategic Recommendations",
                    "description": "Actionable insights and optimization suggestions",
                    "enabled": True,
                    "default": True,
                    "subsections": [
                        {"id": "active_recommendations", "label": "Active Contacts Recommendations", "default": True},
                        {"id": "inactive_recommendations", "label": "Inactive Contacts Recommendations", "default": True},
                        {"id": "data_quality_recommendations", "label": "Data Quality Recommendations", "default": True},
                        {"id": "scoring_recommendations", "label": "Lead Scoring Recommendations", "default": True},
                        {"id": "priority_actions", "label": "Priority Action Items", "default": True}
                    ]
                }
            ],
            "data_available": cached_data is not None,
            "export_options": {
                "include_summary": {"label": "Executive Summary", "default": True},
                "include_methodology": {"label": "Methodology Notes", "default": False},
                "include_raw_data": {"label": "Raw Data Tables", "default": False},
                "page_breaks": {"label": "Page Breaks Between Sections", "default": True}
            }
        }
        
        # If data is available, check which sections have content
        if cached_data:
            active_data = cached_data.get('active_contacts', {}).get('table_data', [])
            inactive_data = cached_data.get('inactive_contacts', {}).get('table_data', [])
            empty_data = cached_data.get('empty_details', {}).get('table_data', [])
            chart_data = cached_data.get('chart_data', {})
            recommendations = cached_data.get('recommendations', {})
            
            # Update section availability based on data
            for section in modal_options["sections"]:
                if section["id"] == "active_contacts":
                    section["enabled"] = len(active_data) > 0
                    section["record_count"] = len(active_data)
                elif section["id"] == "inactive_contacts":
                    section["enabled"] = len(inactive_data) > 0
                    section["record_count"] = len(inactive_data)
                elif section["id"] == "data_quality":
                    section["enabled"] = len(empty_data) > 0
                    section["record_count"] = len(empty_data)
                elif section["id"] == "scoring_issues":
                    section["enabled"] = True  # Always available
                    section["record_count"] = 5  # Estimated scoring issues
                elif section["id"] == "charts":
                    section["enabled"] = len(chart_data) > 0
                    section["record_count"] = len(chart_data)
                elif section["id"] == "recommendations":
                    total_recs = sum(len(recs) for recs in recommendations.values() if isinstance(recs, list))
                    section["enabled"] = total_recs > 0
                    section["record_count"] = total_recs
        
        return jsonify(modal_options)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@database_health_bp.route("/get-scoring-issues", methods=["GET"])
@require_auth
def get_scoring_issues():
    """Get lead scoring issues data"""
    try:
        cache_key = f"prospect_health:{g.access_token[:20]}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data and 'scoring_issues' in cached_data:
            return jsonify(cached_data['scoring_issues'])
        
        return jsonify({"error": "Please fetch prospect health data first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@database_health_bp.route("/get-enhanced-charts", methods=["GET"])
@require_auth
def get_enhanced_charts():
    """Get enhanced chart data with proper visualization formatting"""
    try:
        cache_key = f"prospect_health:{g.access_token[:20]}"
        cached_data = get_cached_data(cache_key)
        
        print(f"DEBUG: Cache key: {cache_key}")
        print(f"DEBUG: Cached data available: {cached_data is not None}")
        
        if cached_data and 'chart_data' in cached_data:
            chart_data = cached_data['chart_data']
            print(f"DEBUG: Chart data type: {type(chart_data)}")
            print(f"DEBUG: Chart data length: {len(chart_data) if isinstance(chart_data, (list, dict)) else 'N/A'}")
            
            # Ensure chart_data is an array
            if isinstance(chart_data, dict):
                # Convert old object format to array format
                chart_array = []
                for chart_id, chart_config in chart_data.items():
                    chart_config['id'] = chart_id
                    chart_array.append(chart_config)
                chart_data = chart_array
                print(f"DEBUG: Converted dict to array, new length: {len(chart_data)}")
            
            enhanced_charts = {
                "charts": chart_data,
                "chart_count": len(chart_data) if chart_data else 0,
                "supported_types": ["line", "bar", "doughnut", "pie", "horizontalBar", "funnel"],
                "color_schemes": {
                    "primary": ["rgba(54, 162, 235, 0.8)", "rgba(255, 99, 132, 0.8)", "rgba(255, 205, 86, 0.8)"],
                    "success": ["rgba(75, 192, 192, 0.8)", "rgba(153, 255, 153, 0.8)", "rgba(144, 238, 144, 0.8)"],
                    "warning": ["rgba(255, 159, 64, 0.8)", "rgba(255, 206, 86, 0.8)", "rgba(255, 235, 59, 0.8)"]
                }
            }
            
            print(f"DEBUG: Returning {len(enhanced_charts['charts'])} charts")
            return jsonify(enhanced_charts)
        
        print(f"DEBUG: No chart data found in cache")
        return jsonify({"error": "Chart data not available. Please fetch prospect health data first."}), 400
    except Exception as e:
        print(f"DEBUG: Exception in get_enhanced_charts: {str(e)}")
        return jsonify({"error": str(e)}), 500

@database_health_bp.route("/debug-cache", methods=["GET"])
@require_auth
def debug_cache():
    """Debug endpoint to check cache contents"""
    try:
        cache_key = f"prospect_health:{g.access_token[:20]}"
        cached_data = get_cached_data(cache_key)
        
        debug_info = {
            "cache_key": cache_key,
            "data_available": cached_data is not None,
            "data_keys": list(cached_data.keys()) if cached_data else [],
            "chart_data_available": 'chart_data' in cached_data if cached_data else False,
            "chart_data_type": str(type(cached_data.get('chart_data'))) if cached_data else None,
            "chart_data_length": len(cached_data.get('chart_data', [])) if cached_data and 'chart_data' in cached_data else 0
        }
        
        if cached_data and 'chart_data' in cached_data:
            chart_data = cached_data['chart_data']
            if isinstance(chart_data, list):
                debug_info['chart_titles'] = [chart.get('title', 'No title') for chart in chart_data]
            elif isinstance(chart_data, dict):
                debug_info['chart_keys'] = list(chart_data.keys())
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500