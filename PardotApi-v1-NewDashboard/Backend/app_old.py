from flask import Flask, redirect, request, jsonify, send_file, session
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import os
load_dotenv()

# Import configuration
from config.settings import REDIRECT_URI, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SECRET_KEY,CLIENT_ID,CLIENT_SECRET,BUSINESS_UNIT_ID

# Import services
from services.email_service import get_email_stats
from services.form_service import get_form_stats, get_active_inactive_forms, get_form_abandonment_analysis, get_active_inactive_forms_from_cache, get_form_abandonment_analysis_from_cache
from services.Landing_page_service import get_landing_page_stats, get_filtered_landing_page_stats
from services.prospect_service import get_prospect_health, fetch_all_prospects, find_duplicate_prospects, find_inactive_prospects, find_missing_critical_fields, find_scoring_inconsistencies, get_filtered_prospects
from services.engagement_service import get_engagement_programs_analysis, get_engagement_programs_performance
from services.pdf_service import create_professional_pdf_report, create_form_pdf_report, create_prospect_pdf_report, create_comprehensive_summary_pdf
from services.utm_service import get_utm_analysis, get_campaign_engagement_analysis


# Import Google integration
from google_integration import GoogleIntegration

# Initialize data cache
data_cache = {'forms': {}, 'landing_pages': {}, 'prospects': {}, 'engagement': {}}

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Security: Configure CORS properly for production
CORS(app, 
     origins=["http://localhost:5173"], 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


# Google Integration
google_integration = GoogleIntegration(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)

@app.route("/login")
def login():
    try:
        auth_url = (
            "https://login.salesforce.com/services/oauth2/authorize"
            f"?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
            "&scope=api%20pardot_api%20full%20refresh_token"
        )
        return redirect(auth_url)
    except Exception:
        return jsonify({"error": "Please setup credentials first"}), 400

@app.route("/callback")
def callback():
    auth_code = request.args.get("code")
    if not auth_code:
        return jsonify({"error": "No code received"}), 400

    try:
     
        client_secret = CLIENT_SECRET
        if not client_secret:
            return jsonify({"error": "OAuth session expired"}), 400
            
        token_response = requests.post("https://login.salesforce.com/services/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": CLIENT_ID,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI
        })
        

        if token_response.status_code != 200:
            return jsonify({"error": token_response.text}), 500

        access_token = token_response.json().get("access_token")
        # Store token securely in session instead of URL
        session['access_token'] = access_token
        return redirect("http://localhost:5173/dashboard")
    except Exception:
        return jsonify({"error": "No credentials found"}), 400

@app.route("/get-token", methods=["GET"])
def get_token():
    """Secure endpoint to get access token from session"""
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "No access token found"}), 401
    
    print(access_token)
    return jsonify({"token": access_token})

@app.route("/validate-token", methods=["GET"])
def validate_token():
    """Validate if current token is still valid"""
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"valid": False, "error": "No token provided"}), 401
    
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Pardot-Business-Unit-Id": BUSINESS_UNIT_ID
        }
        
        # Test token with a simple API call
        response = requests.get(
            "https://pi.pardot.com/api/v5/objects/prospects",
            headers=headers,
            params={"fields": "id", "limit": 1}
        )
        
        if response.status_code == 401:
            return jsonify({"valid": False, "error": "Token expired"}), 401
        elif response.status_code == 200:
            return jsonify({"valid": True})
        else:
            return jsonify({"valid": False, "error": "Token validation failed"}), 400
            
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

# ===== Email Routes =====
@app.route("/get-email-stats", methods=["GET"])
def get_email_stats_route():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is required"}), 401

    try:
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        stats_list = get_email_stats(access_token, filter_type, start_date, end_date)
        return jsonify(stats_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== Form Routes =====
@app.route("/get-form-stats", methods=["GET"])
def get_form_stats_route():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is required"}), 401
    
    try:
        # Get date filters from query parameters
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        # Convert filter type to date range if provided
        if filter_type and not start_date and not end_date:
            from services.form_service import get_date_range_from_filter
            start_date, end_date = get_date_range_from_filter(filter_type)
        
        form_stats = get_form_stats(access_token, start_date, end_date)
        # Cache form stats for other form routes
        data_cache['forms'][access_token] = form_stats
        return jsonify(form_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-active-inactive-forms", methods=["GET"])
def get_active_inactive_forms_route():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is required"}), 401
    
    try:
        # Check cache first
        cached_forms = data_cache['forms'].get(access_token)
        if cached_forms:
            forms_data = get_active_inactive_forms_from_cache(cached_forms)
        else:
            forms_data = get_active_inactive_forms(access_token)
        return jsonify(forms_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-form-abandonment-analysis", methods=["GET"])
def get_form_abandonment_analysis_route():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is required"}), 401
    
    try:
        # Get date filters from query parameters
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        # Convert filter type to date range if provided
        if filter_type and not start_date and not end_date:
            from services.form_service import get_date_range_from_filter
            start_date, end_date = get_date_range_from_filter(filter_type)
        
        # Check cache first
        cached_forms = data_cache['forms'].get(access_token)
        if cached_forms and not (start_date or end_date):
            abandonment_data = get_form_abandonment_analysis_from_cache(cached_forms)
        else:
            abandonment_data = get_form_abandonment_analysis(access_token, start_date, end_date)
        return jsonify(abandonment_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-filtered-form-stats", methods=["GET"])
def get_filtered_form_stats_route():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is required"}), 401
    
    try:
        # Get date filters from query parameters
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        
        if filter_type and not start_date and not end_date:
            from services.form_service import get_date_range_from_filter
            start_date, end_date = get_date_range_from_filter(filter_type)
        
       
        filtered_stats = get_form_stats(access_token, start_date, end_date)
        return jsonify(filtered_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get-landing-page-stats", methods=["GET"])
def get_landing_page_stats_route():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is required"}), 401
    
    try:
       
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
     
        if filter_type and not start_date and not end_date:
            from services.Landing_page_service import get_date_range_from_filter
            start_date, end_date = get_date_range_from_filter(filter_type)
        
        landing_page_stats = get_landing_page_stats(access_token, start_date, end_date)
       
        data_cache['landing_pages'][access_token] = landing_page_stats
        return jsonify(landing_page_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-filtered-landing-page-stats", methods=["GET"])
def get_filtered_landing_page_stats_route():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is required"}), 401
    
    try:
        
        filter_type = request.args.get("filter_type")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        filtered_stats = get_filtered_landing_page_stats(access_token, filter_type, start_date, end_date)
        return jsonify(filtered_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-landing-page-field-issues", methods=["GET"])
def get_landing_page_field_issues():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is required"}), 401
    
    try:
        severity = request.args.get("severity", "all").lower()
        issue_type = request.args.get("type", "all").lower()
        
        # Check cache first
        cached_stats = data_cache['landing_pages'].get(access_token)
        if cached_stats:
            landing_page_stats = cached_stats
        else:
            landing_page_stats = get_landing_page_stats(access_token)
            data_cache['landing_pages'][access_token] = landing_page_stats
            
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


# ===== Prospect Routes =====
@app.route("/get-prospect-health", methods=["GET"])
def get_prospect_health_route():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token required"}), 401
    
    try:
        health_data = get_prospect_health(access_token)
        # Cache the data in memory using access token as key
        data_cache['prospects'][access_token] = health_data
        return jsonify(health_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-inactive-prospects", methods=["GET"])
def get_inactive_prospects():
    access_token = session.get('access_token')
    try:
        # Use cached data from memory if available
        cached_health = data_cache['prospects'].get(access_token)
        if cached_health and 'all_prospects' in cached_health:
            prospects = cached_health['all_prospects']
            inactive_prospects = find_inactive_prospects(prospects)
            
            return jsonify({
                "total_inactive": len(inactive_prospects),
                "inactive_prospects": inactive_prospects
            })
        else:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-duplicate-prospects", methods=["GET"])
def get_duplicate_prospects():
    access_token = session.get('access_token')
    try:
        # Use cached data from memory if available
        cached_health = data_cache['prospects'].get(access_token)
        if cached_health and 'all_prospects' in cached_health:
            prospects = cached_health['all_prospects']
            duplicates = find_duplicate_prospects(prospects)
            
            return jsonify({
                "total_duplicate_groups": len(duplicates),
                "duplicate_prospects": duplicates
            })
        else:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-missing-fields-prospects", methods=["GET"])
def get_missing_fields_prospects():
    access_token = session.get('access_token')
    try:
        # Use cached data from memory if available
        cached_health = data_cache['prospects'].get(access_token)
        if cached_health and 'all_prospects' in cached_health:
            prospects = cached_health['all_prospects']
            missing_fields = find_missing_critical_fields(prospects)
            
            return jsonify({
                "total_with_missing_fields": len(missing_fields),
                "prospects_missing_fields": missing_fields
            })
        else:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/filter-prospects", methods=["POST"])
def filter_prospects_route():
    try:
        filters = request.json or {}
        print(f"[DEBUG] Received filters: {filters}")
        
        # Get the first (and likely only) cached prospect data
        if not data_cache['prospects']:
            return jsonify({"error": "Please run prospect health analysis first"}), 400
        
        # Use the first available cached data
        cached_key = list(data_cache['prospects'].keys())[0]
        cached_health = data_cache['prospects'][cached_key]
        
        if 'all_prospects' not in cached_health:
            print(f"[DEBUG] Cached data keys: {list(cached_health.keys())}")
            return jsonify({"error": "Cached data missing all_prospects"}), 400
        
        prospects = cached_health['all_prospects']
        print(f"[DEBUG] Found {len(prospects)} cached prospects")
        
        # Apply simple client-side filtering
        filtered_prospects = apply_simple_filters(prospects, filters)
        
        return jsonify({
            "total_prospects": len(prospects),
            "filtered_count": len(filtered_prospects),
            "prospects": filtered_prospects,
            "filters_applied": filters
        })
    except Exception as e:
        print(f"[DEBUG] Filter error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def apply_simple_filters(prospects, filters):
    """Apply basic filters to prospect data"""
    filtered = prospects.copy()
    
    # View filters
    view = filters.get('view', 'All Prospects')
    if view == 'Active Prospects':
        filtered = [p for p in filtered if p.get('lastActivityAt')]
    elif view == 'Never Active Prospects':
        filtered = [p for p in filtered if not p.get('lastActivityAt')]
    elif view == 'Active Prospects For Review':
        filtered = [p for p in filtered if p.get('lastActivityAt') and not p.get('isReviewed')]
    elif view == 'Assigned Prospects':
        filtered = [p for p in filtered if p.get('assignedTo')]
    elif view == 'Mailable Prospects':
        filtered = [p for p in filtered if not p.get('isDoNotEmail', False) and p.get('email')]
    elif view == 'My Prospects':
        filtered = [p for p in filtered if p.get('assignedTo') == 'current_user']
    elif view == 'My Starred Prospects':
        filtered = [p for p in filtered if p.get('isStarred')]
    elif view == 'Prospects Not In Salesforce':
        filtered = [p for p in filtered if not p.get('salesforceId')]
    elif view == 'Reviewed Prospects':
        filtered = [p for p in filtered if p.get('isReviewed')]
    elif view == 'Unassigned Prospects':
        filtered = [p for p in filtered if not p.get('assignedTo')]
    elif view == 'Unmailable Prospects':
        filtered = [p for p in filtered if p.get('isDoNotEmail', False)]
    elif view == 'Unsubscribed Prospects':
        filtered = [p for p in filtered if p.get('optedOut', False)]
    elif view == 'Paused Prospects':
        filtered = [p for p in filtered if p.get('isPaused', False)]
    elif view == 'Undelivered Prospects':
        filtered = [p for p in filtered if p.get('isEmailHardBounced', False)]
    
    # Time filters
    time_filter = filters.get('time', 'All Time')
    if time_filter != 'All Time':
        from datetime import datetime, timedelta
        now = datetime.now()
        activity_field = 'lastActivityAt' if filters.get('activity') == 'Last Activity' else 'createdAt'
        
        start_date = None
        end_date = None
        
        if time_filter == 'Today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif time_filter == 'Yesterday':
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif time_filter == 'This Quarter':
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif time_filter == 'This Month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif time_filter == 'This Year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif time_filter == 'Last 7 Days':
            start_date = now - timedelta(days=7)
            end_date = now
        elif time_filter == 'Last Week':
            days_since_monday = now.weekday()
            last_monday = now - timedelta(days=days_since_monday + 7)
            start_date = last_monday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = last_monday + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif time_filter == 'Last Month':
            if now.month == 1:
                start_date = now.replace(year=now.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
            else:
                start_date = now.replace(month=now.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(microseconds=1)
        elif time_filter == 'Last Quarter':
            current_quarter = (now.month - 1) // 3 + 1
            if current_quarter == 1:
                start_date = now.replace(year=now.year-1, month=10, day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(year=now.year-1, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
            else:
                last_quarter_start_month = (current_quarter - 2) * 3 + 1
                last_quarter_end_month = (current_quarter - 1) * 3
                start_date = now.replace(month=last_quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
                if last_quarter_end_month in [1, 3, 5, 7, 8, 10, 12]:
                    last_day = 31
                elif last_quarter_end_month in [4, 6, 9, 11]:
                    last_day = 30
                else:
                    last_day = 29 if now.year % 4 == 0 and (now.year % 100 != 0 or now.year % 400 == 0) else 28
                end_date = now.replace(month=last_quarter_end_month, day=last_day, hour=23, minute=59, second=59, microsecond=999999)
        elif time_filter == 'Last Year':
            start_date = now.replace(year=now.year-1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(year=now.year-1, month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        
        if start_date:
            time_filtered = []
            for p in filtered:
                date_val = p.get(activity_field)
                if date_val:
                    try:
                        if 'T' in str(date_val):
                            prospect_date = datetime.fromisoformat(str(date_val).replace('Z', '+00:00'))
                        else:
                            prospect_date = datetime.strptime(str(date_val)[:10], '%Y-%m-%d')
                        
                        prospect_date = prospect_date.replace(tzinfo=None)
                        if end_date:
                            if start_date <= prospect_date <= end_date:
                                time_filtered.append(p)
                        else:
                            if prospect_date >= start_date:
                                time_filtered.append(p)
                    except:
                        continue
            filtered = time_filtered
    
    print(f"[DEBUG] Filtered to {len(filtered)} prospects")
    return filtered

# ===== Engagement Programs Routes =====
@app.route("/get-engagement-programs-analysis", methods=["GET"])
def get_engagement_programs_analysis_route():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token required"}), 401
    
    try:
        analysis_data = get_engagement_programs_analysis(access_token)
        # Cache engagement data
        data_cache['engagement'][access_token] = analysis_data
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-engagement-programs-performance", methods=["GET"])
def get_engagement_programs_performance_route():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token required"}), 401
    
    try:
        # Check cache first
        cached_data = data_cache['engagement'].get(access_token)
        if cached_data:
            # Use cached data to generate performance metrics
            performance_data = cached_data
        else:
            performance_data = get_engagement_programs_performance(access_token)
        return jsonify(performance_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== PDF Routes =====
@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    try:
        data_type = request.json.get("data_type", "emails")
        data = request.json.get("data")
        
        if not data:
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
        else:
            return jsonify({"error": "Invalid data type"}), 400
        
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download-summary-pdf", methods=["POST"])
def download_summary_pdf():
    """Generate comprehensive summary PDF with all data sections"""
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token is required"}), 401
    
    try:
        # Fetch all available data sections
        email_stats = get_email_stats(access_token)
        form_stats = get_form_stats(access_token)
        prospect_health = get_prospect_health(access_token)
        landing_page_stats = get_landing_page_stats(access_token)
        
        # Fetch additional sections
        engagement_programs = None
        utm_analysis = None
        
        try:
            engagement_programs = get_engagement_programs_analysis(access_token)
        except Exception as e:
            print(f"Error fetching engagement programs: {str(e)}")
        
        try:
            utm_analysis = get_utm_analysis(access_token)
        except Exception as e:
            print(f"Error fetching Campaign and UTM analysis: {str(e)}")
        
        # Generate comprehensive PDF with all sections
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

# ===== Google Integration Routes =====
@app.route("/google-auth", methods=["GET"])
def google_auth():
    try:
        token = request.headers.get("Authorization")
        if token:
            session['pardot_token'] = token
        
        auth_url, flow = google_integration.get_auth_url()
        return jsonify({"auth_url": auth_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/google-callback")
def google_callback():
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({"error": "No code received"}), 400
        
        _, flow = google_integration.get_auth_url()
        credentials = google_integration.get_credentials(code, flow)
        session['google_credentials'] = credentials.to_json()
        
        stored_token = session.get('pardot_token', '')
        redirect_url = 'http://localhost:5173/dashboard?google_auth=success'
        if stored_token:
            clean_token = stored_token.replace("Bearer ", "").replace("bearer ", "")
            redirect_url += f'&token={clean_token}'
        return redirect(redirect_url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/export-to-sheets", methods=["POST"])
def export_to_sheets():
    if not session.get('google_credentials'):
        return jsonify({"error": "Google authentication required"}), 401
    
    try:
        from google.oauth2.credentials import Credentials
        import json
        
        credentials = Credentials.from_authorized_user_info(
            json.loads(session['google_credentials'])
        )
        
        title = request.json.get("title", "Stats")
        export_data = request.json.get("data", [])
        
        if not export_data:
            return jsonify({"error": "No data provided"}), 400
        
        spreadsheet_id = google_integration.create_spreadsheet(credentials, title, export_data)
        
        return jsonify({
            "success": True,
            "spreadsheet_id": spreadsheet_id,
            "url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/google-auth-status", methods=["GET"])
def google_auth_status():
    return jsonify({"authenticated": bool(session.get('google_credentials'))})

# ===== Campaign and UTM Analysis Routes =====
@app.route("/get-utm-analysis", methods=["GET"])
def get_utm_analysis_route():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({"error": "Access token required"}), 401
    
    try:
        analysis_data = get_utm_analysis(access_token)
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-campaign-engagement-analysis", methods=["GET"])
def get_campaign_engagement_analysis_route():
    try:
        months = request.args.get("months", "6")  # Default 6 months
        analysis_data = get_campaign_engagement_analysis(months)
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":

    app.run(port=4001, debug=True, host='127.0.0.1')

#     app.run(port=4001, debug=True)
# >>>>>>> landing_pages
