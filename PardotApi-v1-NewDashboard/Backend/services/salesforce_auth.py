import requests
import time
from config.settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SF_LOGIN_URL

class SalesforceAuthService:
    _instance = None
    _token_data = {
        "access_token": None,
        "refresh_token": None,
        "expires_at": None
    }
 
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SalesforceAuthService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Use class-level token_data to share across instances
        self.token_data = SalesforceAuthService._token_data

    def save_tokens(self, data):
        """Save access/refresh token with expiry timestamp."""
        self.token_data["access_token"] = data.get("access_token")
        self.token_data["refresh_token"] = data.get("refresh_token")
        self.token_data["expires_at"] = time.time() + int(data.get("expires_in", 3600))

    def is_token_expired(self):
        if not self.token_data["expires_at"]:
            return True
        return time.time() > self.token_data["expires_at"] - 300  # refresh 5 min early

    def exchange_code_for_token(self, code):
        url = f"{SF_LOGIN_URL}/services/oauth2/token"
        print(url)
        response = requests.post(url, data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI
        })

        if response.status_code != 200:
            raise Exception(response.text)

        token_data = response.json()
        self.save_tokens(token_data)
        return token_data

    def refresh_access_token(self):
        print(f"Attempting token refresh. Refresh token exists: {bool(self.token_data.get('refresh_token'))}")
        if not self.token_data.get("refresh_token"):
            print("No refresh token found, clearing token data")
            self.token_data = {"access_token": None, "refresh_token": None, "expires_at": None}
            raise Exception("No refresh token found. Please re-authenticate.")

        url = f"{SF_LOGIN_URL}/services/oauth2/token"

        response = requests.post(url, data={
            "grant_type": "refresh_token",
            "refresh_token": self.token_data["refresh_token"],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        })

        if response.status_code != 200:
            print(f"Token refresh failed: {response.text}")
            self.token_data = {"access_token": None, "refresh_token": None, "expires_at": None}
            raise Exception(response.text)

        token_data = response.json()
        # Preserve existing refresh token if not provided in response
        if 'refresh_token' not in token_data and self.token_data.get('refresh_token'):
            token_data['refresh_token'] = self.token_data['refresh_token']
        self.save_tokens(token_data)
        return token_data

    def get_valid_access_token(self):
        """Central method: always use this."""
        if self.is_token_expired():
            print(f"🔄 TOKEN REFRESH: Token expired, refreshing automatically...")
            self.refresh_access_token()
            print(f"✅ TOKEN REFRESH: Successfully refreshed token")
        else:
            print(f"✅ TOKEN VALID: Using existing token (expires in {int(self.token_data['expires_at'] - time.time())} seconds)")
        return self.token_data["access_token"]
