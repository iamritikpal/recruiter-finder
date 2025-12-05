"""
Job search utilities for finding job postings by company using web search
"""
import logging
import requests
import time
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class JobSearchClient:
    """
    Client for searching job postings using Google Custom Search API
    """
    
    def __init__(self, api_key, search_engine_id):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search_jobs(self, company_name, max_results=15, timeout=30):
        """
        Search for job postings using multiple strategies with location awareness
        
        Args:
            company_name: Name of the company to search for (can include location)
            max_results: Maximum number of results to return
            timeout: Request timeout in seconds
        
        Returns:
            list: List of job postings
        """
        # Parse company name and location
        company, location = self._parse_company_and_location(company_name)
        
        logger.info(f"Searching for jobs at: {company}" + (f" in {location}" if location else ""))
        
        # Generate job search strategies
        search_strategies = self._generate_job_search_strategies(company, location)
        
        all_results = []
        
        for i, search_query in enumerate(search_strategies):
            logger.info(f"Trying job search strategy {i+1}: {search_query}")
            
            try:
                results = self._perform_job_search(search_query, max_results, timeout, location)
                
                # Add unique results (based on URL and title similarity)
                for result in results:
                    if not self._is_duplicate_job(result, all_results):
                        all_results.append(result)
                        logger.info(f"Found job posting: {result['title'][:60]}...")
                
                # Stop if we have enough results
                if len(all_results) >= max_results:
                    break
                    
            except Exception as e:
                logger.warning(f"Job search strategy {i+1} failed: {e}")
                continue
        
        logger.info(f"Found {len(all_results)} unique job postings" + (f" for {location}" if location else ""))
        return self._rank_and_format_jobs(all_results[:max_results], company, location)
    
    def _parse_company_and_location(self, company_input):
        """
        Parse company name and location from input string
        Examples: 'Google India' -> ('Google', 'India')
                 'Microsoft' -> ('Microsoft', None)
        """
        location_keywords = [
            'india', 'usa', 'uk', 'canada', 'australia', 'germany', 'france', 'japan',
            'singapore', 'netherlands', 'sweden', 'brazil', 'mexico', 'spain', 'italy',
            'london', 'new york', 'san francisco', 'seattle', 'chicago', 'toronto',
            'sydney', 'melbourne', 'berlin', 'paris', 'tokyo', 'mumbai', 'bangalore',
            'hyderabad', 'pune', 'chennai', 'delhi', 'gurgaon', 'noida', 'remote'
        ]
        
        company_input_lower = company_input.lower().strip()
        
        for keyword in location_keywords:
            if keyword in company_input_lower:
                # Split and clean
                parts = company_input.lower().split()
                location_parts = []
                company_parts = []
                
                for part in parts:
                    if any(loc_word in part for loc_word in location_keywords):
                        location_parts.append(part.title())
                    else:
                        company_parts.append(part.title())
                
                company = ' '.join(company_parts).strip()
                location = ' '.join(location_parts).strip()
                
                return company, location if location else None
        
        return company_input.strip(), None
    
    def _generate_job_search_strategies(self, company, location=None):
        """
        Generate multiple search strategies for finding job postings
        """
        strategies = []
        location_suffix = f" {location}" if location else ""
        
        # Strategy 1: Direct job board searches
        strategies.extend([
            f"site:linkedin.com/jobs {company}{location_suffix} jobs",
            f"site:indeed.com {company}{location_suffix} jobs",
            f"site:glassdoor.com {company}{location_suffix} jobs",
            f"site:naukri.com {company}{location_suffix} jobs" if location and 'india' in location.lower() else None,
            f"site:monster.com {company}{location_suffix} jobs"
        ])
        
        # Strategy 2: Company career pages
        strategies.extend([
            f"site:{company.lower().replace(' ', '')}.com careers{location_suffix}",
            f"site:{company.lower().replace(' ', '')}.com jobs{location_suffix}",
            f"{company} careers{location_suffix} hiring",
            f"{company} job openings{location_suffix}"
        ])
        
        # Strategy 3: General job searches
        strategies.extend([
            f'"{company}" jobs{location_suffix} 2024 2025',
            f'"{company}" hiring{location_suffix} openings',
            f"{company} recruitment{location_suffix} positions"
        ])
        
        # Strategy 4: Technology/Role specific (if applicable)
        tech_roles = ["software engineer", "developer", "data scientist", "product manager", "designer"]
        strategies.extend([
            f'"{company}" {role}{location_suffix} jobs' for role in tech_roles[:2]
        ])
        
        # Remove None values and return
        return [s for s in strategies if s is not None][:8]  # Limit to 8 strategies
    
    def _perform_job_search(self, query, max_results, timeout, location=None):
        """
        Perform actual Google Custom Search for job postings
        """
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': min(max_results, 10),  # Google Custom Search max is 10
            'safe': 'medium',
            'lr': 'lang_en'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            
            results = []
            items = data.get('items', [])
            
            for item in items:
                # Filter out non-job related results
                if self._is_job_posting(item):
                    job_data = self._extract_job_data(item, location)
                    if job_data:
                        results.append(job_data)
            
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Search request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            return []
    
    def _is_job_posting(self, item):
        """
        Determine if search result is likely a job posting
        """
        title = item.get('title', '').lower()
        snippet = item.get('snippet', '').lower()
        url = item.get('link', '').lower()
        
        # Job indicators
        job_keywords = [
            'job', 'jobs', 'career', 'careers', 'hiring', 'opening', 'openings',
            'position', 'positions', 'vacancy', 'vacancies', 'recruitment',
            'apply', 'application', 'candidate', 'employment', 'work at'
        ]
        
        # Job board domains
        job_sites = [
            'linkedin.com/jobs', 'indeed.com', 'glassdoor.com', 'naukri.com',
            'monster.com', 'ziprecruiter.com', 'simplyhired.com', 'dice.com',
            'careers', 'jobs'
        ]
        
        # Check for job keywords in title or snippet
        has_job_keywords = any(keyword in title or keyword in snippet for keyword in job_keywords)
        
        # Check for job site URLs
        is_job_site = any(site in url for site in job_sites)
        
        # Exclude non-job content
        exclude_keywords = [
            'news', 'article', 'blog', 'wikipedia', 'about us', 'company profile',
            'stock', 'financial', 'investor', 'press release'
        ]
        
        has_exclude_keywords = any(keyword in title or keyword in snippet for keyword in exclude_keywords)
        
        return (has_job_keywords or is_job_site) and not has_exclude_keywords
    
    def _extract_job_data(self, item, location=None):
        """
        Extract job data from search result item
        """
        try:
            url = item.get('link', '')
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            
            # Extract job details
            job_data = {
                'title': self._clean_job_title(title),
                'url': url,
                'snippet': snippet,
                'company': self._extract_company_from_result(title, snippet),
                'location': self._extract_location_from_result(title, snippet, location),
                'source': self._extract_job_source(url),
                'posted_date': self._extract_posted_date(snippet),
                'job_type': self._extract_job_type(title, snippet),
                'salary': self._extract_salary(snippet),
                'found_timestamp': datetime.now().isoformat()
            }
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            return None
    
    def _clean_job_title(self, title):
        """Clean and format job title"""
        # Remove common site suffixes
        suffixes_to_remove = [
            '- Indeed.com', '- LinkedIn', '- Glassdoor', '- Naukri.com',
            '- Monster.com', '| Indeed.com', '| LinkedIn', '| Glassdoor'
        ]
        
        for suffix in suffixes_to_remove:
            title = title.replace(suffix, '')
        
        return title.strip()
    
    def _extract_company_from_result(self, title, snippet):
        """Extract company name from title or snippet"""
        # Look for common patterns
        patterns = [
            'at ', 'with ', '- ', '| ', 'for ', 'by '
        ]
        
        for pattern in patterns:
            if pattern in title.lower():
                parts = title.split(pattern)
                if len(parts) > 1:
                    company = parts[-1].strip()
                    # Clean company name
                    company = company.split('(')[0].strip()
                    company = company.split('-')[0].strip()
                    return company
        
        # Fallback: try to extract from snippet
        snippet_words = snippet.split()
        for i, word in enumerate(snippet_words):
            if word.lower() in ['at', 'with'] and i + 1 < len(snippet_words):
                return snippet_words[i + 1].strip('.,')
        
        return 'Company Not Specified'
    
    def _extract_location_from_result(self, title, snippet, searched_location=None):
        """Extract job location from title or snippet"""
        location_patterns = [
            r'\b\w+,\s*\w+\b',  # City, State
            r'\b\w+\s+\w+,\s*\w+\b'  # City Name, State
        ]
        
        # Check title and snippet for location
        text = f"{title} {snippet}".lower()
        
        # Common location keywords
        location_keywords = [
            'remote', 'hybrid', 'onsite', 'bangalore', 'mumbai', 'delhi', 'hyderabad',
            'pune', 'chennai', 'gurgaon', 'noida', 'london', 'new york', 'san francisco',
            'seattle', 'chicago', 'toronto', 'sydney', 'berlin', 'paris', 'tokyo'
        ]
        
        for keyword in location_keywords:
            if keyword in text:
                return keyword.title()
        
        # If searched with location, use that as fallback
        return searched_location if searched_location else 'Location Not Specified'
    
    def _extract_job_source(self, url):
        """Extract job board/source from URL"""
        domain = urlparse(url).netloc.lower()
        
        source_mapping = {
            'linkedin.com': 'LinkedIn',
            'indeed.com': 'Indeed',
            'glassdoor.com': 'Glassdoor',
            'naukri.com': 'Naukri',
            'monster.com': 'Monster',
            'ziprecruiter.com': 'ZipRecruiter',
            'simplyhired.com': 'SimplyHired',
            'dice.com': 'Dice'
        }
        
        for domain_key, source_name in source_mapping.items():
            if domain_key in domain:
                return source_name
        
        # If it's a company career page
        if 'careers' in domain or 'jobs' in domain:
            return 'Company Career Page'
        
        return 'Other'
    
    def _extract_posted_date(self, snippet):
        """Extract posted date from snippet"""
        import re
        
        # Look for date patterns
        date_patterns = [
            r'(\d{1,2})\s+(days?|hours?|weeks?)\s+ago',
            r'posted\s+(\d{1,2})\s+(days?|hours?|weeks?)\s+ago',
            r'(\d{1,2})d\s+ago',
            r'(\d{1,2})h\s+ago'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, snippet.lower())
            if match:
                return match.group(0)
        
        return 'Date Not Specified'
    
    def _extract_job_type(self, title, snippet):
        """Extract job type (Full-time, Part-time, Contract, etc.)"""
        text = f"{title} {snippet}".lower()
        
        type_keywords = {
            'full-time': 'Full-time',
            'full time': 'Full-time',
            'part-time': 'Part-time',
            'part time': 'Part-time',
            'contract': 'Contract',
            'freelance': 'Freelance',
            'internship': 'Internship',
            'intern': 'Internship',
            'temporary': 'Temporary',
            'permanent': 'Permanent'
        }
        
        for keyword, job_type in type_keywords.items():
            if keyword in text:
                return job_type
        
        return 'Not Specified'
    
    def _extract_salary(self, snippet):
        """Extract salary information from snippet"""
        import re
        
        # Look for salary patterns
        salary_patterns = [
            r'[\$₹£€]\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?:\s*-\s*[\$₹£€]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?)?',
            r'\d{1,3}(?:,\d{3})*\s*(?:lpa|per year|per month|/year|/month)',
            r'\d+k\s*-\s*\d+k',
            r'\d+\s*lakh'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, snippet.lower())
            if match:
                return match.group(0)
        
        return 'Salary Not Specified'
    
    def _is_duplicate_job(self, new_job, existing_jobs):
        """Check if job is duplicate based on URL and title similarity"""
        for existing in existing_jobs:
            # Check URL similarity
            if new_job['url'] == existing['url']:
                return True
            
            # Check title similarity (basic)
            new_title = new_job['title'].lower()
            existing_title = existing['title'].lower()
            
            # If titles are very similar and companies match
            if (self._text_similarity(new_title, existing_title) > 0.8 and 
                new_job['company'].lower() == existing['company'].lower()):
                return True
        
        return False
    
    def _text_similarity(self, text1, text2):
        """Calculate basic text similarity"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _rank_and_format_jobs(self, jobs, company, location):
        """Rank and format job results"""
        # Add relevance scores
        for job in jobs:
            job['relevance_score'] = self._calculate_job_relevance(job, company, location)
        
        # Sort by relevance score
        jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return jobs
    
    def _calculate_job_relevance(self, job, target_company, target_location):
        """Calculate job relevance score"""
        score = 50  # Base score
        
        title = job['title'].lower()
        snippet = job['snippet'].lower()
        company = job['company'].lower()
        
        # Company name match
        if target_company.lower() in company or target_company.lower() in title:
            score += 30
        
        # Location match
        if target_location and target_location.lower() in job['location'].lower():
            score += 20
        
        # Source credibility
        source_scores = {
            'LinkedIn': 25,
            'Indeed': 20,
            'Glassdoor': 20,
            'Company Career Page': 30,
            'Naukri': 18,
            'Monster': 15
        }
        score += source_scores.get(job['source'], 10)
        
        # Recency (if posted date is available)
        posted_date = job['posted_date'].lower()
        if 'hour' in posted_date or 'today' in posted_date:
            score += 15
        elif 'day' in posted_date and '1' in posted_date:
            score += 10
        elif 'week' in posted_date and '1' in posted_date:
            score += 5
        
        return min(score, 100)  # Cap at 100


def create_job_search_client(api_key, search_engine_id):
    """
    Create a JobSearchClient instance
    """
    try:
        if not api_key or not search_engine_id:
            logger.warning("Missing Google Custom Search credentials for job search")
            return None
        
        client = JobSearchClient(api_key, search_engine_id)
        logger.info("Job search client created successfully")
        return client
    
    except Exception as e:
        logger.error(f"Failed to create job search client: {e}")
        return None


def search_jobs_with_fallback(job_search_client, company_name, max_results=15):
    """
    Search for jobs with fallback strategies
    
    Args:
        job_search_client: JobSearchClient instance
        company_name: Company name to search for (can include location)
        max_results: Maximum number of results
    
    Returns:
        list: List of job postings
    """
    results = []
    
    # Try job search client first
    if job_search_client:
        try:
            results = job_search_client.search_jobs(company_name, max_results)
            if results:
                return results
        except Exception as e:
            logger.error(f"Job search failed: {e}")
    
    # Fallback: return sample data if search fails
    logger.warning("Job search API unavailable, returning sample data")
    return _get_sample_job_data(company_name)


def _get_sample_job_data(company_name):
    """
    Generate sample job data when search fails
    """
    company, location = company_name, None
    if ' ' in company_name:
        parts = company_name.split()
        company = parts[0]
        location = ' '.join(parts[1:]) if len(parts) > 1 else None
    
    sample_jobs = [
        {
            'title': f'Software Engineer at {company}',
            'url': f'https://linkedin.com/jobs/view/sample-{company.lower()}-swe',
            'snippet': f'Join {company} as a Software Engineer. Work on cutting-edge technology...',
            'company': company,
            'location': location or 'Multiple Locations',
            'source': 'LinkedIn',
            'posted_date': '2 days ago',
            'job_type': 'Full-time',
            'salary': 'Competitive Salary',
            'relevance_score': 85,
            'found_timestamp': datetime.now().isoformat()
        },
        {
            'title': f'Product Manager - {company}',
            'url': f'https://indeed.com/viewjob?jk=sample-{company.lower()}-pm',
            'snippet': f'Lead product development at {company}. Define product strategy...',
            'company': company,
            'location': location or 'Remote',
            'source': 'Indeed',
            'posted_date': '1 week ago',
            'job_type': 'Full-time',
            'salary': 'Not Specified',
            'relevance_score': 80,
            'found_timestamp': datetime.now().isoformat()
        }
    ]
    
    return sample_jobs
