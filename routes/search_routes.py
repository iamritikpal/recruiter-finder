"""
Search routes for company-based recruiter search
"""
import logging
from flask import Blueprint, request, jsonify, current_app
from utils.search_utils import search_with_fallback
from utils.company_api_utils import company_service

logger = logging.getLogger(__name__)

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search_recruiters():
    """
    API endpoint to search for LinkedIn recruiter profiles by company
    
    Query Parameters:
        company (str): Company name to search for
    
    Returns:
        JSON response with profiles or error message
    """
    try:
        company = request.args.get('company')
        
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
        
        logger.info(f"Searching for recruiters at: {company}")
        
        # Get search and Gemini clients from app context
        search_client = current_app.search_client
        gemini_client = current_app.gemini_client
        
        # Perform the search using utilities
        try:
            profiles = search_with_fallback(
                search_client, 
                gemini_client, 
                company.strip(),
                current_app.config['MAX_SEARCH_RESULTS']
            )
        except Exception as search_error:
            logger.error(f"Search function error: {search_error}")
            return jsonify({
                "error": "Search failed",
                "message": "Unable to perform search at this time. This could be due to network issues or temporary service unavailability. Please try again in a few moments.",
                "company": company,
                "profiles": []
            }), 500
        
        if not profiles:
            return jsonify({
                "company": company,
                "profiles": [],
                "message": _get_no_results_message(company)
            })
        
        # Check if location-aware search was performed
        location_context = ""
        if profiles and profiles[0].get('location_searched'):
            location = profiles[0]['location_searched']
            location_context = f" in {location.title()}"
        
        # Fix f-string syntax by moving string with backslashes outside
        example_text = 'Add location like "Company India" for targeted results'
        search_enhanced_msg = f"🌍 Location-aware search {'activated' if location_context else 'available'} - {'Results filtered by location' if location_context else example_text}"
        
        return jsonify({
            "company": company,
            "profiles": profiles,
            "count": len(profiles),
            "location_searched": profiles[0].get('location_searched') if profiles else None,
            "message": f"Found {len(profiles)} LinkedIn recruiter profile{'s' if len(profiles) != 1 else ''}{location_context}",
            "search_enhanced": search_enhanced_msg
        })
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({
            "error": "API error",
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(e) if current_app.debug else None
        }), 500

@search_bp.route('/test-search', methods=['GET'])
def test_search():
    """
    Test endpoint to debug Custom Search Engine configuration
    
    Query Parameters:
        company (str): Company name to test with (default: Google)
    
    Returns:
        JSON response with test results
    """
    try:
        company = request.args.get('company', 'Google')
        search_client = current_app.search_client
        
        if not search_client:
            return jsonify({
                "error": "Custom Search API not configured",
                "custom_search_key": bool(current_app.config.get('GOOGLE_CUSTOM_SEARCH_API_KEY')),
                "search_engine_id": bool(current_app.config.get('GOOGLE_CUSTOM_SEARCH_ENGINE_ID'))
            })
        
        # Test the search configuration
        test_results = search_client.test_search(company)
        
        return jsonify({
            "test_company": company,
            "configuration_status": "configured",
            "results": test_results
        })
        
    except Exception as e:
        logger.error(f"Test search error: {e}")
        return jsonify({
            "error": str(e),
            "custom_search_configured": bool(current_app.search_client),
            "gemini_configured": bool(current_app.gemini_client)
        })

@search_bp.route('/debug-search', methods=['GET'])
def debug_search():
    """
    Debug endpoint to diagnose Custom Search Engine configuration
    
    Query Parameters:
        company (str): Company name to test with (default: Google)
        test_type (str): Type of test to run (basic, linkedin, full)
    
    Returns:
        JSON response with detailed debug information
    """
    try:
        company = request.args.get('company', 'Google')
        test_type = request.args.get('test_type', 'full')
        
        search_client = current_app.search_client
        
        if not search_client:
            return jsonify({
                "error": "Custom Search API not configured",
                "custom_search_key": bool(current_app.config.get('GOOGLE_CUSTOM_SEARCH_API_KEY')),
                "search_engine_id": bool(current_app.config.get('GOOGLE_CUSTOM_SEARCH_ENGINE_ID'))
            })
        
        debug_results = {
            "test_company": company,
            "test_type": test_type,
            "configuration": {
                "api_key_length": len(search_client.api_key) if search_client.api_key else 0,
                "search_engine_id": search_client.search_engine_id
            },
            "tests": []
        }
        
        # Test different search approaches
        test_queries = []
        
        if test_type in ['basic', 'full']:
            test_queries.extend([
                f'{company}',
                f'{company} recruiter',
                f'recruiter {company}'
            ])
        
        if test_type in ['linkedin', 'full']:
            test_queries.extend([
                f'site:linkedin.com {company}',
                f'site:linkedin.com {company} recruiter',
                f'site:linkedin.com/in {company}',
                f'linkedin.com {company} recruiter'
            ])
        
        if test_type == 'full':
            test_queries.extend([
                f'{company} india recruiter',
                f'{company} hiring manager',
                f'{company} talent acquisition'
            ])
        
        import requests
        
        for query in test_queries:
            test_result = {
                "query": query,
                "status": "unknown",
                "results_count": 0,
                "error": None,
                "sample_results": []
            }
            
            try:
                params = {
                    'key': search_client.api_key,
                    'cx': search_client.search_engine_id,
                    'q': query,
                    'num': 3,
                    'safe': 'off'
                }
                
                response = requests.get(search_client.base_url, params=params, timeout=10)
                test_result["response_status"] = response.status_code
                test_result["response_url"] = response.url
                
                if response.status_code == 200:
                    data = response.json()
                    test_result["status"] = "success"
                    
                    if 'searchInformation' in data:
                        test_result["total_results"] = data['searchInformation'].get('totalResults', '0')
                        test_result["search_time"] = data['searchInformation'].get('searchTime', '0')
                    
                    if 'items' in data:
                        test_result["results_count"] = len(data['items'])
                        # Get sample results
                        for item in data['items'][:3]:
                            sample = {
                                "title": item.get('title', '')[:100],
                                "url": item.get('link', ''),
                                "is_linkedin": "linkedin.com" in item.get('link', ''),
                                "has_recruiter_keywords": any(keyword in item.get('title', '').lower() + item.get('snippet', '').lower() 
                                                            for keyword in ['recruiter', 'hiring', 'talent', 'hr'])
                            }
                            test_result["sample_results"].append(sample)
                    else:
                        test_result["results_count"] = 0
                else:
                    test_result["status"] = "error"
                    test_result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                    
            except Exception as e:
                test_result["status"] = "error"
                test_result["error"] = str(e)
            
            debug_results["tests"].append(test_result)
        
        # Summary
        successful_tests = [t for t in debug_results["tests"] if t["status"] == "success" and t["results_count"] > 0]
        debug_results["summary"] = {
            "total_tests": len(debug_results["tests"]),
            "successful_tests": len(successful_tests),
            "tests_with_results": len([t for t in debug_results["tests"] if t["results_count"] > 0]),
            "linkedin_results_found": any(any(r["is_linkedin"] for r in t["sample_results"]) for t in debug_results["tests"]),
            "recruiter_keywords_found": any(any(r["has_recruiter_keywords"] for r in t["sample_results"]) for t in debug_results["tests"])
        }
        
        # Recommendations
        recommendations = []
        
        if debug_results["summary"]["successful_tests"] == 0:
            recommendations.append("❌ No successful searches - check API key and Search Engine ID")
        
        if not debug_results["summary"]["linkedin_results_found"]:
            recommendations.append("❌ No LinkedIn results found - check if Search Engine includes linkedin.com")
        
        if not debug_results["summary"]["recruiter_keywords_found"]:
            recommendations.append("⚠️ No recruiter-related results found - may need to adjust search terms")
        
        if debug_results["summary"]["successful_tests"] > 0:
            recommendations.append("✅ API is working - search configuration looks good")
        
        debug_results["recommendations"] = recommendations
        
        return jsonify(debug_results)
        
    except Exception as e:
        logger.error(f"Debug search error: {e}")
        return jsonify({
            "error": str(e),
            "custom_search_configured": bool(current_app.search_client),
            "gemini_configured": bool(current_app.gemini_client)
        })

@search_bp.route('/companies', methods=['GET'])
def get_companies():
    """Get all companies with their details for the gallery"""
    try:
        logger.info("Fetching companies from API service...")
        
        # Check if force refresh is requested
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        # Fetch companies from API service
        if force_refresh:
            companies_data = company_service.force_refresh()
            cache_status = "refreshed"
        else:
            companies_data = company_service.fetch_all_companies()
            # Check if data came from cache using the new method
            cache_status = "hit" if company_service.was_last_fetch_from_cache() else "miss"
        
        # Add filtering options
        location = request.args.get('location')
        category = request.args.get('category')
        search = request.args.get('search', '').lower()
        
        filtered_companies = companies_data
        
        # Filter by location
        if location and location != 'all':
            filtered_companies = [
                company for company in filtered_companies 
                if location in company['locations']
            ]
        
        # Filter by category
        if category and category != 'all':
            filtered_companies = [
                company for company in filtered_companies 
                if company['category'].lower() == category.lower()
            ]
        
        # Filter by search term
        if search:
            filtered_companies = [
                company for company in filtered_companies 
                if (search in company['display_name'].lower() or 
                    search in company['category'].lower() or 
                    search in company['description'].lower() or
                    search in company['industry'].lower() or
                    any(search in tag.lower() for tag in company['tags']))
            ]
        
        # Get available filters
        available_locations = sorted(list(set(loc for company in companies_data for loc in company['locations'])))
        available_categories = sorted(list(set(company['category'] for company in companies_data)))
        
        return jsonify({
            'success': True,
            'companies': filtered_companies,
            'total_count': len(companies_data),
            'filtered_count': len(filtered_companies),
            'filters': {
                'location': location,
                'category': category,
                'search': search
            },
            'available_locations': available_locations,
            'available_categories': available_categories,
            'data_source': 'live_api',
            'cache_status': cache_status,
            'cache_stats': company_service.get_cache_stats(),
            'timestamp': None
        })
        
    except Exception as e:
        logger.error(f"Error getting companies from API: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to fetch companies data from API',
            'message': str(e),
            'data_source': 'api_error'
        }), 500

@search_bp.route('/companies/cache', methods=['GET'])
def get_cache_info():
    """Get cache statistics"""
    try:
        cache_stats = company_service.get_cache_stats()
        return jsonify({
            'success': True,
            'cache_stats': cache_stats
        })
    except Exception as e:
        logger.error(f"Error getting cache info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get cache information',
            'message': str(e)
        }), 500

@search_bp.route('/companies/cache', methods=['DELETE'])
def clear_cache():
    """Clear the company data cache"""
    try:
        company_service.clear_cache()
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to clear cache',
            'message': str(e)
        }), 500

def _get_no_results_message(company):
    """Generate detailed no results message with location awareness"""
    
    # Check if location was specified
    try:
        from utils.search_utils import CustomSearchClient
        # Create a temporary instance to use the parsing method
        temp_client = type('temp', (), {})()
        temp_client._parse_company_and_location = lambda x: _parse_company_and_location_simple(x)
        
        parsed_company, location = temp_client._parse_company_and_location(company)
    except:
        parsed_company, location = company, None
    
    if location:
        location_specific_message = f"""
🌍 **Location-Specific Search Results for {parsed_company} in {location.title()}**

No recruiter profiles found for '{parsed_company}' specifically in {location.title()}.

**We searched for:**
• Technical/Engineering Recruiters in {location.title()}
• Talent Acquisition Specialists at {parsed_company} {location.title()} office
• Local Hiring Managers and HR personnel
• Regional recruiting teams for {location.title()}

**This could be due to:**
• Limited public LinkedIn profiles for {parsed_company} recruiters in {location.title()}
• Recruiters may be listed under global profiles without location specification
• {location.title()}-specific recruiting team may be small or recently established

**Try these suggestions:**
• Search without location: "{parsed_company}" (for global recruiters)
• Try alternate location names: 
  {_get_alternate_location_names(location)}
• Search for regional terms: "{parsed_company} {_get_regional_term(location)}"
• Look for country/regional heads: "{parsed_company} {location.title()} country manager"

**💡 Alternative approaches:**
• Connect with {parsed_company} employees in {location.title()} who might refer you to recruiters
• Check {parsed_company}'s careers page for {location.title()}-specific contact information
• Look for {parsed_company} recruiting events or job fairs in {location.title()}
        """
        return location_specific_message.strip()
    
    else:
        return f"""No recruiter profiles found for '{company}'.

We search for people with titles like:
• Technical/Engineering Recruiters
• Talent Acquisition Specialists
• Hiring Managers
• Recruiting Managers
• People Partners
• And other recruiting roles

This could be due to:
• No recruiters with public LinkedIn profiles for this company
• Try different company name variations (e.g., 'Uber Technologies' instead of 'Uber')
• Some companies may have limited public recruiter visibility

**💡 Enhanced Search Tips:**
Try location-specific searches like:
• "{company} India" - for India-based recruiters
• "{company} USA" - for US-based recruiters  
• "{company} London" - for London-based recruiters
• "{company} Singapore" - for Singapore-based recruiters

Try searching for larger tech companies like Google, Microsoft, or Apple for better results.

**New!** 🌍 Location-aware search now available - specify location for targeted results!"""

def _parse_company_and_location_simple(company_input):
    """Simple parsing function for location detection in messages"""
    import re
    
    location_patterns = [
        r'\b(india|usa|uk|canada|australia|germany|france|singapore|japan|china|brazil|mexico)\b',
        r'\b(bangalore|mumbai|delhi|hyderabad|chennai|pune|london|new york|san francisco|seattle|toronto|sydney|berlin|paris|tokyo|beijing|shanghai|sao paulo)\b'
    ]
    
    company_input_lower = company_input.lower().strip()
    
    for pattern in location_patterns:
        match = re.search(pattern, company_input_lower, re.IGNORECASE)
        if match:
            location = match.group(1)
            company = re.sub(r'\s*' + re.escape(location) + r'\s*', '', company_input, flags=re.IGNORECASE).strip()
            return company, location
    
    return company_input.strip(), None

def _get_alternate_location_names(location):
    """Get alternate names for a location"""
    alternates = {
        'india': 'IN, Bharat, "Indian subcontinent"',
        'usa': 'US, "United States", America, "North America"',
        'uk': 'Britain, "United Kingdom", England, "Great Britain"', 
        'canada': 'CA, "North America"',
        'australia': 'AU, Oceania',
        'germany': 'DE, Deutschland',
        'france': 'FR, "French Republic"',
        'singapore': 'SG, "Southeast Asia"',
        'japan': 'JP, "East Asia"',
        'china': 'CN, "Peoples Republic", "East Asia"',
        'brazil': 'BR, Brasil, "South America"',
        'mexico': 'MX, "North America"',
        'bangalore': 'Bengaluru, "Garden City", Karnataka',
        'mumbai': 'Bombay, Maharashtra, "Financial Capital"',
        'delhi': '"New Delhi", NCR, "Capital Region"',
        'london': '"Greater London", "City of London"',
        'new york': 'NYC, "New York City", Manhattan',
        'san francisco': 'SF, "Bay Area", "Silicon Valley"'
    }
    
    return alternates.get(location.lower(), f'"{location}"')

def _get_regional_term(location):
    """Get regional terms for location"""
    regions = {
        'india': 'APAC',
        'usa': 'Americas', 
        'uk': 'EMEA',
        'canada': 'Americas',
        'australia': 'APAC',
        'germany': 'EMEA',
        'france': 'EMEA', 
        'singapore': 'APAC',
        'japan': 'APAC',
        'china': 'APAC',
        'brazil': 'Americas',
        'mexico': 'Americas'
    }
    
    return regions.get(location.lower(), 'Regional') 