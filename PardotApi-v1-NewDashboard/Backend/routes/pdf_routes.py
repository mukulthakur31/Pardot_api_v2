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

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route("/download-pdf", methods=["POST"])
@require_auth
def download_pdf():
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
            
            # Get filters if provided
            if filters:
                print(f"[PDF] Re-fetching data with filters: {filters}")
                data = get_database_health_stats(g.access_token, 
                                                filters.get("filter_type"), 
                                                filters.get("start_date"), 
                                                filters.get("end_date"))
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
            
            # Get filters if provided
            if filters:
                print(f"[PDF] Re-fetching data with filters: {filters}")
                data = get_database_health_stats(g.access_token, 
                                                filters.get("filter_type"), 
                                                filters.get("start_date"), 
                                                filters.get("end_date"))
            buffer = create_prospect_health_comprehensive_pdf(data, sections)
            filename = "prospect_health_comprehensive_report.pdf"
        else:
            return jsonify({"error": "Invalid data type"}), 400
        
        # Clear timeout
        timeout_occurred.set()
        
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
    try:
        print("🚀 Starting comprehensive PDF generation...")
        
        # Add request timeout protection (Windows compatible)
        import threading
        import time
        
        timeout_occurred = threading.Event()
        
        def timeout_checker():
            if timeout_occurred.wait(600):  # 10 minutes
                return
            raise TimeoutError("PDF generation timed out")
        
        timeout_thread = threading.Thread(target=timeout_checker, daemon=True)
        timeout_thread.start()
        
        # Fetch all data with timeout protection
        email_stats = None
        form_stats = None
        prospect_health = None
        landing_page_stats = None
        engagement_programs = None
        utm_analysis = None
        database_health = None
        
        try:
            print("Fetching email stats...")
            email_stats = get_email_stats(g.access_token)
            print(f"✅ Email stats: {len(email_stats) if email_stats else 0} campaigns")
        except Exception as e:
            print(f"❌ Email stats failed: {str(e)}")
        
        try:
            print("Fetching form stats...")
            form_stats = get_form_stats(g.access_token)
            print(f"✅ Form stats: {len(form_stats) if form_stats else 0} forms")
        except Exception as e:
            print(f"❌ Form stats failed: {str(e)}")
        
        try:
            print("Fetching database health stats...")
            database_health = get_database_health_stats(g.access_token)
            print("✅ Database health fetched")
        except Exception as e:
            print(f"❌ Database health failed: {str(e)}")
            try:
                print("Trying prospect health fallback...")
                prospect_health = get_prospect_health(g.access_token)
                print("✅ Prospect health fetched")
            except Exception as e2:
                print(f"❌ Prospect health failed: {str(e2)}")
        
        try:
            print("Fetching landing page stats...")
            landing_page_stats = get_landing_page_stats(g.access_token)
            print("✅ Landing page stats fetched")
        except Exception as e:
            print(f"❌ Landing page stats failed: {str(e)}")
        
        try:
            print("Fetching engagement programs...")
            engagement_programs = get_engagement_programs_analysis(g.access_token)
            print("✅ Engagement programs fetched")
        except Exception as e:
            print(f"❌ Engagement programs failed: {str(e)}")
        
        try:
            print("Fetching UTM analysis...")
            utm_analysis = get_utm_analysis(g.access_token)
            print("✅ UTM analysis fetched")
        except Exception as e:
            print(f"❌ UTM analysis failed: {str(e)}")
        
        print("🔄 Generating comprehensive PDF...")
        buffer = create_comprehensive_audit_pdf(
            email_stats, 
            form_stats, 
            prospect_health, 
            landing_page_stats,
            engagement_programs,
            utm_analysis,
            database_health
        )
        
        print("✅ PDF generated successfully")
        
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
        
        # Fetch prospect health data with filters
        prospect_health_data = get_database_health_stats(g.access_token, filter_type, start_date, end_date)
        
        # Create PDF with selected sections and filtered data
        buffer = create_prospect_health_comprehensive_pdf(prospect_health_data, sections)
        
        return send_file(buffer, as_attachment=True, download_name="prospect_health_report.pdf", mimetype="application/pdf")
    except Exception as e:
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