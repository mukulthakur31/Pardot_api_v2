import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
REDIRECT_URI = "http://localhost:4001/callback"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
CLIENT_ID=os.getenv("CLIENT_ID")
BUSINESS_UNIT_ID=os.getenv("BUSINESS_UNIT_ID")
SF_LOGIN_URL=os.getenv("SF_LOGIN_URL")