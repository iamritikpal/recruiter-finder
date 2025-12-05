"""
File utilities for handling resume uploads and text extraction
"""
import os
import tempfile
import logging
import PyPDF2
from docx import Document

logger = logging.getLogger(__name__)

def validate_file(file, max_size, allowed_extensions, allowed_mime_types):
    """
    Validate uploaded file
    
    Args:
        file: Uploaded file object
        max_size: Maximum file size in bytes
        allowed_extensions: Set of allowed file extensions
        allowed_mime_types: List of allowed MIME types
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file or file.filename == '':
        return False, "No file selected"
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
    
    # Check MIME type
    if file.mimetype not in allowed_mime_types:
        return False, "Invalid file format"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f"File size must be less than {max_size_mb:.1f}MB"
    
    return True, None

def extract_text_from_file(file):
    """
    Extract text from uploaded file based on file type
    
    Args:
        file: Uploaded file object
    
    Returns:
        str: Extracted text content
    
    Raises:
        ValueError: If file format is unsupported or extraction fails
    """
    try:
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            return _extract_text_from_pdf(file)
        elif filename.endswith(('.doc', '.docx')):
            return _extract_text_from_docx(file)
        elif filename.endswith('.txt'):
            return _extract_text_from_txt(file)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
            
    except Exception as e:
        logger.error(f"Error extracting text from file {file.filename}: {e}")
        raise ValueError(f"Failed to extract text from file: {str(e)}")

def _extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if not text.strip():
            raise ValueError("No text found in PDF file")
            
        return text.strip()
        
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise ValueError("Failed to extract text from PDF")

def _extract_text_from_docx(file):
    """Extract text from Word document"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            file.save(tmp_file.name)
            
            # Extract text from document
            doc = Document(tmp_file.name)
            text = ""
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
            
            # Clean up temp file
            os.unlink(tmp_file.name)
            
            if not text.strip():
                raise ValueError("No text found in document")
                
            return text.strip()
            
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        raise ValueError("Failed to extract text from Word document")

def _extract_text_from_txt(file):
    """Extract text from plain text file"""
    try:
        # Try different encodings
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                file.seek(0)
                text = file.read().decode(encoding)
                
                if text.strip():
                    return text.strip()
                    
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        raise ValueError("Unable to decode text file")
        
    except Exception as e:
        logger.error(f"TXT extraction error: {e}")
        raise ValueError("Failed to extract text from text file")

def get_file_info(file):
    """
    Get information about uploaded file
    
    Args:
        file: Uploaded file object
    
    Returns:
        dict: File information
    """
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    return {
        'filename': file.filename,
        'size': file_size,
        'size_mb': round(file_size / (1024 * 1024), 2),
        'mimetype': file.mimetype,
        'extension': os.path.splitext(file.filename)[1].lower()
    } 