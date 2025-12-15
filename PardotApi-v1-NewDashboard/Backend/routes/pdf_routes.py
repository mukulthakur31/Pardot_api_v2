from flask import Blueprint, request, jsonify, send_file, g
from services.pdf_service import (
    create_professional_pdf_report, create_form_pdf_report, 
    create_landing_page_pdf_report, create_engagement_pdf_report, 
    create_utm_pdf_report, create_comprehensive_summary_pdf,
    create_prospect_health_comprehensive_pdf
)
from services.comprehensive_pdf import create_comprehensive_audit_pdf
from services.email_service import get_email_stats
from services.form_service import get_form_stats
from services.prospect_service import get_prospect_health
from services.Landing_page_service import get_landing_page_stats
from services.engagement_service import get_engagement_programs_analysis
from services.utm_service import get_utm_analysis
from services.database_health_service import get_database_health_stats
from middleware.auth_middleware import require_auth
from cache import get_cached_data, set_cached_data
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

pdf_bp = Blueprint('pdf', __name__)


def fetch_email_stats(token):
    email_cache_key = f"emails:{token[:20]}:all::"
    data = get_cached_data(email_cache_key)
    if data:
        print("📦 EMAIL from cache")
        return data

    print("🌐 EMAIL from API")
    data = get_email_stats(token)
    if data:
        set_cached_data(email_cache_key, data, ttl=1800)
    return data


def fetch_form_stats(token):
    form_cache_key = f"forms:{token[:20]}:all::"
    data = get_cached_data(form_cache_key)
    if data:
        print("📦 FORM from cache")
        return data

    print("🌐 FORM from API")
    data = get_form_stats(token)
    if data:
        set_cached_data(form_cache_key, data, ttl=1800)
    return data


def fetch_database_health(token):
    db_health_cache_key = f"database_health:{token[:20]}:all::"
    data = get_cached_data(db_health_cache_key)
    if data:
        print("📦 DATABASE HEALTH from cache")
        return data

    print("🌐 DATABASE HEALTH from API")
    data = get_database_health_stats(token)
    if data:
        set_cached_data(db_health_cache_key, data, ttl=3600)
    return data


def fetch_landing_page_stats(token):
    lp_cache_key = f"landing_pages:{token[:20]}:all::"
    data = get_cached_data(lp_cache_key)
    if data:
        print("📦 LANDING PAGE from cache")
        return data

    print("🌐 LANDING PAGE from API")
    data = get_landing_page_stats(token)
    if data:
        set_cached_data(lp_cache_key, data, ttl=1800)
    return data

def fetch_engagement_programs(token):
    engagement_cache_key = f"engagement_programs:{token[:20]}"
    data = get_cached_data(engagement_cache_key)
    if data:
        print("📦 ENGAGEMENT from cache")
        return data

    print("🌐 ENGAGEMENT from API")
    data = get_engagement_programs_analysis(token)
    if data:
        set_cached_data(engagement_cache_key, data, ttl=1800)
    return data


def fetch_utm_analysis(token):
    utm_cache_key = f"utm_analysis:{token[:20]}"
    data = get_cached_data(utm_cache_key)
    if data:
        print("📦 UTM from cache")
        return data

    print("🌐 UTM from API")
    data = get_utm_analysis(token)
    if data:
        set_cached_data(utm_cache_key, data, ttl=1800)
    return data


def fetch_prospect_health(token):
    prospect_cache_key = f"prospect_health:{token[:20]}:all::"
    data = get_cached_data(prospect_cache_key)
    if data:
        print("📦 PROSPECT HEALTH from cache")
        return data

    print("🌐 PROSPECT HEALTH from API")
    data = get_prospect_health(token)
    if data:
        set_cached_data(prospect_cache_key, data, ttl=3600)
    return data


@pdf_bp.route("/download-pdf", methods=["POST"])
@require_auth
def download_pdf():
    start_time = time.time()
    try:
        print(f"📄 [PDF] Starting PDF generation...")
        print(f"[PDF] Full Request JSON: {request.json}")
        
        # Add timeout protection (Windows compatible)
        import threading
        
        timeout_occurred = threading.Event()
        
        def timeout_checker():
            if timeout_occurred.wait(300):  # 5 minutes
                return
            raise TimeoutError("PDF generation timed out")
        
        timeout_thread = threading.Thread(target=timeout_checker, daemon=True)
        timeout_thread.start()
        data_type = request.json.get("data_type", "emails")
        data = request.json.get("data")
        filters = request.json.get("filters", {})
        sections = request.json.get("sections", {})
        
        print(f"[PDF] Data Type: {data_type}")
        print(f"[PDF] Data Available: {data is not None}")
        print(f"[PDF] Filters: {filters}")
        print(f"[PDF] Sections: {sections}")
        print(f"[PDF] Sections Type: {type(sections)}")
        print(f"[PDF] Sections Keys: {list(sections.keys()) if isinstance(sections, dict) else 'Not a dict'}")
        
        if not data:
            print("No data provided")
            return jsonify({"error": "No data provided"}), 400
        
        if data_type == "emails":
            filters = request.json.get("filters", {})
            day = filters.get("day")
            month = filters.get("month")
            year = filters.get("year")
            buffer = create_professional_pdf_report(data, day, month, year)
            filename = "email_campaign_report.pdf"
        elif data_type == "forms":
            buffer = create_form_pdf_report(data)
            filename = "form_stats_report.pdf"
        elif data_type == "prospects":
            # Use sections from modal or default to all enabled
            default_sections = {
                "active_contacts": True,
                "inactive_contacts": True,
                "empty_details": True,
                "scoring_issues": True,
                "charts": True,
                "recommendations": True
            }
            sections = request.json.get("sections", default_sections)
            print(f"[PDF] Using sections for prospects: {sections}")
            
            # Get filters if provided - Check cache first
            if filters:
                filter_type = filters.get("filter_type")
                start_date = filters.get("start_date")
                end_date = filters.get("end_date")
                filtered_cache_key = f"database_health:{g.access_token[:20]}:{filter_type or 'all'}:{start_date or ''}:{end_date or ''}"
                
                data = get_cached_data(filtered_cache_key)
                if data:
                    print(f"📦 FILTERED DATABASE HEALTH: Retrieved from CACHE for PDF - Key: {filtered_cache_key}")
                else:
                    print(f"🌐 FILTERED DATABASE HEALTH: Fetching from API for PDF - Key: {filtered_cache_key}")
                    data = get_database_health_stats(g.access_token, filter_type, start_date, end_date)
                    if data:
                        set_cached_data(filtered_cache_key, data, ttl=3600)
            buffer = create_prospect_health_comprehensive_pdf(data, sections)
            filename = "prospect_health_comprehensive_report.pdf"
        elif data_type == "landing_pages":
            buffer = create_landing_page_pdf_report(data)
            filename = "landing_pages_report.pdf"
        elif data_type == "engagement" or data_type == "engagement_programs":
            buffer = create_engagement_pdf_report(data)
            filename = "engagement_programs_report.pdf"
        elif data_type == "utm" or data_type == "utm_analysis":
            buffer = create_utm_pdf_report(data)
            filename = "utm_analysis_report.pdf"
        elif data_type == "database_health":
            # Use sections from modal or default to all enabled
            default_sections = {
                "active_contacts": True,
                "inactive_contacts": True,
                "empty_details": True,
                "scoring_issues": True,
                "charts": True,
                "recommendations": True
            }
            sections = request.json.get("sections", default_sections)
            print(f"[PDF] Using sections for database_health: {sections}")
            
            # Get filters if provided - Check cache first
            if filters:
                filter_type = filters.get("filter_type")
                start_date = filters.get("start_date")
                end_date = filters.get("end_date")
                filtered_cache_key = f"prospect_health:{g.access_token[:20]}:{filter_type or 'all'}:{start_date or ''}:{end_date or ''}"
                
                data = get_cached_data(filtered_cache_key)
                if data:
                    print(f"📦 FILTERED PROSPECT HEALTH: Retrieved from CACHE for PDF - Key: {filtered_cache_key}")
                else:
                    print(f"🌐 FILTERED PROSPECT HEALTH: Fetching from API for PDF - Key: {filtered_cache_key}")
                    data = get_database_health_stats(g.access_token, filter_type, start_date, end_date)
                    if data:
                        set_cached_data(filtered_cache_key, data, ttl=3600)
            buffer = create_prospect_health_comprehensive_pdf(data, sections)
            filename = "prospect_health_comprehensive_report.pdf"
        else:
            return jsonify({"error": "Invalid data type"}), 400
        
        # Clear timeout
        timeout_occurred.set()
        
        total_time = time.time() - start_time
        print(f"⏱️ PDF Generated in {total_time:.2f} seconds")
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")
    except TimeoutError as e:
        print(f"⏰ [ERROR] PDF Generation Timeout: {str(e)}")
        timeout_occurred.set()
        return jsonify({"error": "PDF generation timed out. Please try again."}), 408
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ [ERROR] PDF Generation Failed: {str(e)}")
        print(f"[ERROR] Full traceback: {error_details}")
        timeout_occurred.set()
        return jsonify({"error": str(e), "details": error_details}), 500

@pdf_bp.route("/download-summary-pdf", methods=["POST"])
@require_auth
def download_summary_pdf():
    start_time = time.time()
    try:
        print("🚀 Starting comprehensive PDF generation...")
        
        # Add request timeout protection (Windows compatible)
        import threading
        
        timeout_occurred = threading.Event()
        
        def timeout_checker():
            if timeout_occurred.wait(600):  # 10 minutes
                return
            raise TimeoutError("PDF generation timed out")
        
        timeout_thread = threading.Thread(target=timeout_checker, daemon=True)
        timeout_thread.start()
        
        # Fetch all data with timeout protection - Check cache first for each module
        results = {
            "email_stats": None,
            "form_stats": None,
            "prospect_health": None,
            "landing_page_stats": None,
            "engagement_programs": None
        }

        token = g.access_token

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(fetch_email_stats, token): "email_stats",
                executor.submit(fetch_form_stats, token): "form_stats",
                executor.submit(fetch_prospect_health, token): "prospect_health",
                executor.submit(fetch_landing_page_stats, token): "landing_page_stats",
                executor.submit(fetch_engagement_programs, token): "engagement_programs"
            }

            print("🔄 Generating comprehensive PDF...")
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                    print(f"✅ {key} fetched")
                except Exception as e:
                    print(f"❌ {key} failed: {str(e)}")
                    results[key] = None

        buffer = create_comprehensive_audit_pdf(
            results["email_stats"],
            results["form_stats"],
            results["prospect_health"],
            results["landing_page_stats"],
            results["engagement_programs"]
        )
        
        total_time = time.time() - start_time
        print(f"⏱️ Comprehensive PDF Generated in {total_time:.2f} seconds")
        
        # Clear timeout
        timeout_occurred.set()
        
        return send_file(buffer, as_attachment=True, download_name="pardot_comprehensive_report.pdf", mimetype="application/pdf")
    except TimeoutError as e:
        print(f"⏰ PDF Generation Timeout: {str(e)}")
        timeout_occurred.set()
        return jsonify({"error": "PDF generation timed out. Please try again with a smaller date range."}), 408
    except Exception as e:
        import traceback
        print(f"❌ PDF Generation Error: {str(e)}")
        print(traceback.format_exc())
        timeout_occurred.set()
        return jsonify({"error": str(e)}), 500

@pdf_bp.route("/download-prospect-health-pdf", methods=["POST"])
@require_auth
def download_prospect_health_pdf():
    start_time = time.time()
    try:
        # Get selected sections from request
        sections = request.json.get("sections", {
            "active_contacts": True,
            "inactive_contacts": True,
            "empty_details": True,
            "scoring_issues": True,
            "charts": True,
            "recommendations": True
        })
        
        # Get filter parameters from request
        filters = request.json.get("filters", {})
        filter_type = filters.get("filter_type")
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        
        # Fetch prospect health data with filters - Check cache first
        cache_key = f"prospect_health:{g.access_token[:20]}:{filter_type or 'all'}:{start_date or ''}:{end_date or ''}"
        prospect_health_data = get_cached_data(cache_key)
        
        if prospect_health_data:
            print(f"📦 PROSPECT HEALTH PDF: Retrieved from CACHE - Key: {cache_key}")
        else:
            print(f"🌐 PROSPECT HEALTH PDF: Fetching from API - Key: {cache_key}")
            prospect_health_data = get_database_health_stats(g.access_token, filter_type, start_date, end_date)
            if prospect_health_data:
                set_cached_data(cache_key, prospect_health_data, ttl=3600)
                print(f"💾 PROSPECT HEALTH PDF: Cached for 1 hour - Key: {cache_key}")
        
        # Create PDF with selected sections and filtered data
        buffer = create_prospect_health_comprehensive_pdf(prospect_health_data, sections)
        
        total_time = time.time() - start_time
        print(f"⏱️ Prospect Health PDF Generated in {total_time:.2f} seconds")
        return send_file(buffer, as_attachment=True, download_name="prospect_health_report.pdf", mimetype="application/pdf")
    except Exception as e:
        total_time = time.time() - start_time
        print(f"❌ PDF Failed after {total_time:.2f} seconds: {str(e)}")
        return jsonify({"error": str(e)}), 500

@pdf_bp.route("/get-pdf-modal-options/<data_type>", methods=["GET"])
@require_auth
def get_pdf_modal_options(data_type):
    """Get PDF modal options for different data types"""
    try:
        if data_type in ["prospects", "database_health"]:
            # Return comprehensive modal options for prospect health
            modal_options = {
                "title": "Customize Your Prospect Health PDF Report",
                "description": "Select which sections and metrics to include in your comprehensive report:",
                "sections": [
                    {
                        "id": "active_contacts",
                        "label": "Active Contacts Analysis",
                        "description": "Engagement metrics and activity data",
                        "enabled": True,
                        "default": True
                    },
                    {
                        "id": "inactive_contacts",
                        "label": "Inactive Contacts Analysis",
                        "description": "Unsubscribed leads and inactive periods",
                        "enabled": True,
                        "default": True
                    },
                    {
                        "id": "empty_details",
                        "label": "Data Quality & Issues",
                        "description": "Empty fields, duplicates, and data quality issues",
                        "enabled": True,
                        "default": True
                    },
                    {
                        "id": "scoring_issues",
                        "label": "Lead Scoring Issues",
                        "description": "Scoring problems and grade inconsistencies",
                        "enabled": True,
                        "default": True
                    },
                    {
                        "id": "charts",
                        "label": "Charts & Visualizations",
                        "description": "Trend charts and visual analytics",
                        "enabled": True,
                        "default": True
                    },
                    {
                        "id": "recommendations",
                        "label": "Strategic Recommendations",
                        "description": "Actionable insights and optimization suggestions",
                        "enabled": True,
                        "default": True
                    }
                ],
                "export_options": {
                    "include_summary": {"label": "Executive Summary", "default": True},
                    "include_methodology": {"label": "Methodology Notes", "default": False},
                    "page_breaks": {"label": "Page Breaks Between Sections", "default": True}
                }
            }
            return jsonify(modal_options)
        else:
            # For other data types, return simple options
            return jsonify({
                "title": f"Export {data_type.title()} Report",
                "description": "Generate PDF report with current data",
                "sections": [],
                "export_options": {
                    "include_summary": {"label": "Include Summary", "default": True}
                }
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500