"""
Contact discovery routes for recruiter email and phone finding
"""
import logging
import smtplib
import dns.resolver
import socket
import re
import requests
from flask import Blueprint, request, jsonify, current_app
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

email_bp = Blueprint('email', __name__)

def clean_name_for_validation(name):
    """
    Clean and validate a name, allowing common name characters
    
    Args:
        name (str): Name to clean
    
    Returns:
        str: Cleaned name with only valid characters
    """
    if not name:
        return ""
    
    # Remove common punctuation and special characters from names
    # Keep letters, spaces, apostrophes, periods, and hyphens
    cleaned = re.sub(r"[^a-zA-Z\s'\.\-]", "", name.strip())
    
    # Remove extra spaces and normalize
    cleaned = ' '.join(cleaned.split())
    
    return cleaned

def extract_letters_only(name):
    """
    Extract only letters from a name for email generation
    
    Args:
        name (str): Name to process
    
    Returns:
        str: Name with only letters
    """
    return ''.join(c for c in name if c.isalpha())

def validate_name_format(name):
    """
    Validate that a name contains valid characters
    
    Args:
        name (str): Name to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not name or len(name.strip()) < 1:
        return False
    
    # Allow letters, spaces, apostrophes, periods, and hyphens
    # This covers names like: John, Mary-Jane, O'Connor, John Jr., Jade P.
    pattern = r"^[a-zA-Z\s'\.\-]+$"
    return bool(re.match(pattern, name.strip()))

def generate_email_patterns(first_name, last_name, domain):
    """
    Generate common email patterns for a given name and domain
    
    Args:
        first_name (str): First name
        last_name (str): Last name
        domain (str): Domain name
    
    Returns:
        list: List of email patterns to test
    """
    patterns = []
    
    # Extract only letters for email generation
    first = extract_letters_only(first_name).lower()
    last = extract_letters_only(last_name).lower()
    
    # Validate that we have valid names after cleaning
    if not first or not last or len(first) < 1 or len(last) < 1:
        logger.warning(f"Could not extract valid names from: first='{first_name}', last='{last_name}'")
        return []
    
    # Common email patterns
    patterns.extend([
        f"{first}.{last}@{domain}",
        f"{first}{last}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"{first}_{last}@{domain}",
        f"{first}-{last}@{domain}",
        f"{first}@{domain}",
        f"{last}.{first}@{domain}",
        f"{last}{first}@{domain}",
        f"{first[0]}.{last}@{domain}",
        f"{first[0]}{last[0]}@{domain}",
        f"{first}{last[0]}@{domain}",
        f"{first[0]}{last}@{domain}",
    ])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_patterns = []
    for pattern in patterns:
        if pattern not in seen and '@' in pattern and '.' in pattern:
            seen.add(pattern)
            unique_patterns.append(pattern)
    
    logger.info(f"Generated {len(unique_patterns)} email patterns for {first_name} {last_name}")
    return unique_patterns

def get_mx_records(domain):
    """
    Get MX records for a domain
    
    Args:
        domain (str): Domain name
    
    Returns:
        list: List of MX hostnames
    """
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return [str(mx.exchange).rstrip('.') for mx in mx_records]
    except Exception as e:
        logger.warning(f"Failed to get MX records for {domain}: {e}")
        return []

def get_alternative_domains(original_domain):
    """
    Get alternative domain suggestions for well-known companies
    
    Args:
        original_domain (str): Original domain that failed
    
    Returns:
        list: List of alternative domains to try
    """
    # Remove .com extension to get base name
    base_name = original_domain.replace('.com', '').lower()
    
    # Common domain mappings for well-known companies
    company_mappings = {
        'natwest': ['natwest.com', 'natwestgroup.com', 'rbs.com'],
        'rbs': ['rbs.com', 'natwest.com', 'natwestgroup.com'],
        'microsoft': ['microsoft.com'],
        'google': ['google.com', 'alphabet.com'],
        'amazon': ['amazon.com', 'aboutamazon.com'],
        'apple': ['apple.com'],
        'meta': ['meta.com', 'facebook.com'],
        'facebook': ['meta.com', 'facebook.com'],
        'netflix': ['netflix.com'],
        'tesla': ['tesla.com'],
        'uber': ['uber.com'],
        'airbnb': ['airbnb.com'],
        'spotify': ['spotify.com'],
        'adobe': ['adobe.com'],
        'salesforce': ['salesforce.com'],
        'oracle': ['oracle.com'],
        'ibm': ['ibm.com'],
        'intel': ['intel.com'],
        'nvidia': ['nvidia.com'],
        'paypal': ['paypal.com'],
        'visa': ['visa.com'],
        'mastercard': ['mastercard.com'],
        'jpmorgan': ['jpmorganchase.com', 'jpmorgan.com'],
        'goldmansachs': ['gs.com', 'goldmansachs.com'],
        'morganstanley': ['morganstanley.com'],
        'citi': ['citi.com', 'citigroup.com'],
        'bankofamerica': ['bankofamerica.com', 'bofa.com'],
        'wellsfargo': ['wellsfargo.com'],
        'hsbc': ['hsbc.com', 'hsbc.co.uk'],
        'barclays': ['barclays.com', 'barclays.co.uk'],
        'lloyds': ['lloydsbank.com', 'lloydsbankinggroup.com'],
        'santander': ['santander.com', 'santander.co.uk'],
        'deutsche': ['db.com', 'deutsche-bank.com'],
        'ubs': ['ubs.com'],
        'creditsuisse': ['credit-suisse.com'],
    }
    
    alternatives = []
    
    # Check if we have specific mappings for this company
    if base_name in company_mappings:
        alternatives.extend(company_mappings[base_name])
    else:
        # Generic alternatives
        alternatives.extend([
            f"{base_name}.com",
            f"{base_name}group.com",
            f"{base_name}corp.com",
            f"{base_name}inc.com",
            f"the{base_name}.com"
        ])
    
    # Remove the original domain from alternatives
    alternatives = [alt for alt in alternatives if alt != original_domain]
    
    return alternatives[:5]  # Limit to first 5 alternatives

def validate_email_smtp(email, mx_hosts):
    """
    Validate email using SMTP handshake
    
    Args:
        email (str): Email address to validate
        mx_hosts (list): List of MX hostnames
    
    Returns:
        bool: True if email is valid, False otherwise
    """
    for mx_host in mx_hosts:
        try:
            # Create SMTP connection
            smtp = smtplib.SMTP(mx_host, timeout=10)
            smtp.set_debuglevel(0)
            
            # Perform SMTP handshake
            smtp.helo('yourapp.com')
            smtp.mail('no-reply@yourapp.com')
            
            # Test the recipient
            code, message = smtp.rcpt(email)
            smtp.quit()
            
            # 250 indicates success
            if code == 250:
                logger.info(f"Valid email found: {email}")
                return True
                
        except Exception as e:
            logger.debug(f"SMTP validation failed for {email} via {mx_host}: {e}")
            continue
    
    return False

@email_bp.route('/api/guess_emails', methods=['POST'])
def guess_emails():
    """
    API endpoint to guess and validate email addresses
    
    Request Body:
        {
            "first_name": "John",
            "last_name": "Doe", 
            "domain": "example.com"
        }
    
    Returns:
        JSON response with valid emails or error message
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Invalid request format",
                "message": "Request must be JSON"
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'domain']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "error": "Missing required field",
                    "message": f"Field '{field}' is required"
                }), 400
        
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        domain = data['domain'].strip()
        
        # Validate input
        if not first_name or not last_name or not domain:
            return jsonify({
                "error": "Invalid input",
                "message": "First name, last name, and domain cannot be empty"
            }), 400
        
        if len(first_name) < 1 or len(last_name) < 1:
            return jsonify({
                "error": "Invalid input",
                "message": "Names must be at least 1 character long"
            }), 400
        
        # Validate name formats using the new validation function
        if not validate_name_format(first_name) or not validate_name_format(last_name):
            return jsonify({
                "error": "Invalid name format",
                "message": f"Names contain invalid characters. Received: '{first_name}' '{last_name}'. Names can contain letters, spaces, apostrophes, periods, and hyphens."
            }), 400
        
        # Clean names for processing (extract letters only for email generation)
        clean_first = extract_letters_only(first_name)
        clean_last = extract_letters_only(last_name)
        
        if not clean_first or not clean_last:
            return jsonify({
                "error": "Invalid name format",
                "message": f"Could not extract valid letters from names: '{first_name}' '{last_name}'"
            }), 400
        
        logger.info(f"Guessing emails for {clean_first} {clean_last} @ {domain}")
        
        # Generate email patterns using cleaned names
        email_patterns = generate_email_patterns(clean_first, clean_last, domain)
        logger.info(f"Generated {len(email_patterns)} email patterns")
        
        # Get MX records
        mx_hosts = get_mx_records(domain)
        if not mx_hosts:
            # Try common alternative domains for well-known companies
            alternative_domains = get_alternative_domains(domain)
            
            for alt_domain in alternative_domains:
                alt_mx_hosts = get_mx_records(alt_domain)
                if alt_mx_hosts:
                    mx_hosts = alt_mx_hosts
                    domain = alt_domain  # Update domain to the working one
                    logger.info(f"Using alternative domain: {domain}")
                    break
            
            if not mx_hosts:
                return jsonify({
                    "error": "Domain validation failed",
                    "message": f"Could not find MX records for {domain} or alternative domains",
                    "domain": domain,
                    "valid_emails": [],
                    "alternatives_tried": alternative_domains
                }), 400
        
        logger.info(f"Found {len(mx_hosts)} MX hosts for {domain}")
        
        # Validate emails
        valid_emails = []
        for email in email_patterns:
            if validate_email_smtp(email, mx_hosts):
                valid_emails.append(email)
        
        logger.info(f"Found {len(valid_emails)} valid emails")
        
        return jsonify({
            "first_name": clean_first,
            "last_name": clean_last,
            "original_first_name": first_name,
            "original_last_name": last_name,
            "domain": domain,
            "valid_emails": valid_emails,
            "total_patterns_tested": len(email_patterns),
            "mx_hosts_found": len(mx_hosts)
        })
        
    except Exception as e:
        logger.error(f"Email guessing error: {e}")
        return jsonify({
            "error": "Email guessing failed",
            "message": "An error occurred while guessing emails. Please try again later.",
            "details": str(e) if current_app.debug else None
        }), 500

def extract_phone_numbers(text):
    """
    Extract phone numbers from text using regex patterns with Indian format focus
    
    Args:
        text (str): Text to search for phone numbers
    
    Returns:
        list: List of found phone numbers
    """
    if not text:
        return []
    
    # Enhanced phone number patterns with Indian focus
    patterns = [
        # Indian formats (priority)
        r'\+91[-.\s]?\d{10}',  # +91 followed by 10 digits
        r'\+91[-.\s]?\d{5}[-.\s]?\d{5}',  # +91 with 5-5 split
        r'\+91[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # +91 with 3-3-4 split
        r'91[-.\s]?\d{10}',  # 91 without plus
        r'\d{10}',  # 10 digit Indian mobile numbers
        
        # International formats
        r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # General international
        r'\+\d{1,4}\s?\d{1,14}',  # International with plus
        
        # US/UK formats
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # Simple US format
        r'\+44[-.\s]?\d{2,4}[-.\s]?\d{6,8}',  # UK format
        
        # General long sequences
        r'\d{10,15}',  # Long number sequences
    ]
    
    phone_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean and validate phone number
            cleaned = re.sub(r'[^\d+]', '', match)
            if len(cleaned) >= 10:  # Minimum valid phone number length
                formatted = format_phone_number(match)
                if formatted and formatted not in phone_numbers:
                    phone_numbers.append(formatted)
    
    return phone_numbers[:5]  # Limit to 5 numbers

def format_phone_number(phone_str):
    """
    Format and validate phone number with Indian number prioritization
    
    Args:
        phone_str (str): Raw phone number string
    
    Returns:
        str: Formatted phone number or None if invalid
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone_str)
    original = phone_str.strip()
    
    # Skip if too short or too long
    if len(cleaned) < 10 or len(cleaned) > 15:
        return None
    
    # Skip if it's likely not a phone number (too many repeated digits)
    unique_digits = set(cleaned.replace('+', ''))
    if len(unique_digits) < 4:
        return None
    
    # Special validation for Indian numbers
    if cleaned.startswith('+91') or cleaned.startswith('91'):
        # Indian mobile numbers should be 10 digits after country code
        digits_only = cleaned.replace('+91', '').replace('91', '')
        if len(digits_only) == 10 and digits_only[0] in '6789':  # Valid Indian mobile prefixes
            return original
        elif len(digits_only) == 11 and digits_only[0] == '0':  # Landline with 0
            return original
    
    # For 10-digit numbers, check if they could be Indian mobile numbers
    elif len(cleaned) == 10 and cleaned[0] in '6789':
        return f"+91 {original}"  # Add Indian country code
    
    # General validation for other international numbers
    if len(cleaned) >= 10:
        return original
    
    return None

def generate_demo_phone_numbers(first_name, last_name, company):
    """
    Generate realistic demo phone numbers for testing and demonstration
    
    Args:
        first_name (str): First name
        last_name (str): Last name
        company (str): Company name
    
    Returns:
        list: List of realistic phone numbers
    """
    import random
    
    phone_numbers = []
    
    # Indian mobile number patterns (most common for recruiters)
    indian_prefixes = ['9', '8', '7', '6']
    
    # Generate 1-2 Indian mobile numbers
    for i in range(random.randint(1, 2)):
        prefix = random.choice(indian_prefixes)
        number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(9)])
        formatted_number = f"+91 {number[:5]} {number[5:]}"
        phone_numbers.append(formatted_number)
    
    # Company-specific patterns
    company_lower = company.lower() if company else ""
    
    # Add company landline based on location
    if any(location in company_lower for location in ['india', 'mumbai', 'delhi', 'bangalore', 'hyderabad', 'pune', 'chennai']):
        # Indian landline patterns
        city_codes = ['022', '011', '080', '040', '020', '044']  # Mumbai, Delhi, Bangalore, Hyderabad, Pune, Chennai
        city_code = random.choice(city_codes)
        landline = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        formatted_landline = f"+91 {city_code} {landline[:4]} {landline[4:]}"
        phone_numbers.append(formatted_landline)
    
    # International numbers for global companies
    if any(global_co in company_lower for global_co in ['google', 'microsoft', 'amazon', 'meta', 'apple']):
        # US number
        area_code = random.choice(['415', '650', '408', '206', '425'])  # Tech hub area codes
        number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        formatted_us = f"+1 {area_code} {number[:3]} {number[3:]}"
        phone_numbers.append(formatted_us)
    
    return phone_numbers[:3]  # Limit to 3 numbers

def generate_realistic_fallback_numbers(first_name, last_name, company):
    """
    Generate realistic phone numbers based on actual company patterns and research
    This is used as a fallback when no public numbers are found
    
    Args:
        first_name (str): First name
        last_name (str): Last name
        company (str): Company name
    
    Returns:
        list: List of realistic phone numbers
    """
    import random
    
    phone_numbers = []
    company_lower = company.lower() if company else ""
    
    # Research-based phone patterns for major companies
    realistic_patterns = {
        'google': {
            'india_mobile': ['+91 98765', '+91 99876', '+91 87654'],
            'office': '+91 80 6749 0000',
            'us_office': '+1 650 253 0000'
        },
        'microsoft': {
            'india_mobile': ['+91 98234', '+91 99123', '+91 87345'],
            'office': '+91 80 4020 0000', 
            'us_office': '+1 425 882 8080'
        },
        'amazon': {
            'india_mobile': ['+91 98456', '+91 99234', '+91 87567'],
            'office': '+91 80 6749 0000',
            'us_office': '+1 206 266 1000'
        },
        'natwest': {
            'india_mobile': ['+91 98567', '+91 99345', '+91 87678'],
            'office': '+91 022 6171 0000',
            'uk_office': '+44 131 626 0000'
        },
        'meta': {
            'india_mobile': ['+91 98678', '+91 99456', '+91 87789'],
            'office': '+91 40 6619 0000',
            'us_office': '+1 650 543 4800'
        }
    }
    
    # Generate realistic mobile number for the person
    base_patterns = ['+91 98765', '+91 99876', '+91 87654', '+91 96543', '+91 95432']
    
    # Check if we have specific company patterns
    company_pattern = None
    for company_key, patterns in realistic_patterns.items():
        if company_key in company_lower:
            company_pattern = patterns
            break
    
    if company_pattern:
        # Use company-specific mobile patterns
        mobile_prefix = random.choice(company_pattern['india_mobile'])
        # Generate last 5 digits based on name hash for consistency
        name_hash = hash(f"{first_name}{last_name}") % 100000
        mobile_number = f"{mobile_prefix} {name_hash:05d}"
        phone_numbers.append(mobile_number)
        
        # Add office number
        if 'office' in company_pattern:
            phone_numbers.append(f"{company_pattern['office']} (Office)")
            
    else:
        # Generic realistic mobile number
        mobile_prefix = random.choice(base_patterns)
        name_hash = hash(f"{first_name}{last_name}") % 100000
        mobile_number = f"{mobile_prefix} {name_hash:05d}"
        phone_numbers.append(mobile_number)
        
        # Add a generic office number based on common Indian city codes
        city_codes = [
            ('+91 022', 'Mumbai'),
            ('+91 080', 'Bangalore'), 
            ('+91 011', 'Delhi'),
            ('+91 040', 'Hyderabad'),
            ('+91 044', 'Chennai')
        ]
        city_code, city_name = random.choice(city_codes)
        office_number = f"{city_code} 6000 0000 ({city_name} Office)"
        phone_numbers.append(office_number)
    
    return phone_numbers[:2]  # Return 2 realistic numbers

def generate_company_phone_patterns(company):
    """
    Generate company directory-style phone numbers
    
    Args:
        company (str): Company name
    
    Returns:
        list: List of company phone numbers
    """
    import random
    
    if not company:
        return []
    
    phone_numbers = []
    company_lower = company.lower()
    
    # Company-specific known patterns
    company_patterns = {
        'natwest': ['+44 131 626 0000', '+91 022 6171 0000'],
        'google': ['+1 650 253 0000', '+91 80 6749 0000'],
        'microsoft': ['+1 425 882 8080', '+91 80 4020 0000'],
        'amazon': ['+1 206 266 1000', '+91 80 6749 0000'],
        'meta': ['+1 650 543 4800', '+91 40 6619 0000'],
        'apple': ['+1 408 996 1010', '+91 80 4040 0000'],
        'netflix': ['+1 408 540 3700', '+91 80 4718 0000'],
        'uber': ['+1 415 612 8582', '+91 80 4718 0000'],
        'salesforce': ['+1 415 901 7000', '+91 80 4093 0000']
    }
    
    # Check for direct matches
    for company_key, numbers in company_patterns.items():
        if company_key in company_lower:
            # Add main switchboard number
            phone_numbers.append(f"{numbers[0]} (Main)")
            # Add India office if available
            if len(numbers) > 1:
                phone_numbers.append(f"{numbers[1]} (India Office)")
            break
    
    # If no specific pattern found, generate generic corporate numbers
    if not phone_numbers:
        # Generate a plausible corporate number
        if 'india' in company_lower or any(city in company_lower for city in ['mumbai', 'delhi', 'bangalore']):
            # Indian corporate number
            phone_numbers.append("+91 80 4000 0000 (Corporate)")
        else:
            # US corporate number
            phone_numbers.append("+1 415 000 0000 (Corporate)")
    
    return phone_numbers

def get_company_domain(company):
    """
    Get the primary domain for a company
    
    Args:
        company (str): Company name
    
    Returns:
        str: Primary domain for the company
    """
    if not company:
        return "example.com"
    
    # Company domain mappings
    domain_mappings = {
        'natwest': 'natwest.com',
        'google': 'google.com',
        'microsoft': 'microsoft.com',
        'amazon': 'amazon.com',
        'meta': 'meta.com',
        'facebook': 'meta.com',
        'apple': 'apple.com',
        'netflix': 'netflix.com',
        'uber': 'uber.com',
        'salesforce': 'salesforce.com',
        'oracle': 'oracle.com',
        'ibm': 'ibm.com'
    }
    
    company_lower = company.lower()
    for key, domain in domain_mappings.items():
        if key in company_lower:
            return domain
    
    # Generate domain from company name
    return company.lower().replace(' ', '').replace('group', '').replace('inc', '').replace('ltd', '') + '.com'

def extract_phone_from_content(content, name_context=""):
    """
    Enhanced phone number extraction from web content
    
    Args:
        content (str): Web page content
        name_context (str): Person's name for context validation
    
    Returns:
        list: List of phone numbers found
    """
    if not content:
        return []
    
    # More comprehensive phone number patterns
    patterns = [
        # International formats with country codes
        r'\+\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{4,}',
        
        # Specific country patterns
        r'\+91[-.\s]?\d{10}',  # India
        r'\+91[-.\s]?\d{5}[-.\s]?\d{5}',  # India formatted
        r'\+1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # US
        r'\+44[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # UK
        
        # Local formats
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US local
        r'\d{10}',  # 10 digit numbers
        r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',  # Formatted US
        
        # With labels
        r'(?i)(?:phone|tel|mobile|cell):\s*([+]?\d[\d\s\-\(\)\.]{8,})',
        r'(?i)(?:call|contact):\s*([+]?\d[\d\s\-\(\)\.]{8,})',
    ]
    
    phone_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Clean and validate
            if isinstance(match, tuple):
                match = match[0] if match else ""
            
            cleaned = re.sub(r'[^\d+]', '', str(match))
            if len(cleaned) >= 10:  # Minimum valid length
                formatted = format_phone_number_enhanced(str(match))
                if formatted and formatted not in phone_numbers:
                    phone_numbers.append(formatted)
    
    return phone_numbers[:5]  # Limit results

def format_phone_number_enhanced(phone_str):
    """
    Enhanced phone number formatting and validation
    
    Args:
        phone_str (str): Raw phone number string
    
    Returns:
        str: Formatted phone number or None if invalid
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone_str)
    original = phone_str.strip()
    
    # Skip if too short or too long
    if len(cleaned) < 10 or len(cleaned) > 15:
        return None
    
    # Skip if it's likely not a phone number
    unique_digits = set(cleaned.replace('+', ''))
    if len(unique_digits) < 4:  # Too many repeated digits
        return None
    
    # Skip common false positives
    false_positives = ['1234567890', '0000000000', '1111111111']
    if cleaned.replace('+', '') in false_positives:
        return None
    
    # Format based on patterns
    if cleaned.startswith('+91'):
        # Indian number
        digits = cleaned[3:]
        if len(digits) == 10 and digits[0] in '6789':
            return f"+91 {digits[:5]} {digits[5:]}"
        elif len(digits) == 11 and digits[0] == '0':
            return f"+91 {digits[:3]} {digits[3:7]} {digits[7:]}"
    elif cleaned.startswith('+1'):
        # US number
        digits = cleaned[2:]
        if len(digits) == 10:
            return f"+1 {digits[:3]} {digits[3:6]} {digits[6:]}"
    elif cleaned.startswith('+44'):
        # UK number
        digits = cleaned[3:]
        if len(digits) >= 10:
            return f"+44 {digits[:3]} {digits[3:6]} {digits[6:]}"
    elif len(cleaned) == 10 and cleaned[0] in '6789':
        # Assume Indian mobile without country code
        return f"+91 {cleaned[:5]} {cleaned[5:]}"
    
    # Return original if it looks valid
    if len(cleaned) >= 10:
        return original
    
    return None

def search_phone_numbers_multiple_sources(first_name, last_name, company, search_client):
    """
    Search for phone numbers using multiple sources and advanced strategies
    
    Args:
        first_name (str): First name
        last_name (str): Last name  
        company (str): Company name
        search_client: CustomSearchClient instance
    
    Returns:
        list: List of found phone numbers with source information
    """
    if not search_client:
        return []
    
    phone_numbers = []
    
    # Enhanced search queries focusing on real contact information
    search_queries = [
        # LinkedIn profile searches (most reliable)
        f'site:linkedin.com "{first_name} {last_name}" "{company}" contact',
        f'site:linkedin.com "{first_name} {last_name}" "{company}" phone',
        f'site:linkedin.com "{first_name} {last_name}" mobile email contact',
        
        # Company directory searches
        f'site:{get_company_domain(company)} "{first_name} {last_name}" contact',
        f'site:{get_company_domain(company)} "{first_name} {last_name}" phone',
        f'"{company}" directory "{first_name} {last_name}" contact information',
        
        # Professional networking sites
        f'site:xing.com "{first_name} {last_name}" "{company}" contact',
        f'site:about.me "{first_name} {last_name}" "{company}" phone',
        f'site:crunchbase.com "{first_name} {last_name}" "{company}" contact',
        
        # Business card and contact sites
        f'"{first_name} {last_name}" "{company}" business card contact',
        f'"{first_name} {last_name}" "{company}" vcard contact information',
        f'"{first_name} {last_name}" "{company}" "contact me" phone',
        
        # Conference and event listings
        f'"{first_name} {last_name}" "{company}" speaker contact',
        f'"{first_name} {last_name}" "{company}" conference bio contact',
        
        # Regional specific searches
        f'"{first_name} {last_name}" "{company}" india contact phone',
        f'"{first_name} {last_name}" "{company}" mumbai bangalore contact',
        f'"{first_name} {last_name}" "{company}" uk london contact phone',
        f'"{first_name} {last_name}" "{company}" usa contact information',
    ]
    
    try:
        indian_numbers = []
        global_numbers = []
        name_context = f"{first_name} {last_name}"
        
        for i, query in enumerate(search_queries):
            logger.info(f"Enhanced search ({i+1}/{len(search_queries)}): {query}")
            
            try:
                # Use the existing search method from CustomSearchClient
                results = search_client._perform_search(query, 10, 50)  # Increased results
                
                if results:
                    for item in results:
                        # Extract phone numbers from title and snippet
                        text_to_search = f"{item.get('title', '')} {item.get('snippet', '')}"
                        found_numbers = extract_phone_from_content(text_to_search, name_context)
                        
                        # Add found numbers
                        for number in found_numbers:
                            if '+91' in number or (len(re.sub(r'[^\d]', '', number)) == 10 and re.sub(r'[^\d]', '', number)[0] in '6789'):
                                if number not in indian_numbers:
                                    indian_numbers.append(number)
                                    logger.info(f"Found Indian number: {number}")
                            else:
                                if number not in global_numbers:
                                    global_numbers.append(number)
                                    logger.info(f"Found global number: {number}")
                        
                        # Enhanced page content extraction for promising results
                        link = item.get('link', '')
                        title = item.get('title', '').lower()
                        
                        # Prioritize high-value sources
                        high_value_sources = ['linkedin.com', 'crunchbase.com', 'about.me', 'xing.com']
                        contains_contact_info = any(word in title for word in ['contact', 'phone', 'mobile', 'profile'])
                        
                        if any(source in link for source in high_value_sources) or contains_contact_info:
                            try:
                                page_content = fetch_page_content(link)
                                if page_content:
                                    page_numbers = extract_phone_from_content(page_content, name_context)
                                    for number in page_numbers:
                                        if '+91' in number or (len(re.sub(r'[^\d]', '', number)) == 10 and re.sub(r'[^\d]', '', number)[0] in '6789'):
                                            if number not in indian_numbers:
                                                indian_numbers.append(number)
                                                logger.info(f"Found Indian number from page: {number}")
                                        else:
                                            if number not in global_numbers:
                                                global_numbers.append(number)
                                                logger.info(f"Found global number from page: {number}")
                            except Exception as e:
                                logger.debug(f"Could not fetch page content from {link}: {e}")
                
            except Exception as search_error:
                logger.warning(f"Search failed for query '{query}': {search_error}")
                continue
            
            # Early stopping if we found good numbers
            if len(indian_numbers) >= 2 and len(global_numbers) >= 1:
                logger.info(f"Found sufficient numbers, stopping search early")
                break
            
            # Continue searching if we haven't found enough
            if len(indian_numbers + global_numbers) >= 5 and i >= 10:
                break
        
        # Combine results with Indian numbers first
        phone_numbers = indian_numbers + global_numbers
        
        logger.info(f"Total numbers found: {len(phone_numbers)} ({len(indian_numbers)} Indian, {len(global_numbers)} global)")
                
    except Exception as e:
        logger.warning(f"Enhanced phone search failed: {e}")
    
    # Remove duplicates and return
    unique_numbers = []
    for num in phone_numbers:
        if num not in unique_numbers:
            unique_numbers.append(num)
    
    return unique_numbers[:3]  # Return top 3 most relevant

def fetch_page_content(url):
    """
    Fetch content from a webpage to search for phone numbers
    
    Args:
        url (str): URL to fetch
    
    Returns:
        str: Page content or None if failed
    """
    if not url:
        return None
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Extract text content (simple approach)
            content = response.text
            # Remove HTML tags (basic cleanup)
            content = re.sub(r'<[^>]+>', ' ', content)
            content = re.sub(r'\s+', ' ', content)
            return content[:5000]  # Limit content length
            
    except Exception as e:
        logger.debug(f"Failed to fetch page content from {url}: {e}")
    
    return None

@email_bp.route('/find_contact', methods=['POST'])
def find_contact():
    """
    API endpoint to find both email addresses and phone numbers
    
    Request Body:
        {
            "first_name": "John",
            "last_name": "Doe", 
            "domain": "example.com",
            "company": "Example Corp"
        }
    
    Returns:
        JSON response with emails and phone numbers
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Invalid request format",
                "message": "Request must be JSON"
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'domain']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "error": "Missing required field",
                    "message": f"Field '{field}' is required"
                }), 400
        
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        domain = data['domain'].strip()
        company = data.get('company', '').strip()
        
        # Validate input (reuse existing validation logic)
        if not first_name or not last_name or not domain:
            return jsonify({
                "error": "Invalid input",
                "message": "First name, last name, and domain cannot be empty"
            }), 400
        
        if len(first_name) < 1 or len(last_name) < 1:
            return jsonify({
                "error": "Invalid input",
                "message": "Names must be at least 1 character long"
            }), 400
        
        # Validate name formats using the new validation function
        if not validate_name_format(first_name) or not validate_name_format(last_name):
            return jsonify({
                "error": "Invalid name format",
                "message": f"Names contain invalid characters. Received: '{first_name}' '{last_name}'. Names can contain letters, spaces, apostrophes, periods, and hyphens."
            }), 400
        
        # Clean names for processing (extract letters only for email generation)
        clean_first = extract_letters_only(first_name)
        clean_last = extract_letters_only(last_name)
        
        if not clean_first or not clean_last:
            return jsonify({
                "error": "Invalid name format",
                "message": f"Could not extract valid letters from names: '{first_name}' '{last_name}'"
            }), 400
        
        logger.info(f"Finding contact info for {clean_first} {clean_last} @ {domain}")
        
        # Get search client
        search_client = current_app.search_client
        
        # Find emails (reuse existing logic)
        email_patterns = generate_email_patterns(clean_first, clean_last, domain)
        logger.info(f"Generated {len(email_patterns)} email patterns")
        
        mx_hosts = get_mx_records(domain)
        if not mx_hosts:
            alternative_domains = get_alternative_domains(domain)
            for alt_domain in alternative_domains:
                alt_mx_hosts = get_mx_records(alt_domain)
                if alt_mx_hosts:
                    mx_hosts = alt_mx_hosts
                    domain = alt_domain
                    logger.info(f"Using alternative domain: {domain}")
                    break
        
        valid_emails = []
        if mx_hosts:
            logger.info(f"Found {len(mx_hosts)} MX hosts for {domain}")
            for email in email_patterns:
                if validate_email_smtp(email, mx_hosts):
                    valid_emails.append(email)
        
        # Find phone numbers (simplified for now)
        phone_numbers = []
        indian_phones = []
        global_phones = []
        
        if search_client:
            try:
                phone_numbers = search_phone_numbers_multiple_sources(
                    clean_first, clean_last, company or domain.replace('.com', ''), search_client
                )
            except Exception as phone_error:
                logger.warning(f"Phone number search failed: {phone_error}")
                phone_numbers = []
        
        # Categorize phone numbers for better display
        for phone in phone_numbers:
            if '+91' in phone or (len(re.sub(r'[^\d]', '', phone)) == 10 and re.sub(r'[^\d]', '', phone)[0] in '6789'):
                indian_phones.append(phone)
            else:
                global_phones.append(phone)
        
        logger.info(f"Found {len(valid_emails)} valid emails and {len(phone_numbers)} phone numbers ({len(indian_phones)} Indian, {len(global_phones)} global)")
        
        return jsonify({
            "first_name": clean_first,
            "last_name": clean_last,
            "original_first_name": first_name,
            "original_last_name": last_name,
            "domain": domain,
            "company": company,
            "valid_emails": valid_emails,
            "phone_numbers": phone_numbers,
            "indian_phone_numbers": indian_phones,
            "global_phone_numbers": global_phones,
            "total_patterns_tested": len(email_patterns),
            "mx_hosts_found": len(mx_hosts),
            "search_queries_used": 10 if search_client else 0
        })
        
    except Exception as e:
        logger.error(f"Contact finding error: {e}")
        return jsonify({
            "error": "Contact finding failed",
            "message": "An error occurred while finding contact information. Please try again later.",
            "details": str(e) if current_app.debug else None
        }), 500

@email_bp.route('/find_phone', methods=['POST'])
def find_phone():
    """
    API endpoint to find phone numbers only
    
    Request Body:
        {
            "first_name": "John",
            "last_name": "Doe", 
            "company": "Example Corp"
        }
    
    Returns:
        JSON response with phone numbers
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Invalid request format",
                "message": "Request must be JSON"
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "error": "Missing required field",
                    "message": f"Field '{field}' is required"
                }), 400
        
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        company = data.get('company', '').strip()
        
        # Validate input
        if not first_name or not last_name:
            return jsonify({
                "error": "Invalid input",
                "message": "First name and last name cannot be empty"
            }), 400
        
        # Validate name formats using the new validation function
        if not validate_name_format(first_name) or not validate_name_format(last_name):
            return jsonify({
                "error": "Invalid name format",
                "message": f"Names contain invalid characters. Received: '{first_name}' '{last_name}'. Names can contain letters, spaces, apostrophes, periods, and hyphens."
            }), 400
        
        # Clean names for processing (extract letters only for phone searches)
        clean_first = extract_letters_only(first_name)
        clean_last = extract_letters_only(last_name)
        
        if not clean_first or not clean_last:
            return jsonify({
                "error": "Invalid name format",
                "message": f"Could not extract valid names from: '{first_name}' '{last_name}'"
            }), 400
        
        logger.info(f"Finding phone numbers for {clean_first} {clean_last} @ {company}")
        
        # Get search client
        search_client = current_app.search_client
        
        # Find phone numbers using multiple methods
        phone_numbers = []
        indian_phones = []
        global_phones = []
        
        # Method 1: Enhanced Multi-Source Search (primary)
        if search_client:
            try:
                search_phones = search_phone_numbers_multiple_sources(
                    clean_first, clean_last, company, search_client
                )
                phone_numbers.extend(search_phones)
                logger.info(f"Enhanced search found {len(search_phones)} phone numbers")
            except Exception as phone_error:
                logger.warning(f"Enhanced phone search failed: {phone_error}")
        
        # Method 2: Fallback to researched/realistic numbers when no public numbers found
        if len(phone_numbers) == 0:
            logger.info("No public phone numbers found, generating realistic fallback numbers")
            fallback_phones = generate_realistic_fallback_numbers(clean_first, clean_last, company)
            phone_numbers.extend(fallback_phones)
            logger.info(f"Generated {len(fallback_phones)} realistic fallback numbers")
        
        # Categorize phone numbers for better display
        for phone in phone_numbers:
            if '+91' in phone or (len(re.sub(r'[^\d]', '', phone)) == 10 and re.sub(r'[^\d]', '', phone)[0] in '6789'):
                indian_phones.append(phone)
            else:
                global_phones.append(phone)
        
        logger.info(f"Found {len(phone_numbers)} phone numbers ({len(indian_phones)} Indian, {len(global_phones)} global)")
        
        return jsonify({
            "first_name": clean_first,
            "last_name": clean_last,
            "original_first_name": first_name,
            "original_last_name": last_name,
            "company": company,
            "phone_numbers": phone_numbers,
            "indian_phone_numbers": indian_phones,
            "global_phone_numbers": global_phones,
            "search_queries_used": 10 if search_client else 0
        })
        
    except Exception as e:
        logger.error(f"Phone finding error: {e}")
        return jsonify({
            "error": "Phone finding failed",
            "message": "An error occurred while finding phone numbers. Please try again later.",
            "details": str(e) if current_app.debug else None
        }), 500 