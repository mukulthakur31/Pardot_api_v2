from flask import Blueprint, request, jsonify, redirect, session, g
from google_integration import GoogleIntegration
from config.settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from middleware.auth_middleware import require_auth

google_bp = Blueprint('google', __name__)

# Initialize Google Integration
google_integration = GoogleIntegration(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)

@google_bp.route("/google-auth", methods=["GET"])
@require_auth
def google_auth():
    try:
        auth_url, flow = google_integration.get_auth_url()
        print("entered in google auth")
        return jsonify({"auth_url": auth_url})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@google_bp.route("/google-callback")
def google_callback():
    try:
        code = request.args.get('code')
        print(code)
        if not code:
            return jsonify({"error": "No code received"}), 400
        
        _, flow = google_integration.get_auth_url()
        credentials = google_integration.get_credentials(code, flow)
        print(credentials)
        session['google_credentials'] = credentials.to_json()
        
        return redirect('http://localhost:5173/dashboard?google_auth=success')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@google_bp.route("/export-to-sheets", methods=["POST"])
@require_auth
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

@google_bp.route("/google-auth-status", methods=["GET"])
def google_auth_status():
    return jsonify({"authenticated": bool(session.get('google_credentials'))})

@google_bp.route("/google-disconnect", methods=["POST"])
@require_auth
def google_disconnect():
    try:
        session.pop('google_credentials', None)
        return jsonify({"success": True, "message": "Google account disconnected"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500