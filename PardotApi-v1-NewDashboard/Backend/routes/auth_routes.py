from flask import Blueprint, redirect, request, jsonify, make_response
import jwt
import time
from config.settings import REDIRECT_URI, CLIENT_ID, CLIENT_SECRET, SECRET_KEY
from services.salesforce_auth import SalesforceAuthService
from middleware.auth_middleware import require_auth

auth_bp = Blueprint('auth', __name__)
auth_service = SalesforceAuthService()

@auth_bp.route("/login")
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

@auth_bp.route("/callback")
def callback():
    auth_code = request.args.get("code")
    if not auth_code:
        return jsonify({"error": "No code received"}), 400

    try:
        # Get token and store in auth service class
        token_data = auth_service.exchange_code_for_token(auth_code)
        access_token = token_data.get("access_token")
        
        # Create JWT with token reference
        jwt_payload = {
            'token_ref': access_token[:10],  # First 10 chars as reference
            'exp': int(time.time()) + (24 * 3600),  # 24 hours
            'iat': int(time.time())
        }
        
        jwt_token = jwt.encode(jwt_payload, SECRET_KEY, algorithm='HS256')
        
        # Redirect with JWT cookie
        response = make_response(redirect("http://localhost:5173/dashboard"))
        response.set_cookie(
            'auth_token',
            jwt_token,
            max_age=24*3600,  # 24 hours
            httponly=False,  # Allow JS access for debugging
            secure=False,
            samesite='Lax',
            path='/'
        )
        
        return response
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route("/check-auth")
@require_auth
def check_auth():
    """Check if user is authenticated"""
    return jsonify({"authenticated": True, "token_valid": True})


@auth_bp.route("/auth-status")
def auth_status():
    """Check authentication status without requiring auth"""
    try:
        jwt_token = request.cookies.get('auth_token')
        if not jwt_token:
            return jsonify({"authenticated": False, "reason": "No JWT token found"})
        
        # Try to decode JWT
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
        token_ref = payload.get('token_ref')
        
        # Check if we have a valid Salesforce token
        actual_token = auth_service.get_valid_access_token()
        if not actual_token:
            return jsonify({"authenticated": False, "reason": "No Salesforce token available"})
        
        if not actual_token.startswith(token_ref):
            return jsonify({"authenticated": False, "reason": "Token reference mismatch"})
        
        return jsonify({"authenticated": True, "token_valid": True})
        
    except jwt.ExpiredSignatureError:
        return jsonify({"authenticated": False, "reason": "JWT token expired"})
    except jwt.InvalidTokenError:
        return jsonify({"authenticated": False, "reason": "Invalid JWT token"})
    except Exception as e:
        return jsonify({"authenticated": False, "reason": f"Auth check failed: {str(e)}"})

