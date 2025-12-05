"""
Recruiter utilities for matching, scoring, and recommendation logic
"""
import logging

logger = logging.getLogger(__name__)

def find_recruiters_for_profile(analysis, search_client, gemini_client, max_results=8):
    """
    Find relevant recruiters based on resume analysis
    
    Args:
        analysis: Resume analysis results
        search_client: CustomSearchClient instance
        gemini_client: GeminiClient instance
        max_results: Maximum number of recruiters to return
    
    Returns:
        list: List of recommended recruiters with match scores
    """
    try:
        # Determine target companies based on analysis
        target_companies = _get_target_companies(analysis)
        
        all_recruiters = []
        
        # Search for recruiters at each target company
        for company in target_companies:
            logger.info(f"Searching for recruiters at {company} for profile match")
            
            try:
                # Use the search utilities with fallback
                from utils.search_utils import search_with_fallback
                recruiters = search_with_fallback(search_client, gemini_client, company)
                
                # Add match scoring and reasoning
                for recruiter in recruiters:
                    match_score, match_reason = calculate_match_score(recruiter, analysis)
                    recruiter['match_score'] = match_score
                    recruiter['match_reason'] = match_reason
                    recruiter['target_company'] = company
                    
                all_recruiters.extend(recruiters)
                
            except Exception as e:
                logger.warning(f"Failed to search recruiters for {company}: {e}")
                continue
        
        # Sort by match score and return top matches
        all_recruiters.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Return top matches
        return all_recruiters[:max_results]
        
    except Exception as e:
        logger.error(f"Error finding recruiters for profile: {e}")
        return []

def _get_target_companies(analysis):
    """
    Determine target companies based on resume analysis
    
    Args:
        analysis: Resume analysis results
    
    Returns:
        list: List of target company names
    """
    target_companies = []
    
    # Add industry-specific companies
    industry = analysis.get('industry', '').lower()
    
    if 'software' in industry or 'engineering' in industry or 'tech' in industry:
        target_companies.extend(['Google', 'Microsoft', 'Apple', 'Amazon', 'Meta', 'Netflix', 'Uber'])
    elif 'data' in industry or 'analytics' in industry:
        target_companies.extend(['Google', 'Microsoft', 'Amazon', 'Netflix', 'Airbnb', 'Spotify'])
    elif 'marketing' in industry:
        target_companies.extend(['Google', 'Meta', 'Adobe', 'Salesforce', 'HubSpot'])
    elif 'finance' in industry or 'fintech' in industry:
        target_companies.extend(['JPMorgan', 'Goldman Sachs', 'Stripe', 'Square', 'PayPal'])
    elif 'healthcare' in industry or 'biotech' in industry:
        target_companies.extend(['Johnson & Johnson', 'Pfizer', 'Moderna', 'Genentech'])
    elif 'automotive' in industry:
        target_companies.extend(['Tesla', 'Ford', 'General Motors', 'BMW'])
    elif 'retail' in industry or 'ecommerce' in industry:
        target_companies.extend(['Amazon', 'Shopify', 'Walmart', 'Target'])
    else:
        # Default to major tech companies
        target_companies.extend(['Google', 'Microsoft', 'Apple', 'Amazon', 'Meta'])
    
    # Add companies based on experience level
    experience_level = analysis.get('experience_level', '').lower()
    if 'senior' in experience_level or 'executive' in experience_level:
        target_companies.extend(['Apple', 'Microsoft', 'Google', 'Amazon'])
    elif 'junior' in experience_level:
        target_companies.extend(['Uber', 'Airbnb', 'Spotify', 'Slack', 'Dropbox'])
    
    # Add companies mentioned in the analysis
    companies_from_analysis = analysis.get('companies', [])
    if companies_from_analysis:
        target_companies.extend(companies_from_analysis)
    
    # Remove duplicates and limit to top companies
    target_companies = list(set(target_companies))[:5]
    
    logger.info(f"Target companies for profile: {target_companies}")
    return target_companies

def calculate_match_score(recruiter, analysis):
    """
    Calculate match score between recruiter and candidate profile with location awareness
    
    Args:
        recruiter: Recruiter profile data
        analysis: Resume analysis results
    
    Returns:
        tuple: (match_score, match_reason)
    """
    try:
        score = 60  # Base score
        reasons = []
        
        title = recruiter.get('title', '').lower()
        snippet = recruiter.get('snippet', '').lower()
        recruiter_text = f"{title} {snippet}"
        
        # Check for location match if location was searched
        location_searched = recruiter.get('location_searched')
        if location_searched:
            location_lower = location_searched.lower()
            
            # Check if recruiter profile mentions the location
            location_terms = _get_location_terms(location_lower)
            if any(term in recruiter_text for term in location_terms):
                score += 15
                reasons.append(f"{location_searched} location match")
        
        # Check for industry match
        industry = analysis.get('industry', '').lower()
        industry_keywords = _get_industry_keywords(industry)
        
        if any(keyword in recruiter_text for keyword in industry_keywords):
            score += 20
            reasons.append(f"{industry.title()} recruiting focus")
        
        # Check for experience level match
        experience_level = analysis.get('experience_level', '').lower()
        if 'senior' in experience_level and any(keyword in recruiter_text for keyword in ['senior', 'lead', 'principal', 'staff']):
            score += 15
            reasons.append("Senior-level focus")
        elif 'junior' in experience_level and any(keyword in recruiter_text for keyword in ['entry', 'junior', 'new grad', 'early career']):
            score += 15
            reasons.append("Entry-level focus")
        elif 'executive' in experience_level and any(keyword in recruiter_text for keyword in ['executive', 'c-level', 'vp', 'director']):
            score += 20
            reasons.append("Executive-level focus")
        
        # Check for specific skills match
        skills = analysis.get('skills', [])
        skill_matches = _check_skill_matches(skills, recruiter_text)
        
        if skill_matches:
            score += min(15, len(skill_matches) * 3)  # Max 15 points for skills
            reasons.append(f"Skills alignment ({', '.join(skill_matches[:3])})")
        
        # Check for role type match
        role_types = analysis.get('role_types', [])
        role_matches = _check_role_matches(role_types, recruiter_text)
        
        if role_matches:
            score += 10
            reasons.append("Role type alignment")
        
        # Check for company type/size match
        if 'startup' in recruiter_text and any('startup' in company.lower() for company in analysis.get('companies', [])):
            score += 5
            reasons.append("Startup focus")
        elif 'enterprise' in recruiter_text and any('enterprise' in company.lower() for company in analysis.get('companies', [])):
            score += 5
            reasons.append("Enterprise focus")
        
        # Check for preferred location match from resume analysis
        preferred_locations = analysis.get('preferred_locations', [])
        if location_searched and preferred_locations:
            for pref_location in preferred_locations:
                if location_searched.lower() in pref_location.lower() or pref_location.lower() in location_searched.lower():
                    score += 10
                    reasons.append("Preferred location alignment")
                    break
        
        # Bonus for HR/People roles when location is specified (local knowledge important)
        if location_searched and any(keyword in recruiter_text for keyword in ['hr', 'human resources', 'people partner']):
            score += 5
            reasons.append("Local HR expertise")
        
        # Ensure score doesn't exceed 100
        score = min(score, 95)
        
        # Create match reason string
        if reasons:
            match_reason = "; ".join(reasons)
        else:
            match_reason = "General recruiter match"
        
        return score, match_reason
        
    except Exception as e:
        logger.error(f"Error calculating match score: {e}")
        return 70, "Profile alignment"

def _get_industry_keywords(industry):
    """Get relevant keywords for industry matching"""
    industry_map = {
        'software': ['technical', 'engineering', 'software', 'developer', 'tech'],
        'engineering': ['technical', 'engineering', 'software', 'developer', 'tech'],
        'data science': ['data', 'analytics', 'machine learning', 'ai', 'scientist'],
        'marketing': ['marketing', 'digital', 'growth', 'brand', 'content'],
        'finance': ['finance', 'fintech', 'banking', 'financial', 'investment'],
        'healthcare': ['healthcare', 'medical', 'biotech', 'pharmaceutical', 'clinical'],
        'sales': ['sales', 'business development', 'account', 'revenue'],
        'product': ['product', 'design', 'ux', 'ui', 'user experience'],
        'operations': ['operations', 'logistics', 'supply chain', 'process']
    }
    
    for key, keywords in industry_map.items():
        if key in industry.lower():
            return keywords
    
    return ['technical', 'engineering']  # Default

def _check_skill_matches(skills, recruiter_text):
    """Check for skill matches between candidate and recruiter focus"""
    skill_keywords = {
        'python': ['python', 'django', 'flask'],
        'javascript': ['javascript', 'js', 'node', 'react', 'angular', 'vue'],
        'java': ['java', 'spring', 'kotlin'],
        'aws': ['aws', 'amazon web services', 'cloud'],
        'react': ['react', 'frontend'],
        'machine learning': ['ml', 'machine learning', 'ai', 'artificial intelligence'],
        'data science': ['data', 'analytics', 'science'],
        'devops': ['devops', 'infrastructure', 'deployment'],
        'mobile': ['mobile', 'ios', 'android', 'react native', 'flutter'],
        'backend': ['backend', 'server', 'api'],
        'frontend': ['frontend', 'ui', 'ux']
    }
    
    matches = []
    for skill in skills:
        skill_lower = skill.lower()
        for category, keywords in skill_keywords.items():
            if any(keyword in skill_lower for keyword in keywords):
                if any(keyword in recruiter_text for keyword in keywords):
                    matches.append(category)
                break
    
    return list(set(matches))  # Remove duplicates

def _check_role_matches(role_types, recruiter_text):
    """Check for role type matches"""
    role_keywords = {
        'engineer': ['engineer', 'developer', 'technical'],
        'manager': ['manager', 'lead', 'director'],
        'designer': ['designer', 'ux', 'ui'],
        'analyst': ['analyst', 'data'],
        'scientist': ['scientist', 'research'],
        'consultant': ['consultant', 'advisory']
    }
    
    for role in role_types:
        role_lower = role.lower()
        for category, keywords in role_keywords.items():
            if category in role_lower:
                if any(keyword in recruiter_text for keyword in keywords):
                    return True
    
    return False

def format_recruiter_profile(recruiter):
    """
    Format recruiter profile for consistent display
    
    Args:
        recruiter: Raw recruiter profile data
    
    Returns:
        dict: Formatted recruiter profile
    """
    return {
        'title': recruiter.get('title', '').replace('\s+', ' ').strip(),
        'url': recruiter.get('url', ''),
        'snippet': _truncate_snippet(recruiter.get('snippet', '')),
        'match_score': recruiter.get('match_score', 0),
        'match_reason': recruiter.get('match_reason', ''),
        'target_company': recruiter.get('target_company', '')
    }

def _truncate_snippet(snippet, max_length=200):
    """Truncate snippet to max length with ellipsis"""
    if len(snippet) <= max_length:
        return snippet
    return snippet[:max_length].rsplit(' ', 1)[0] + "..."

def validate_recruiter_profile(recruiter):
    """
    Validate recruiter profile data
    
    Args:
        recruiter: Recruiter profile data
    
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['title', 'url']
    
    # Check required fields
    for field in required_fields:
        if not recruiter.get(field):
            return False
    
    # Validate LinkedIn URL
    url = recruiter.get('url', '')
    if not url.startswith('https://linkedin.com/in/') and not url.startswith('https://www.linkedin.com/in/'):
        return False
    
    return True 

def _get_location_terms(location):
    """
    Get related location terms for better matching
    
    Args:
        location: Primary location
    
    Returns:
        list: List of related location terms
    """
    location_map = {
        'india': ['india', 'indian', 'mumbai', 'bangalore', 'delhi', 'hyderabad', 'chennai', 'pune', 'gurgaon', 'noida'],
        'usa': ['usa', 'us', 'united states', 'american', 'california', 'new york', 'seattle', 'texas', 'bay area', 'silicon valley'],
        'uk': ['uk', 'united kingdom', 'british', 'london', 'england', 'scotland', 'wales'],
        'canada': ['canada', 'canadian', 'toronto', 'vancouver', 'montreal', 'ottawa'],
        'australia': ['australia', 'australian', 'sydney', 'melbourne', 'brisbane', 'perth'],
        'germany': ['germany', 'german', 'berlin', 'munich', 'hamburg', 'frankfurt'],
        'france': ['france', 'french', 'paris', 'lyon', 'marseille'],
        'singapore': ['singapore', 'singaporean'],
        'japan': ['japan', 'japanese', 'tokyo', 'osaka', 'kyoto'],
        'china': ['china', 'chinese', 'beijing', 'shanghai', 'shenzhen', 'guangzhou'],
        'brazil': ['brazil', 'brazilian', 'sao paulo', 'rio de janeiro', 'brasilia'],
        'mexico': ['mexico', 'mexican', 'mexico city', 'guadalajara', 'monterrey'],
        
        # Cities
        'bangalore': ['bangalore', 'bengaluru', 'blr', 'karnataka'],
        'mumbai': ['mumbai', 'bombay', 'maharashtra'],
        'delhi': ['delhi', 'new delhi', 'ncr', 'gurgaon', 'noida'],
        'hyderabad': ['hyderabad', 'telangana', 'andhra pradesh'],
        'chennai': ['chennai', 'madras', 'tamil nadu'],
        'pune': ['pune', 'maharashtra'],
        'london': ['london', 'uk', 'england', 'britain'],
        'new york': ['new york', 'nyc', 'manhattan', 'brooklyn'],
        'san francisco': ['san francisco', 'sf', 'bay area', 'silicon valley'],
        'seattle': ['seattle', 'washington', 'redmond'],
        'toronto': ['toronto', 'ontario', 'gta'],
        'sydney': ['sydney', 'nsw', 'new south wales'],
        'berlin': ['berlin', 'germany'],
        'paris': ['paris', 'france'],
        'tokyo': ['tokyo', 'japan'],
        'beijing': ['beijing', 'china'],
        'shanghai': ['shanghai', 'china'],
        'sao paulo': ['sao paulo', 'brazil']
    }
    
    return location_map.get(location.lower(), [location.lower()]) 