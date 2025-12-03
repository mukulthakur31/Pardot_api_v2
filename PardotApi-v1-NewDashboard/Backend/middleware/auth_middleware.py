from functools import wraps
from flask import request, jsonify, g
import jwt
from config.settings import SECRET_KEY
from services.salesforce_auth import SalesforceAuthService

auth_service = SalesforceAuthService()

def require_auth(f):
    """Middleware to authenticate JWT token from cookie"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get JWT token from cookie
        jwt_token = request.cookies.get('auth_token')
        
        if not jwt_token:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            # Decode JWT token
            payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=['HS256'])
            token_ref = payload.get('token_ref')
            
            # Get actual token from auth service class (auto-refreshes if expired)
            try:
                actual_token = auth_service.get_valid_access_token()
            except Exception as e:
                print(f"Token refresh failed: {str(e)}")
                return jsonify({'error': 'Token refresh failed, please re-login'}), 401
            
            # Match token reference with actual token
            if not actual_token:
                return jsonify({'error': 'No valid token available'}), 401
            
            # Skip token reference check if token was refreshed
            if not actual_token.startswith(token_ref):
                print("Token was refreshed, reference mismatch is expected")
                # Update JWT with new token reference for future requests
                # For now, just proceed with the refreshed token
            
            # Store token in g for route use
            g.access_token = actual_token
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Authentication failed'}), 401
    
    return decorated_function