"""
LinkedIn Recruiter Finder - Main Application
A full-stack web application to find LinkedIn recruiters by company or analyze resumes for AI-powered recommendations.

Features:
- Company-based recruiter search using Google Custom Search API
- AI-powered resume analysis using Gemini 2.0 Flash
- Smart recruiter matching and recommendations
- Modern React frontend with responsive design
- RESTful API endpoints

Author: AI Assistant
Version: 2.0.0
"""

import logging
from flask import Flask
from flask_cors import CORS

# Import configuration
from config.config import Config

# Import utility classes
from utils.search_utils import create_search_client
from utils.gemini_utils import create_gemini_client

# Import route blueprints
try:
    from routes.health_routes import health_bp
    from routes.search_routes import search_bp
    from routes.resume_routes import resume_bp
    from routes.email_routes import email_bp
    from routes.job_routes import job_bp
    print("All blueprints imported successfully")
except ImportError as e:
    print(f"Blueprint import error: {e}")
    raise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('recruiter_finder.log')
    ]
)

logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """
    Application factory pattern
    
    Args:
        config_class: Configuration class to use
    
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for frontend communication
    # Allow localhost for development and specific production domains
    allowed_origins = [
        # Development origins
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://localhost:3000",  # HTTPS localhost
        
        # Your specific frontend deployment
        "https://find-recruiter.onrender.com",
        
        # Generic platform patterns (for flexibility)
        "https://*.netlify.app",
        "https://*.vercel.app", 
        "https://*.onrender.com",
        "https://*.herokuapp.com",
        "https://*.github.io",
        "https://*.pages.dev",  # Cloudflare Pages
    ]
    
    # In development, allow all origins for easier testing
    if app.config.get('DEBUG', False):
        CORS(app, origins="*")  # Allow all origins in debug mode
    else:
        # In production, be more specific but include your frontend domain
        CORS(app, 
             origins=allowed_origins,
             methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             allow_headers=["Content-Type", "Authorization"],
             supports_credentials=True)
    
    # Initialize API clients
    search_client = create_search_client(
        app.config['GOOGLE_CUSTOM_SEARCH_API_KEY'],
        app.config['GOOGLE_CUSTOM_SEARCH_ENGINE_ID']
    )
    
    gemini_client = create_gemini_client(
        app.config['GOOGLE_GEMINI_API_KEY'],
        app.config['GEMINI_MODEL']
    )
    
    # Initialize job search client (using same Google Custom Search credentials)
    from utils.job_search_utils import create_job_search_client
    job_search_client = create_job_search_client(
        app.config['GOOGLE_CUSTOM_SEARCH_API_KEY'],
        app.config['GOOGLE_CUSTOM_SEARCH_ENGINE_ID']
    )
    
    # Store clients in app context for route access
    app.search_client = search_client
    app.gemini_client = gemini_client
    app.job_search_client = job_search_client
    
    # Register blueprints - matching the DEPLOYED backend (with /api prefix)
    try:
        # Health routes (no prefix) - /health
        app.register_blueprint(health_bp)
        logger.info("Health blueprint registered")
        
        # Search and company routes (with /api prefix) - /api/search, /api/companies 
        app.register_blueprint(search_bp, url_prefix='/api')
        logger.info("Search blueprint registered")
        
        # Resume routes (with /api prefix) - /api/analyze-resume
        app.register_blueprint(resume_bp, url_prefix='/api')
        logger.info("Resume blueprint registered")
        
        # Email/contact routes (with /api prefix) - /api/find_contact, /api/find_phone
        app.register_blueprint(email_bp, url_prefix='/api')
        logger.info("Email blueprint registered")
        
        # Job routes (with /api prefix) - /api/search-jobs, /api/jobs-by-company
        app.register_blueprint(job_bp, url_prefix='/api')
        logger.info("Job blueprint registered")
        
    except Exception as e:
        logger.error(f"Error registering blueprints: {e}")
        raise
    
    # Log configuration status
    _log_configuration_status(app, search_client, gemini_client)
    
    return app

def _log_configuration_status(app, search_client, gemini_client):
    """Log the configuration status of various services"""
    logger.info("=== LinkedIn Recruiter Finder v2.0.0 ===")
    logger.info("Configuration Status:")
    
    # API Configuration
    if search_client:
        logger.info("Google Custom Search API: Configured")
    else:
        logger.warning("Google Custom Search API: Not configured")
    
    if gemini_client:
        logger.info(f"Gemini AI ({app.config['GEMINI_MODEL']}): Configured")
    else:
        logger.warning("Gemini AI: Not configured")
    
    # Application Settings
    logger.info(f"Debug Mode: {app.config['DEBUG']}")
    logger.info(f"Host: {app.config['HOST']}")
    logger.info(f"Port: {app.config['PORT']}")
    logger.info(f"Max File Size: {app.config['MAX_FILE_SIZE'] / (1024*1024):.1f}MB")
    logger.info(f"Allowed Extensions: {', '.join(app.config['ALLOWED_EXTENSIONS'])}")
    
    # Feature Status
    features = []
    if search_client:
        features.append("Company Search")
    if gemini_client:
        features.append("Resume Analysis")
    if search_client and gemini_client:
        features.append("AI Recommendations")
    
    if features:
        logger.info(f"Available Features: {', '.join(features)}")
    else:
        logger.error("No features available - Please configure API keys")
    
    logger.info("=" * 45)

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    """
    Run the application in development mode
    
    Setup Instructions:
    1. Install dependencies: pip install -r requirements.txt
    2. Set up environment variables in .env file:
       - GOOGLE_CUSTOM_SEARCH_API_KEY=your_api_key
       - GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_engine_id  
       - GOOGLE_GEMINI_API_KEY=your_gemini_key
    3. Start the backend: python app.py
    4. Start the frontend: cd frontend && npm start
    5. Open http://localhost:3000 in your browser
    
    API Endpoints:
    - GET  /                          - API information
    - GET  /health                    - Health check
    - GET  /search?company=Name       - Search recruiters by company
    - POST /analyze-resume            - Analyze resume and get recommendations
    - GET  /test-search?company=Name  - Test search configuration
    - POST /api/guess_emails          - Guess email addresses for a person
    - POST /api/find_contact          - Find both email and phone contact info
    
    For production deployment, use a WSGI server like Gunicorn:
    gunicorn --bind 0.0.0.0:5000 app:app
    """
    
    logger.info("Starting LinkedIn Recruiter Finder...")
    logger.info("Frontend URL: http://localhost:3000")
    logger.info("Backend API: http://localhost:5000")
    
    try:
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        raise 