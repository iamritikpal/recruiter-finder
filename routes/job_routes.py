"""
Job search routes for company-based job posting search
"""
import logging
from flask import Blueprint, request, jsonify, current_app
from utils.job_search_utils import search_jobs_with_fallback

logger = logging.getLogger(__name__)

job_bp = Blueprint('jobs', __name__)

@job_bp.route('/search-jobs', methods=['GET'])
def search_jobs():
    """
    API endpoint to search for job postings by company
    
    Query Parameters:
        company (str): Company name to search for
        location (str, optional): Location filter
        max_results (int, optional): Maximum number of results (default: 15)
    
    Returns:
        JSON response with job postings or error message
    """
    try:
        company = request.args.get('company')
        location = request.args.get('location')
        max_results = int(request.args.get('max_results', 15))
        
        if not company:
            return jsonify({
                "error": "Company parameter is required",
                "message": "Please provide a company name using ?company=CompanyName"
            }), 400
        
        if len(company.strip()) < 2:
            return jsonify({
                "error": "Invalid company name",
                "message": "Company name must be at least 2 characters long"
            }), 400
        
        # Combine company and location if provided
        search_term = f"{company} {location}" if location else company
        
        logger.info(f"Searching for jobs at: {search_term}")
        
        # Get job search client from app context
        job_search_client = getattr(current_app, 'job_search_client', None)
        
        # Perform the job search using utilities
        job_results = search_jobs_with_fallback(
            job_search_client, 
            search_term, 
            max_results
        )
        
        # Format response
        response_data = {
            "success": True,
            "query": {
                "company": company,
                "location": location,
                "max_results": max_results
            },
            "results": {
                "total_found": len(job_results),
                "jobs": job_results
            },
            "metadata": {
                "search_performed": True,
                "api_used": "Google Custom Search" if job_search_client else "Sample Data",
                "search_strategies": "Multiple job boards and company career pages"
            }
        }
        
        logger.info(f"Found {len(job_results)} job postings for {search_term}")
        return jsonify(response_data)
    
    except ValueError as e:
        logger.error(f"Value error in job search: {e}")
        return jsonify({
            "error": "Invalid parameter",
            "message": "Please check your request parameters",
            "details": str(e) if current_app.debug else None
        }), 400
    
    except Exception as e:
        logger.error(f"Job search error: {e}")
        return jsonify({
            "error": "Job search failed",
            "message": "Failed to search for job postings. Please try again.",
            "details": str(e) if current_app.debug else None
        }), 500

@job_bp.route('/jobs-by-company/<company_name>', methods=['GET'])
def get_jobs_by_company(company_name):
    """
    API endpoint to get job postings for a specific company
    
    Path Parameters:
        company_name (str): Company name
    
    Query Parameters:
        location (str, optional): Location filter
        max_results (int, optional): Maximum number of results (default: 15)
    
    Returns:
        JSON response with job postings or error message
    """
    try:
        location = request.args.get('location')
        max_results = int(request.args.get('max_results', 15))
        
        if not company_name or len(company_name.strip()) < 2:
            return jsonify({
                "error": "Invalid company name",
                "message": "Company name must be at least 2 characters long"
            }), 400
        
        # Combine company and location if provided
        search_term = f"{company_name} {location}" if location else company_name
        
        logger.info(f"Getting jobs for company: {search_term}")
        
        # Get job search client from app context
        job_search_client = getattr(current_app, 'job_search_client', None)
        
        # Perform the job search
        job_results = search_jobs_with_fallback(
            job_search_client, 
            search_term, 
            max_results
        )
        
        # Format response
        response_data = {
            "success": True,
            "company": company_name,
            "location": location,
            "results": {
                "total_found": len(job_results),
                "jobs": job_results
            },
            "metadata": {
                "search_performed": True,
                "api_used": "Google Custom Search" if job_search_client else "Sample Data"
            }
        }
        
        logger.info(f"Found {len(job_results)} job postings for {company_name}")
        return jsonify(response_data)
    
    except ValueError as e:
        logger.error(f"Value error in company job search: {e}")
        return jsonify({
            "error": "Invalid parameter",
            "message": "Please check your request parameters",
            "details": str(e) if current_app.debug else None
        }), 400
    
    except Exception as e:
        logger.error(f"Company job search error: {e}")
        return jsonify({
            "error": "Company job search failed",
            "message": f"Failed to search for job postings at {company_name}. Please try again.",
            "details": str(e) if current_app.debug else None
        }), 500

@job_bp.route('/test-job-search', methods=['GET'])
def test_job_search():
    """
    Test endpoint to debug job search configuration
    
    Query Parameters:
        company (str): Company name to test with (default: Google)
    
    Returns:
        JSON response with test results
    """
    try:
        company = request.args.get('company', 'Google')
        job_search_client = getattr(current_app, 'job_search_client', None)
        
        if not job_search_client:
            return jsonify({
                "error": "Job Search API not configured",
                "custom_search_key": bool(current_app.config.get('GOOGLE_CUSTOM_SEARCH_API_KEY')),
                "search_engine_id": bool(current_app.config.get('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')),
                "message": "Job search client not available"
            })
        
        # Test the job search configuration
        test_results = job_search_client.search_jobs(company, max_results=3)
        
        return jsonify({
            "test_company": company,
            "configuration_status": "configured",
            "results_found": len(test_results),
            "sample_results": test_results[:2] if test_results else [],
            "client_type": type(job_search_client).__name__
        })
        
    except Exception as e:
        logger.error(f"Test job search error: {e}")
        return jsonify({
            "error": str(e),
            "test_company": request.args.get('company', 'Google'),
            "configuration_status": "error"
        })

@job_bp.route('/job-stats', methods=['GET'])
def get_job_stats():
    """
    Get job search statistics and available sources
    
    Returns:
        JSON response with job search statistics
    """
    try:
        job_search_client = getattr(current_app, 'job_search_client', None)
        
        stats = {
            "job_search_available": bool(job_search_client),
            "supported_sources": [
                "LinkedIn Jobs",
                "Indeed",
                "Glassdoor", 
                "Naukri (India)",
                "Monster",
                "Company Career Pages"
            ],
            "search_capabilities": [
                "Company-based job search",
                "Location-aware search",
                "Multiple job board integration",
                "Real-time job posting discovery",
                "Salary and job type extraction",
                "Relevance scoring and ranking"
            ],
            "supported_locations": [
                "India", "USA", "UK", "Canada", "Australia", "Germany",
                "Remote", "Hybrid", "Bangalore", "Mumbai", "Delhi",
                "London", "New York", "San Francisco", "Seattle"
            ],
            "api_status": {
                "google_custom_search": bool(current_app.config.get('GOOGLE_CUSTOM_SEARCH_API_KEY')),
                "search_engine_configured": bool(current_app.config.get('GOOGLE_CUSTOM_SEARCH_ENGINE_ID'))
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Job stats error: {e}")
        return jsonify({
            "error": "Failed to get job statistics",
            "message": str(e) if current_app.debug else "Internal server error"
        }), 500

@job_bp.route('/popular-companies', methods=['GET'])
def get_popular_companies_for_jobs():
    """
    Get list of popular companies for job search suggestions
    
    Returns:
        JSON response with popular companies
    """
    try:
        popular_companies = [
            # Tech Giants
            {"name": "Google", "category": "Technology", "locations": ["USA", "India", "UK"]},
            {"name": "Microsoft", "category": "Technology", "locations": ["USA", "India", "UK"]},
            {"name": "Amazon", "category": "Technology", "locations": ["USA", "India", "UK"]},
            {"name": "Apple", "category": "Technology", "locations": ["USA", "India"]},
            {"name": "Meta", "category": "Technology", "locations": ["USA", "India", "UK"]},
            
            # Indian IT Companies
            {"name": "TCS", "category": "IT Services", "locations": ["India", "USA", "UK"]},
            {"name": "Infosys", "category": "IT Services", "locations": ["India", "USA", "UK"]},
            {"name": "Wipro", "category": "IT Services", "locations": ["India", "USA"]},
            {"name": "HCL", "category": "IT Services", "locations": ["India", "USA"]},
            {"name": "Accenture", "category": "Consulting", "locations": ["India", "USA", "UK"]},
            
            # Startups & Unicorns
            {"name": "Zomato", "category": "Food Tech", "locations": ["India"]},
            {"name": "Paytm", "category": "Fintech", "locations": ["India"]},
            {"name": "Swiggy", "category": "Food Tech", "locations": ["India"]},
            {"name": "BYJU'S", "category": "EdTech", "locations": ["India"]},
            {"name": "Ola", "category": "Transportation", "locations": ["India"]},
            
            # Financial Services
            {"name": "JPMorgan Chase", "category": "Banking", "locations": ["USA", "India", "UK"]},
            {"name": "Goldman Sachs", "category": "Investment Banking", "locations": ["USA", "India", "UK"]},
            {"name": "HDFC Bank", "category": "Banking", "locations": ["India"]},
            {"name": "ICICI Bank", "category": "Banking", "locations": ["India"]},
            
            # Others
            {"name": "Deloitte", "category": "Consulting", "locations": ["USA", "India", "UK"]},
            {"name": "IBM", "category": "Technology", "locations": ["USA", "India", "UK"]},
            {"name": "Oracle", "category": "Technology", "locations": ["USA", "India"]},
            {"name": "Salesforce", "category": "Technology", "locations": ["USA", "India"]},
            {"name": "Netflix", "category": "Entertainment", "locations": ["USA", "India"]},
            {"name": "Uber", "category": "Transportation", "locations": ["USA", "India"]}
        ]
        
        # Group by category
        categories = {}
        for company in popular_companies:
            category = company["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(company)
        
        return jsonify({
            "total_companies": len(popular_companies),
            "categories": categories,
            "companies": popular_companies
        })
        
    except Exception as e:
        logger.error(f"Popular companies error: {e}")
        return jsonify({
            "error": "Failed to get popular companies",
            "message": str(e) if current_app.debug else "Internal server error"
        }), 500
