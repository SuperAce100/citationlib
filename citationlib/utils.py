"""Utility functions for the citations package."""

import re
from typing import List, Optional
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from urllib.parse import urlparse

from .config import (
    HTTP_HEADERS,
    REQUEST_TIMEOUT,
    NAME_SUFFIXES,
    PROFESSIONAL_TITLES,
    SITE_NAME_MAPPING
)
from .exceptions import (
    DOIError,
    ArXivError,
    PubMedError,
    PMCError,
    WebpageError,
    AuthorExtractionError
)
from .types import Citation, Style

def clean_doi(doi: str) -> str:
    """Clean and validate a DOI string.
    
    Args:
        doi: The DOI string to clean
        
    Returns:
        The cleaned DOI string
        
    Raises:
        DOIError: If the DOI is invalid
    """
    # Remove any URL prefix
    doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi.strip())
    
    # Validate DOI format
    if not re.match(r'^10\.\d{4,}/[-._;()/:\w]+$', doi):
        raise DOIError(f"Invalid DOI format: {doi}")
    
    return doi

def clean_author_name(author: str) -> Optional[str]:
    """Clean and format an author name.
    
    Args:
        author: The author name to clean
        
    Returns:
        The cleaned author name, or None if invalid
    """
    if not author:
        return None
        
    # Basic cleaning
    author = author.strip()
    
    # Skip if too short or looks like a URL/email
    if len(author) < 2 or '@' in author or 'http' in author:
        return None
    
    # Remove "By" prefix and similar
    author = re.sub(r'^(?:by|written by|posted by|from|for)\s+', '', author, flags=re.IGNORECASE)
    
    # Remove any "and" or commas at the start/end
    author = re.sub(r'^(?:and|,|\s)+|(?:and|,|\s)+$', '', author)
    
    # Remove common suffixes that aren't part of names
    author = re.sub(r'\s*(?:and|,)\s*(?:others|et al\.?).*$', '', author)
    
    # Remove roles or titles in parentheses
    author = re.sub(r'\s*\([^)]*\)', '', author)
    
    # Remove professional titles
    titles_pattern = '|'.join(PROFESSIONAL_TITLES)
    author = re.sub(fr'\s*(?:{titles_pattern}).*$', '', author, flags=re.IGNORECASE)
    
    # Remove common separators
    author = re.sub(r'\s*[|.-]\s*', ' ', author)
    
    # Remove any trailing punctuation
    author = re.sub(r'[.,;:]$', '', author)
    
    # Normalize whitespace
    author = ' '.join(author.split())
    
    # If the name is in all caps, convert to title case
    if author.isupper():
        author = author.title()
    
    # Final validation
    cleaned = author.strip()
    if len(cleaned) < 2 or not any(c.isalpha() for c in cleaned):
        return None
        
    return cleaned

def format_author_name(author_name: str) -> str:
    """Format an author name into APA style (Last, F.M.).
    
    Args:
        author_name: The author name to format
        
    Returns:
        The formatted author name
    """
    parts = author_name.strip().split()
    if len(parts) < 2:
        return author_name
    
    # Handle special cases where the last part shouldn't be the last name
    if parts[-1].lower() in NAME_SUFFIXES:
        last_name = parts[-2] + ' ' + parts[-1]
        first_names = parts[:-2]
    else:
        last_name = parts[-1]
        first_names = parts[:-1]
    
    # Handle hyphenated names
    if '-' in last_name:
        last_parts = last_name.split('-')
        last_name = '-'.join(p.capitalize() for p in last_parts)
    
    # Create initials from first names
    initials = '.'.join(name[0].upper() for name in first_names if name)
    
    return f"{last_name}, {initials}." if initials else last_name

def format_author_list(authors: List[str]) -> Optional[str]:
    """Format a list of authors according to APA style.
    
    Args:
        authors: List of author names to format
        
    Returns:
        The formatted author list string, or None if empty
    """
    if not authors:
        return None
        
    formatted_authors = [format_author_name(author) for author in authors]
    
    if len(formatted_authors) == 1:
        return formatted_authors[0]
    elif len(formatted_authors) == 2:
        return f"{formatted_authors[0]} & {formatted_authors[1]}"
    else:
        return f"{formatted_authors[0]} et al."

def get_site_name(url: str) -> str:
    """Get the formatted site name from a URL.
    
    Args:
        url: The URL to get the site name for
        
    Returns:
        The formatted site name
    """
    domain = re.sub(r'^www\.', '', urlparse(url).netloc)
    return SITE_NAME_MAPPING.get(domain, domain.replace('.', ' ').title())

def create_apa_citation(identifier: str) -> str:
    """Create an APA citation from an identifier.
    
    Args:
        identifier: DOI, arXiv ID, PubMed ID, PMC ID, URL, or full link
        
    Returns:
        HTML formatted APA citation
    """
    formatter = CitationFormatter()
    
    # Check for DOI
    doi_match = re.search(r'(10\.\d{4,}/[-._;()/:\w]+)', identifier)
    if doi_match:
        try:
            return formatter.create_doi_citation(doi_match.group(1))
        except DOIError as e:
            return f"Error creating citation: {str(e)}"
    
    # Check for PubMed ID
    pubmed_match = re.search(r'(?:pubmed\.ncbi\.nlm\.nih\.gov/|PMID:?\s*)(\d+)', identifier, re.IGNORECASE)
    if pubmed_match:
        try:
            return formatter.create_pubmed_citation(pubmed_match.group(1))
        except PubMedError as e:
            return f"Error creating citation: {str(e)}"
    
    # Check for PMC ID
    pmc_match = re.search(r'(?:ncbi\.nlm\.nih\.gov/pmc/articles/PMC|PMC:?\s*)(\d+)', identifier, re.IGNORECASE)
    if pmc_match:
        try:
            return formatter.create_pmc_citation(pmc_match.group(1))
        except PMCError as e:
            return f"Error creating citation: {str(e)}"
    
    # Check for arXiv ID
    arxiv_match = re.search(r'(?:arxiv\.org/(?:abs|pdf)/|arXiv:)(\d{4}\.\d{4,}(?:v\d+)?)|^(\d{4}\.\d{4,}(?:v\d+)?)$|^([a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)$', identifier, re.IGNORECASE)
    if arxiv_match:
        try:
            arxiv_id = next(g for g in arxiv_match.groups() if g is not None)
            return formatter.create_arxiv_citation(arxiv_id)
        except ArXivError as e:
            return f"Error creating citation: {str(e)}"
    
    # Handle as URL
    try:
        return formatter.create_webpage_citation(identifier)
    except WebpageError as e:
        return f"Error creating citation: {str(e)}"

def extract_authors(identifier: str) -> List[str]:
    """Extract authors from a citation source.
    
    Args:
        identifier: DOI, arXiv ID, URL, or full link
        
    Returns:
        List of author names
    """
    formatter = CitationFormatter()
    
    # Check for DOI
    doi_match = re.search(r'(10\.\d{4,}/[-._;()/:\w]+)', identifier)
    if doi_match:
        try:
            work = formatter.crossref.works(ids=doi_match.group(1))['message']
            authors = work.get('author', [])
            return [f"{author.get('family', '')}, {author.get('given', '')[0]}." 
                   for author in authors if author.get('family') and author.get('given')]
        except Exception as e:
            raise AuthorExtractionError(f"Error extracting DOI authors: {str(e)}")
    
    # Check for arXiv ID
    arxiv_match = re.search(r'(\d{4}\.\d{4,}|[a-z\-]+(\.[A-Z]{2})?/\d{7})', identifier)
    if arxiv_match:
        try:
            search = formatter.arxiv.Search(id_list=[arxiv_match.group(1)])
            paper = next(search.results())
            return [str(author) for author in paper.authors]
        except Exception as e:
            raise AuthorExtractionError(f"Error extracting arXiv authors: {str(e)}")
    
    # Handle as URL
    try:
        response = requests.get(identifier, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        metadata = formatter.extract_webpage_metadata(soup, identifier)
        return metadata['authors']
    except Exception as e:
        raise AuthorExtractionError(f"Error extracting webpage authors: {str(e)}")

def create_url_citation(url: str, style: Style) -> Citation:
    """Create a citation from just the URL when metadata extraction fails.
    
    Args:
        url: The URL to create a citation for
        style: The citation style to use
        
    Returns:
        Citation: A Citation object with basic information extracted from the URL
    """
    # Parse URL to get domain and path
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.strip('/')
    
    # Create a title from the path
    title = path.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
    if not title:
        title = domain
    
    # Create citation with minimal information
    return Citation(
        authors=[],  # No authors available
        title=title,
        year=datetime.now().year,  # Current year as access year
        url=url,
        accessed_date=datetime.now(),
        publisher=domain.split('.')[0].title()  # Use domain as publisher
    ) 