"""
Health check and information routes
"""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "LinkedIn Recruiter Finder API is running"
    })

@health_bp.route('/', methods=['GET'])
def index():
    """API information endpoint"""
    return jsonify({
        "name": "LinkedIn Recruiter Finder API",
        "version": "2.0.0",
        "description": "Find LinkedIn recruiters by company or get AI-powered recommendations based on your resume",
        "endpoints": {
            "/search?company=CompanyName": "Search for LinkedIn recruiter profiles with location support",
            "/companies": "Get list of companies with filtering options",
            "/analyze-resume": "Analyze uploaded resume and get recruiter recommendations",
            "/health": "Health check",
            "/test-search?company=CompanyName": "Test Google Custom Search API configuration",
            "/debug-search?company=Company&test_type=full": "Debug Custom Search Engine configuration and troubleshooting",
            "/api/guess_emails": "Guess email addresses for a person (POST)",
            "/api/find_contact": "Find both email and phone contact information (POST)",
            "/api/find_phone": "Find phone numbers for a person (POST)"
        },
        "features": [
            "Company-based recruiter search",
            "Location-aware search (e.g., 'Google India')",
            "AI-powered resume analysis",
            "Smart recruiter matching",
            "Email address discovery and validation",
            "Phone number finding with Indian focus",
            "Contact information discovery",
            "Google Custom Search API integration",
            "Gemini 2.0 Flash AI analysis",
            "Advanced debugging and diagnostics"
        ],
        "usage": {
            "company_search": "GET /search?company=Google or /search?company=Google%20India",
            "companies_list": "GET /companies?location=all&search=tech",
            "resume_analysis": "POST /analyze-resume (with file upload)",
            "contact_finding": "POST /api/find_contact (with name and domain)",
            "phone_finding": "POST /api/find_phone (with name and company)",
            "debug_search": "GET /debug-search?company=Google&test_type=linkedin"
        },
        "new_features": {
            "location_aware_search": "Search for 'Google India', 'Microsoft USA', 'Apple UK' etc.",
            "enhanced_debugging": "Use /debug-search to diagnose search configuration issues",
            "improved_accuracy": "Better search strategies and result filtering"
        }
    })

@health_bp.route('/routes', methods=['GET'])
def list_routes():
    """
    List all registered routes for debugging
    
    Returns:
        JSON response with all routes
    """
    from flask import current_app
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "rule": str(rule)
        })
    return jsonify({
        "routes": routes,
        "total": len(routes)
    })