from flask import Blueprint, request, jsonify, send_file, g
from services.pdf_service import (
    create_professional_pdf_report, create_form_pdf_report, 
    create_prospect_pdf_report, create_landing_page_pdf_report, 
    create_engagement_pdf_report, create_utm_pdf_report, create_comprehensive_summary_pdf
)
from services.email_service import get_email_stats
from services.form_service import get_form_stats
from services.prospect_service import get_prospect_health
from services.Landing_page_service import get_landing_page_stats
from services.engagement_service import get_engagement_programs_analysis
from services.utm_service import get_utm_analysis
from middleware.auth_middleware import require_auth

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route("/download-pdf", methods=["POST"])
def download_pdf():
    try:
        print(f"Request JSON: {request.json}")
        data_type = request.json.get("data_type", "emails")
        data = request.json.get("data")
        print(f"Data type: {data_type}, Data: {type(data)}")
        
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
            buffer = create_prospect_pdf_report(data)
            filename = "prospect_health_report.pdf"
        elif data_type == "landing_pages":
            buffer = create_landing_page_pdf_report(data)
            filename = "landing_pages_report.pdf"
        elif data_type == "engagement" or data_type == "engagement_programs":
            buffer = create_engagement_pdf_report(data)
            filename = "engagement_programs_report.pdf"
        elif data_type == "utm" or data_type == "utm_analysis":
            buffer = create_utm_pdf_report(data)
            filename = "utm_analysis_report.pdf"
        else:
            return jsonify({"error": "Invalid data type"}), 400
        
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pdf_bp.route("/download-summary-pdf", methods=["POST"])
@require_auth
def download_summary_pdf():
    
    try:
        email_stats = get_email_stats(g.access_token)
        form_stats = get_form_stats(g.access_token)
        prospect_health = get_prospect_health(g.access_token)
        landing_page_stats = get_landing_page_stats(g.access_token)
        
        engagement_programs = None
        utm_analysis = None
        
        try:
            engagement_programs = get_engagement_programs_analysis(g.access_token)
        except Exception as e:
            print(f"Error fetching engagement programs: {str(e)}")
        
        try:
            utm_analysis = get_utm_analysis(g.access_token)
        except Exception as e:
            print(f"Error fetching Campaign and UTM analysis: {str(e)}")
        
        buffer = create_comprehensive_summary_pdf(
            email_stats, 
            form_stats, 
            prospect_health, 
            landing_page_stats,
            engagement_programs,
            utm_analysis
        )
        
        return send_file(buffer, as_attachment=True, download_name="pardot_comprehensive_report.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500