"""
Search utilities for Google Custom Search API integration with location support
"""
import requests
import logging
import re

logger = logging.getLogger(__name__)

class CustomSearchClient:
    """Google Custom Search API client with location-aware search"""
    
    def __init__(self, api_key, search_engine_id):
        """
        Initialize Custom Search client
        
        Args:
            api_key: Google Custom Search API key
            search_engine_id: Custom Search Engine ID
        """
        if not api_key or not search_engine_id:
            raise ValueError("API key and Search Engine ID are required")
        
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search_recruiters(self, company_name, max_results=10, timeout=30):
        """
        Search for LinkedIn recruiter profiles using multiple strategies with location awareness
        
        Args:
            company_name: Name of the company to search for (can include location)
            max_results: Maximum number of results to return
            timeout: Request timeout in seconds
        
        Returns:
            list: List of recruiter profiles
        """
        # Parse company name and location
        company, location = self._parse_company_and_location(company_name)
        
        logger.info(f"Searching for recruiters at: {company}" + (f" in {location}" if location else ""))
        
        # Generate location-aware search strategies
        search_strategies = self._generate_search_strategies(company, location)
        
        all_results = []
        
        for i, search_query in enumerate(search_strategies):
            logger.info(f"Trying search strategy {i+1}: {search_query}")
            
            try:
                results = self._perform_search(search_query, max_results, timeout, location)
                
                # Add unique results
                for result in results:
                    if not any(r['url'] == result['url'] for r in all_results):
                        all_results.append(result)
                        logger.info(f"Found LinkedIn profile: {result['title'][:50]}...")
                
                # Stop if we have enough results
                if len(all_results) >= max_results:
                    break
                    
            except Exception as e:
                logger.warning(f"Search strategy {i+1} failed: {e}")
                continue
        
        logger.info(f"Found {len(all_results)} unique LinkedIn profiles" + (f" for {location}" if location else ""))
        return all_results[:max_results]
    
    def _parse_company_and_location(self, company_input):
        """
        Parse company name and location from input string
        
        Args:
            company_input: Input string like "Google India" or "Microsoft UK"
        
        Returns:
            tuple: (company_name, location)
        """
        # Common location patterns
        location_patterns = [
            # Countries
            r'\b(india|usa|uk|canada|australia|germany|france|singapore|japan|china|brazil|mexico)\b',
            # Cities
            r'\b(bangalore|mumbai|delhi|hyderabad|chennai|pune|london|new york|san francisco|seattle|toronto|sydney|berlin|paris|tokyo|beijing|shanghai|sao paulo)\b',
            # Regions
            r'\b(asia pacific|emea|north america|latin america|middle east|europe)\b',
            # Office locations
            r'\b(silicon valley|bay area|wall street)\b'
        ]
        
        company_input_lower = company_input.lower().strip()
        
        # Try to find location match
        for pattern in location_patterns:
            match = re.search(pattern, company_input_lower, re.IGNORECASE)
            if match:
                location = match.group(1)
                # Remove location from company name
                company = re.sub(r'\s*' + re.escape(location) + r'\s*', '', company_input, flags=re.IGNORECASE).strip()
                return company, location
        
        # No location found, return original company name
        return company_input.strip(), None
    
    def _generate_search_strategies(self, company, location):
        """
        Generate search strategies with location awareness
        
        Args:
            company: Company name
            location: Location (can be None)
        
        Returns:
            list: List of search query strings
        """
        if location:
            # Location-specific strategies - simplified and more effective
            strategies = [
                # Direct and simple approaches first
                f'{company} recruiter {location}',
                f'{company} hiring {location}',
                f'{company} talent {location}',
                f'{company} {location} recruiter',
                f'{company} {location} hiring manager',
                f'recruiter {company} {location}',
                f'hiring manager {company} {location}',
                # Broader approaches
                f'{company} recruiter',
                f'{company} hiring manager',
                f'{company} talent acquisition'
            ]
        else:
            # Base strategies when no location specified - keep simple
            strategies = [
                f'{company} recruiter',
                f'{company} hiring manager', 
                f'{company} talent acquisition',
                f'{company} hr manager',
                f'{company} people partner',
                f'recruiter {company}',
                f'hiring manager {company}',
                f'talent acquisition {company}'
            ]
        
        return strategies
    
    def test_search(self, company_name="Google", timeout=30):
        """
        Test the Custom Search Engine configuration
        
        Args:
            company_name: Company name to test with
            timeout: Request timeout in seconds
        
        Returns:
            dict: Test results with status and response data
        """
        try:
            company, location = self._parse_company_and_location(company_name)
            
            search_query = f'recruiter "{company}"'
            if location:
                search_query += f' {location}'
            
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': search_query,
                'num': 5,
                'safe': 'off'
            }
            
            response = requests.get(self.base_url, params=params, timeout=timeout)
            
            return {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "search_engine_id": self.search_engine_id,
                "api_key_length": len(self.api_key) if self.api_key else 0,
                "parsed_company": company,
                "parsed_location": location,
                "search_query": search_query
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "search_engine_id": self.search_engine_id,
                "api_key_configured": bool(self.api_key)
            }
    
    def _perform_search(self, query, max_results, timeout, location=None):
        """
        Perform a single search query with location awareness
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            timeout: Request timeout
            location: Location filter (optional)
        
        Returns:
            list: List of search results
        """
        # First try without site restriction to see if we get any results
        params_basic = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': f'site:linkedin.com/in/ {query}',
            'num': min(max_results, 10),  # API limit is 10 per request
            'safe': 'off'
        }
        
        # Try with more flexible parameters first
        params_flexible = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': min(max_results, 10),
            'safe': 'off'
        }
        
        # Add location-based parameters if available
        if location:
            location_lower = location.lower()
            
            # Map common locations to country codes for better targeting
            country_mapping = {
                'india': 'IN',
                'usa': 'US',
                'uk': 'GB',
                'canada': 'CA',
                'australia': 'AU',
                'germany': 'DE',
                'france': 'FR',
                'singapore': 'SG',
                'japan': 'JP',
                'china': 'CN',
                'brazil': 'BR',
                'mexico': 'MX'
            }
            
            if location_lower in country_mapping:
                params_basic['cr'] = f'country{country_mapping[location_lower]}'
                params_flexible['cr'] = f'country{country_mapping[location_lower]}'
                logger.debug(f"Added country restriction: {country_mapping[location_lower]}")
        
        # Try multiple approaches
        for attempt, params in enumerate([params_basic, params_flexible], 1):
            try:
                logger.debug(f"Attempt {attempt} with params: {params}")
                response = requests.get(self.base_url, params=params, timeout=timeout)
                
                # Log response details for debugging
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response URL: {response.url}")
                
                if response.status_code != 200:
                    logger.error(f"API Error: Status {response.status_code}, Response: {response.text}")
                    continue
                
                data = response.json()
                
                # Log search information
                if 'searchInformation' in data:
                    search_info = data['searchInformation']
                    logger.debug(f"Total results: {search_info.get('totalResults', 'Unknown')}")
                    logger.debug(f"Search time: {search_info.get('searchTime', 'Unknown')} seconds")
                
                if 'items' not in data:
                    logger.info(f"No search results found in attempt {attempt}")
                    continue
                
                logger.info(f"Found {len(data['items'])} items in attempt {attempt}")
                
                results = []
                for item in data['items']:
                    try:
                        title = item.get('title', '')
                        url = item.get('link', '')
                        snippet = item.get('snippet', '')
                        
                        # More flexible LinkedIn URL validation
                        if url and ("linkedin.com/in/" in url or "linkedin.com" in url):
                            # Enhance snippet with location info if available
                            enhanced_snippet = self._enhance_snippet_with_location(snippet, location)
                            
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": enhanced_snippet,
                                "location_searched": location
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error processing search result: {e}")
                        continue
                
                if results:
                    logger.info(f"Successfully found {len(results)} LinkedIn profiles")
                    return results
                    
            except Exception as e:
                logger.warning(f"Search attempt {attempt} failed: {e}")
                continue
        
        logger.info("No search results found in any attempt")
        return []
    
    def _enhance_snippet_with_location(self, snippet, location):
        """
        Enhance snippet with location information for better context
        
        Args:
            snippet: Original snippet text
            location: Location being searched
        
        Returns:
            str: Enhanced snippet
        """
        if not location or not snippet:
            return snippet[:200] + "..." if len(snippet) > 200 else snippet
        
        # Truncate snippet but preserve location context
        max_length = 200
        if len(snippet) <= max_length:
            return snippet
        
        # Try to keep location-related content in the snippet
        location_terms = [location.lower()]
        
        # Add related location terms
        if location.lower() == 'india':
            location_terms.extend(['mumbai', 'bangalore', 'delhi', 'hyderabad', 'chennai', 'pune', 'indian'])
        elif location.lower() == 'usa':
            location_terms.extend(['american', 'united states', 'california', 'new york', 'seattle'])
        elif location.lower() == 'uk':
            location_terms.extend(['london', 'british', 'united kingdom', 'england'])
        
        # Check if snippet contains location terms
        snippet_lower = snippet.lower()
        has_location_context = any(term in snippet_lower for term in location_terms)
        
        if has_location_context:
            # Try to preserve location context when truncating
            sentences = snippet.split('. ')
            for sentence in sentences:
                if any(term in sentence.lower() for term in location_terms):
                    if len(sentence) <= max_length:
                        return sentence + "..."
        
        # Default truncation
        return snippet[:max_length].rsplit(' ', 1)[0] + "..."

def create_search_client(api_key, search_engine_id):
    """
    Factory function to create Custom Search client
    
    Args:
        api_key: Google Custom Search API key
        search_engine_id: Custom Search Engine ID
    
    Returns:
        CustomSearchClient or None: Search client instance or None if not configured
    """
    if not api_key or not search_engine_id:
        logger.warning("Google Custom Search API not configured")
        return None
    
    try:
        return CustomSearchClient(api_key, search_engine_id)
    except Exception as e:
        logger.error(f"Failed to create search client: {e}")
        return None

def search_with_fallback(search_client, gemini_client, company_name, max_results=10):
    """
    Search for recruiters with improved fallback strategies
    Enhanced with location awareness
    
    Args:
        search_client: CustomSearchClient instance
        gemini_client: GeminiClient instance
        company_name: Company name to search for (can include location)
        max_results: Maximum number of results
    
    Returns:
        list: List of recruiter profiles
    """
    results = []
    
    # Try Google Custom Search first
    if search_client:
        try:
            results = search_client.search_recruiters(company_name, max_results)
            if results:
                return results
        except Exception as e:
            logger.error(f"Custom Search failed: {e}")
    
    # Fallback to broader Custom Search (skip Gemini for now as it gives fake results)
    if search_client and not results:
        logger.info("No results from main search, trying broader search strategies...")
        try:
            # Parse company and location for broader search
            if hasattr(search_client, '_parse_company_and_location'):
                company, location = search_client._parse_company_and_location(company_name)
            else:
                company, location = company_name, None
            
            # Try very broad searches
            broad_strategies = [
                f'{company} linkedin recruiter',
                f'{company} linkedin hiring',
                f'{company} linkedin talent',
                f'linkedin.com {company} recruiter',
                f'site:linkedin.com {company} talent acquisition',
                f'site:linkedin.com {company} hiring manager'
            ]
            
            if location:
                broad_strategies.extend([
                    f'{company} {location} linkedin recruiter',
                    f'linkedin.com {company} {location}',
                    f'site:linkedin.com {company} {location} recruiter'
                ])
            
            for strategy in broad_strategies:
                try:
                    params = {
                        'key': search_client.api_key,
                        'cx': search_client.search_engine_id,
                        'q': strategy,
                        'num': max_results,
                        'safe': 'off'
                    }
                    
                    response = requests.get(search_client.base_url, params=params, timeout=30)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if 'items' in data:
                        for item in data['items']:
                            try:
                                title = item.get('title', '')
                                url = item.get('link', '')
                                snippet = item.get('snippet', '')
                                
                                if url and "linkedin.com" in url and ("recruiter" in title.lower() or "hiring" in title.lower() or "talent" in title.lower() or "hr" in title.lower()):
                                    results.append({
                                        "title": title,
                                        "url": url,
                                        "snippet": snippet[:200] + "..." if len(snippet) > 200 else snippet,
                                        "location_searched": location
                                    })
                                    
                                    if len(results) >= max_results:
                                        break
                                        
                            except Exception as e:
                                continue
                    
                    if results:
                        logger.info(f"Broad search found {len(results)} results with strategy: {strategy}")
                        break
                        
                except Exception as e:
                    logger.warning(f"Broad search strategy failed: {strategy} - {e}")
                    continue
                        
        except Exception as e:
            logger.error(f"Broader search failed: {e}")
    
    # Note: Temporarily disabled Gemini fallback as it generates fake/generic results
    # if gemini_client and not results:
    #     logger.info("No results from Custom Search, trying Gemini API...")
    #     try:
    #         results = gemini_client.find_recruiters_with_gemini(company_name)
    #     except Exception as e:
    #         logger.error(f"Gemini search failed: {e}")
    
    logger.info(f"Final result: Found {len(results)} LinkedIn profiles")
    return results 