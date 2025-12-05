"""
Gemini AI utilities for resume analysis and text processing with location support
"""
import json
import logging
import re
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini AI client for resume analysis with location-aware search"""
    
    def __init__(self, api_key, model_name='gemini-2.0-flash-exp'):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API key
            model_name: Model name to use
        """
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        
    def analyze_resume(self, resume_text, generation_config=None):
        """
        Analyze resume text using Gemini AI
        
        Args:
            resume_text: The extracted resume text
            generation_config: Generation configuration for Gemini
        
        Returns:
            dict: Analysis results with skills, experience, industry, etc.
        
        Raises:
            ValueError: If analysis fails
        """
        if not resume_text or len(resume_text.strip()) < 50:
            raise ValueError("Resume text is too short for analysis")
        
        try:
            prompt = self._build_resume_analysis_prompt(resume_text)
            
            # Default generation config if not provided
            if generation_config is None:
                generation_config = genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1000,
                    top_p=0.8,
                    top_k=40
                )
            
            logger.info(f"Analyzing resume with {self.model_name}")
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            # Parse and validate JSON response
            analysis = self._parse_gemini_response(response.text)
            logger.info("Successfully analyzed resume with Gemini")
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response text: {response.text}")
            raise ValueError("Failed to parse resume analysis")
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            raise ValueError(f"Resume analysis failed: {str(e)}")
    
    def find_recruiters_with_gemini(self, company_name, generation_config=None):
        """
        Use Gemini to find recruiter profiles for a company with location awareness
        
        Args:
            company_name: Name of the company (can include location like "Google India")
            generation_config: Generation configuration for Gemini
        
        Returns:
            list: List of recruiter profiles
        """
        try:
            # Parse company and location
            company, location = self._parse_company_and_location(company_name)
            
            prompt = self._build_recruiter_search_prompt(company, location)
            
            if generation_config is None:
                generation_config = genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1000,
                    top_p=0.8,
                    top_k=40
                )
            
            search_context = f"{company}" + (f" in {location}" if location else "")
            logger.info(f"Searching with {self.model_name} for: {search_context}")
            
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            if not response.text:
                logger.warning("Gemini API returned empty response")
                return []
            
            # Parse JSON response
            results = self._parse_gemini_response(response.text)
            
            if isinstance(results, list):
                # Add location context to results
                for result in results:
                    if location:
                        result['location_searched'] = location
                        # Enhance snippet with location context if not already present
                        snippet = result.get('snippet', '')
                        if location.lower() not in snippet.lower():
                            result['snippet'] = f"{snippet} • {location} office"
                
                logger.info(f"{self.model_name} found {len(results)} LinkedIn profiles" + (f" for {location}" if location else ""))
                return results
            else:
                logger.warning("Gemini API returned non-list response")
                return []
                
        except Exception as e:
            logger.error(f"Gemini recruiter search error: {e}")
            return []
    
    def _parse_company_and_location(self, company_input):
        """
        Parse company name and location from input string
        Same logic as in search_utils.py for consistency
        
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
    
    def _build_resume_analysis_prompt(self, resume_text):
        """Build prompt for resume analysis"""
        return f"""
        Analyze this resume and extract the following information in JSON format:

        Resume Text:
        {resume_text}

        Please analyze and return ONLY a valid JSON object with these fields:
        {{
            "skills": ["list of technical skills, programming languages, tools, frameworks"],
            "experience_level": "Junior/Mid-level/Senior/Executive",
            "industry": "primary industry focus (e.g., Software Engineering, Data Science, Marketing, etc.)",
            "role_types": ["types of roles this person is qualified for"],
            "companies": ["types/sizes of companies that would be a good fit"],
            "summary": "brief 2-3 sentence summary of the candidate's profile",
            "preferred_locations": ["any location preferences mentioned or inferred from experience"]
        }}

        Focus on:
        - Technical skills and tools mentioned
        - Years of experience (if mentioned)
        - Industry domain expertise
        - Leadership/management experience
        - Education background
        - Certifications
        - Location preferences or work history locations

        Return only the JSON object, no other text.
        """
    
    def _build_recruiter_search_prompt(self, company, location=None):
        """Build prompt for location-aware recruiter search"""
        location_context = ""
        location_examples = ""
        
        if location:
            location_context = f" specifically in {location}"
            location_examples = f"""
            Focus on recruiters who are:
            - Based in {location}
            - Working for {company}'s {location} office/division
            - Recruiting for {location}-based positions
            - Local talent acquisition teams in {location}
            """
            
            # Add location-specific guidance
            if location.lower() == 'india':
                location_examples += f"""
            - Look for recruiters in major Indian cities like Bangalore, Mumbai, Delhi, Hyderabad, Chennai, Pune
            - Include country managers and regional talent heads for India
            """
            elif location.lower() in ['usa', 'us']:
                location_examples += f"""
            - Look for recruiters in major US cities like San Francisco, New York, Seattle, Austin
            - Include regional talent heads for North America
            """
            elif location.lower() == 'uk':
                location_examples += f"""
            - Look for recruiters in London and other UK cities
            - Include European talent acquisition teams based in UK
            """
        
        return f"""
        Find LinkedIn profiles of recruiters and talent acquisition professionals at {company}{location_context}.
        
        Search for people with these job titles:
        - Technical Recruiter, Engineering Recruiter, Tech Recruiter
        - Talent Acquisition Specialist, Talent Acquisition Manager
        - Hiring Manager, Recruiting Manager, Senior Recruiter
        - People Partner, Talent Partner, Recruiting Specialist
        - Recruiting Lead, Technical Sourcer
        - HR Manager, Human Resources Business Partner
        
        {location_examples}
        
        Return ONLY a valid JSON array with this exact format:
        [
            {{
                "title": "Full Name - Job Title at {company}",
                "url": "https://linkedin.com/in/username",
                "snippet": "Brief description of their role{location_context if location else ''}"
            }}
        ]
        
        Rules:
        - Only include publicly accessible LinkedIn profiles
        - Ensure URLs are valid LinkedIn profile links
        - If no profiles found, return empty array []
        - Keep titles concise and professional
        - Focus on technical/engineering recruiting roles
        {f"- Prioritize recruiters with {location} location or {location}-specific experience" if location else ""}
        - Include location context in snippets when relevant
        """
    
    def _parse_gemini_response(self, response_text):
        """
        Parse Gemini response and extract JSON
        
        Args:
            response_text: Raw response from Gemini
        
        Returns:
            dict or list: Parsed JSON data
        
        Raises:
            json.JSONDecodeError: If JSON parsing fails
        """
        # Clean the response text to extract JSON
        text = response_text.strip()
        
        # Remove markdown formatting if present
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        text = text.strip()
        
        # Parse JSON
        return json.loads(text)

def create_gemini_client(api_key, model_name='gemini-2.0-flash-exp'):
    """
    Factory function to create Gemini client
    
    Args:
        api_key: Gemini API key
        model_name: Model name to use
    
    Returns:
        GeminiClient or None: Gemini client instance or None if API key not provided
    """
    if not api_key:
        logger.warning("Gemini API key not configured")
        return None
    
    try:
        return GeminiClient(api_key, model_name)
    except Exception as e:
        logger.error(f"Failed to create Gemini client: {e}")
        return None 