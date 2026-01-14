from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

# Import configuration
from config.settings import SECRET_KEY

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Security: Configure CORS properly for production
    CORS(app, 
         origins=["http://localhost:5173"], 
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.email_routes import email_bp
    from routes.form_routes import form_bp
    from routes.landing_page_routes import landing_page_bp
    from routes.prospect_routes import prospect_bp
    from routes.engagement_routes import engagement_bp
    from routes.utm_routes import utm_bp
    from routes.pdf_routes import pdf_bp
    from routes.google_routes import google_bp
    from routes.database_health_routes import database_health_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(form_bp)
    app.register_blueprint(landing_page_bp)
    app.register_blueprint(prospect_bp)
    app.register_blueprint(engagement_bp)
    app.register_blueprint(utm_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(google_bp)
    app.register_blueprint(database_health_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=4001, debug=True, host='127.0.0.1')