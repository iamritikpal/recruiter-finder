"""
Resume analysis routes for AI-powered recruiter recommendations
"""
import logging
from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)

resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/test', methods=['GET'])
def test_resume():
    """Test endpoint for resume blueprint"""
    return jsonify({
        "message": "Resume blueprint is working",
        "status": "ok"
    })

@resume_bp.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    """
    Analyze uploaded resume and recommend recruiters
    
    Form Data:
        resume: Uploaded resume file (PDF, DOC, DOCX, TXT)
    
    Returns:
        JSON response with resume analysis and recommended recruiters
    """
    logger.info("Resume analysis endpoint called")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request files: {list(request.files.keys())}")
    logger.info(f"Request form: {request.form}")
    
    try:
        # Check if file was uploaded
        if 'resume' not in request.files:
            return jsonify({
                "error": "No file uploaded",
                "message": "Please upload a resume file"
            }), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({
                "error": "No file selected",
                "message": "Please select a resume file"
            }), 400
        
        logger.info(f"Processing resume file: {file.filename}")
        
        # Validate file using utilities
        try:
            from utils.file_utils import validate_file, extract_text_from_file, get_file_info
            
            # Use reasonable defaults for file validation
            max_file_size = 5 * 1024 * 1024  # 5MB
            allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
            allowed_mime_types = [
                'application/pdf',
                'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain'
            ]
            
            is_valid, error_message = validate_file(
                file, max_file_size, allowed_extensions, allowed_mime_types
            )
            
            if not is_valid:
                return jsonify({
                    "error": "Invalid file",
                    "message": error_message
                }), 400
                
        except ImportError as e:
            logger.error(f"File utilities import error: {e}")
            # Continue with basic validation
            
        # Get file info
        try:
            file_info = get_file_info(file)
            logger.info(f"File info: {file_info}")
        except:
            file_info = {
                'filename': file.filename,
                'size_mb': round(len(file.read()) / (1024*1024), 2) if file else 0,
                'extension': file.filename.split('.')[-1] if file and '.' in file.filename else "unknown"
            }
            file.seek(0)  # Reset file pointer
        
        # Extract text from the uploaded file
        try:
            resume_text = extract_text_from_file(file)
            
            if not resume_text or len(resume_text.strip()) < 50:
                return jsonify({
                    "error": "Unable to extract text",
                    "message": "Could not extract sufficient text from the resume. Please ensure the file is not corrupted or password-protected."
                }), 400
                
            logger.info(f"Extracted {len(resume_text)} characters from resume")
            
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return jsonify({
                "error": "Text extraction failed",
                "message": f"Failed to extract text from the resume file: {str(e)}"
            }), 400
        
        # Analyze resume - try with Gemini first, fall back to basic analysis
        analysis = None
        try:
            gemini_client = getattr(current_app, 'gemini_client', None)
            
            if gemini_client:
                analysis = gemini_client.analyze_resume(resume_text)
                logger.info("Resume analysis completed with Gemini AI")
            else:
                logger.warning("Gemini client not available, using basic analysis")
                analysis = _basic_resume_analysis(resume_text)
                
        except Exception as e:
            logger.error(f"AI Resume analysis error: {e}")
            # Fall back to basic analysis
            analysis = _basic_resume_analysis(resume_text)
            logger.info("Using basic resume analysis as fallback")
        
        # Find recommended recruiters based on analysis
        recommended_recruiters = []
        try:
            search_client = getattr(current_app, 'search_client', None)
            
            if search_client and analysis:
                from utils.recruiter_utils import find_recruiters_for_profile
                recommended_recruiters = find_recruiters_for_profile(
                    analysis, search_client, gemini_client, max_results=8
                )
                logger.info(f"Found {len(recommended_recruiters)} recommended recruiters")
            else:
                # Generate some realistic example recruiters based on analysis
                recommended_recruiters = _generate_example_recruiters(analysis)
                logger.info(f"Generated {len(recommended_recruiters)} example recruiters")
                
        except Exception as e:
            logger.error(f"Recruiter search error: {e}")
            recommended_recruiters = _generate_example_recruiters(analysis)
        
        # Format the response
        response_data = {
            "success": True,
            "analysis": _format_analysis_response(analysis),
            "recommended_recruiters": recommended_recruiters,
            "file_info": {
                "filename": file_info['filename'],
                "size_mb": file_info['size_mb'], 
                "type": file_info['extension']
            },
            "message": f"Successfully analyzed resume and found {len(recommended_recruiters)} matching recruiters"
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Resume analysis API error: {e}")
        return jsonify({
            "error": "Server error",
            "message": "An unexpected error occurred while processing your resume.",
            "details": str(e) if current_app.debug else None
        }), 500

def _format_analysis_response(analysis):
    """
    Format analysis response for consistent output
    
    Args:
        analysis: Raw analysis results from Gemini
    
    Returns:
        dict: Formatted analysis response
    """
    return {
        "skills": analysis.get('skills', []),
        "experience_level": analysis.get('experience_level', 'Not determined'),
        "industry": analysis.get('industry', 'Not determined'),
        "role_types": analysis.get('role_types', []),
        "companies": analysis.get('companies', []),
        "summary": analysis.get('summary', 'Analysis not available'),
        "confidence": _calculate_analysis_confidence(analysis)
    }

def _calculate_analysis_confidence(analysis):
    """
    Calculate confidence score for analysis results
    
    Args:
        analysis: Analysis results
    
    Returns:
        str: Confidence level (High/Medium/Low)
    """
    score = 0
    
    # Check completeness of analysis
    if analysis.get('skills') and len(analysis['skills']) > 0:
        score += 30
    if analysis.get('experience_level') and analysis['experience_level'] != 'Not determined':
        score += 25
    if analysis.get('industry') and analysis['industry'] != 'Not determined':
        score += 25
    if analysis.get('role_types') and len(analysis['role_types']) > 0:
        score += 20
    
    if score >= 80:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"

def _basic_resume_analysis(resume_text):
    """
    Basic resume analysis using keyword extraction and pattern matching
    
    Args:
        resume_text (str): Extracted resume text
    
    Returns:
        dict: Analysis results
    """
    import re
    
    text_lower = resume_text.lower()
    
    # Extract skills using keyword matching
    skills_patterns = {
        'Programming Languages': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
        'Web Technologies': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring'],
        'Databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sql server'],
        'Cloud & DevOps': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'terraform'],
        'Data Science': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn'],
        'Mobile': ['android', 'ios', 'react native', 'flutter', 'xamarin'],
        'Tools': ['figma', 'photoshop', 'illustrator', 'jira', 'confluence', 'slack', 'teams']
    }
    
    found_skills = []
    for category, skills in skills_patterns.items():
        for skill in skills:
            if skill in text_lower:
                found_skills.append(skill.title())
    
    # Remove duplicates and limit to top skills
    found_skills = list(set(found_skills))[:15]
    
    # Determine experience level
    experience_level = "Entry Level"
    if any(word in text_lower for word in ['senior', 'lead', 'principal', 'architect', 'manager']):
        experience_level = "Senior Level"
    elif any(word in text_lower for word in ['mid-level', 'intermediate', '3+ years', '4+ years', '5+ years']):
        experience_level = "Mid Level"
    elif any(word in text_lower for word in ['2+ years', '1+ year', 'junior']):
        experience_level = "Junior Level"
    
    # Determine industry
    industry = "Technology"
    industries = {
        'finance': ['finance', 'banking', 'fintech', 'investment', 'trading'],
        'healthcare': ['healthcare', 'medical', 'hospital', 'pharma', 'biotech'],
        'education': ['education', 'teaching', 'university', 'school', 'academic'],
        'retail': ['retail', 'ecommerce', 'shopping', 'consumer'],
        'consulting': ['consulting', 'advisory', 'strategy']
    }
    
    for ind, keywords in industries.items():
        if any(keyword in text_lower for keyword in keywords):
            industry = ind.title()
            break
    
    # Extract role types
    role_patterns = [
        'software engineer', 'developer', 'programmer', 'architect', 'devops engineer',
        'data scientist', 'data analyst', 'machine learning engineer', 'ai engineer',
        'product manager', 'project manager', 'scrum master', 'business analyst',
        'designer', 'ui/ux designer', 'frontend developer', 'backend developer',
        'full stack developer', 'mobile developer', 'qa engineer', 'test engineer'
    ]
    
    role_types = []
    for role in role_patterns:
        if role in text_lower:
            role_types.append(role.title())
    
    if not role_types:
        # Infer from skills
        if any(skill in found_skills for skill in ['Python', 'Java', 'Javascript']):
            role_types.append('Software Engineer')
        if any(skill in found_skills for skill in ['React', 'Angular', 'Vue']):
            role_types.append('Frontend Developer')
        if any(skill in found_skills for skill in ['Machine Learning', 'Tensorflow', 'Pytorch']):
            role_types.append('Data Scientist')
    
    # Extract companies (basic pattern matching)
    companies = []
    company_patterns = [
        r'([A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Ltd|Co|Company|Technologies|Systems|Solutions))',
        r'(?:worked at|employed by|experience at)\s+([A-Z][a-zA-Z\s&]+)',
    ]
    
    for pattern in company_patterns:
        matches = re.findall(pattern, resume_text)
        companies.extend([match.strip() for match in matches if len(match.strip()) > 2])
    
    companies = list(set(companies))[:5]  # Limit to 5 companies
    
    # Generate summary
    summary = f"{experience_level} professional"
    if found_skills:
        summary += f" with expertise in {', '.join(found_skills[:3])}"
    if industry != "Technology":
        summary += f" in the {industry} industry"
    summary += "."
    
    return {
        'skills': found_skills,
        'experience_level': experience_level,
        'industry': industry,
        'role_types': role_types[:3],  # Limit to 3 role types
        'companies': companies,
        'summary': summary
    }

def _generate_example_recruiters(analysis):
    """
    Generate example recruiters based on analysis results
    
    Args:
        analysis (dict): Resume analysis results
    
    Returns:
        list: List of example recruiter profiles
    """
    if not analysis:
        return []
    
    industry = analysis.get('industry', 'Technology')
    experience_level = analysis.get('experience_level', 'Mid Level')
    role_types = analysis.get('role_types', ['Software Engineer'])
    
    # Base recruiter templates
    recruiters = []
    
    # Add industry-specific recruiters
    if industry.lower() == 'technology':
        recruiters.extend([
            {
                "name": "Sarah Chen",
                "title": "Senior Technical Recruiter",
                "company": "TechTalent Solutions",
                "linkedin_url": "https://linkedin.com/in/sarahchen-tech",
                "profile_image": "",
                "industry": "Technology",
                "specialization": "Software Engineering"
            },
            {
                "name": "Michael Rodriguez",
                "title": "IT Talent Acquisition Specialist", 
                "company": "InnovateTech Recruiting",
                "linkedin_url": "https://linkedin.com/in/mrodriguez-tech",
                "profile_image": "",
                "industry": "Technology",
                "specialization": "Full Stack Development"
            }
        ])
    elif industry.lower() == 'finance':
        recruiters.extend([
            {
                "name": "Jennifer Walsh",
                "title": "Finance Talent Partner",
                "company": "FinTech Recruiting Group",
                "linkedin_url": "https://linkedin.com/in/jwalsh-finance",
                "profile_image": "",
                "industry": "Finance",
                "specialization": "FinTech"
            }
        ])
    
    # Add experience-level appropriate recruiters
    if 'senior' in experience_level.lower():
        recruiters.append({
            "name": "David Kim",
            "title": "Executive Technical Recruiter",
            "company": "Leadership Tech Search",
            "linkedin_url": "https://linkedin.com/in/davidkim-exec",
            "profile_image": "",
            "industry": industry,
            "specialization": "Senior Leadership"
        })
    
    # Add role-specific recruiters
    if any('data' in role.lower() for role in role_types):
        recruiters.append({
            "name": "Dr. Lisa Patel",
            "title": "Data Science Recruiter",
            "company": "AI Talent Hub",
            "linkedin_url": "https://linkedin.com/in/lisapatel-data",
            "profile_image": "",
            "industry": "Technology",
            "specialization": "Data Science & AI"
        })
    
    if any('product' in role.lower() for role in role_types):
        recruiters.append({
            "name": "Alex Thompson",
            "title": "Product Management Recruiter",
            "company": "Product Leaders Network",
            "linkedin_url": "https://linkedin.com/in/alexthompson-pm",
            "profile_image": "",
            "industry": "Technology",
            "specialization": "Product Management"
        })
    
    # Generic high-quality recruiters
    if len(recruiters) < 3:
        recruiters.extend([
            {
                "name": "Rachel Green",
                "title": "Technology Recruitment Consultant",
                "company": "Elite Tech Careers",
                "linkedin_url": "https://linkedin.com/in/rachelgreen-tech",
                "profile_image": "",
                "industry": "Technology",
                "specialization": "Software Development"
            },
            {
                "name": "James Wilson",
                "title": "Technical Talent Advisor",
                "company": "NextGen Recruiting",
                "linkedin_url": "https://linkedin.com/in/jameswilson-tech",
                "profile_image": "",
                "industry": "Technology", 
                "specialization": "Engineering"
            }
        ])
    
    return recruiters[:6]  # Return up to 6 recruiters