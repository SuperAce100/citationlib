"""Metadata extraction functionality for the citations package."""

import re
import json
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
from datetime import datetime

from .config import METADATA_SELECTORS, HTTP_HEADERS, REQUEST_TIMEOUT
from .exceptions import MetadataExtractionError, DOIError, ArXivError, PubMedError
from .types import WebpageMetadata
from .utils import clean_author_name, get_site_name
from .scraper import get_webpage_content

def extract_metadata(url: str) -> Dict[str, Any]:
    """Extract metadata from a URL.
    
    This function handles different types of sources:
    - DOI
    - arXiv
    - PubMed
    - PMC
    - General web pages
    
    Args:
        url: URL to extract metadata from
        
    Returns:
        Dictionary containing extracted metadata
        
    Raises:
        MetadataExtractionError: If metadata extraction fails
    """
    # Check for DOI
    doi_match = re.search(r'(10\.\d{4,}/[-._;()/:\w]+)', url)
    if doi_match:
        try:
            return extract_doi_metadata(doi_match.group(1))
        except DOIError:
            # Fall back to webpage extraction if it's a URL
            if url.startswith('http'):
                return extract_webpage_metadata(get_webpage_content(url), url)
            raise
    
    # Check for arXiv
    arxiv_match = re.search(r'(?:arxiv\.org/(?:abs|pdf)/|arXiv:)(\d{4}\.\d{4,}(?:v\d+)?)|^(\d{4}\.\d{4,}(?:v\d+)?)$|^([a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)$', url, re.IGNORECASE)
    if arxiv_match:
        try:
            arxiv_id = next(g for g in arxiv_match.groups() if g is not None)
            return extract_arxiv_metadata(arxiv_id)
        except ArXivError:
            # Fall back to webpage extraction if it's a URL
            if url.startswith('http'):
                return extract_webpage_metadata(get_webpage_content(url), url)
            raise
    
    # Check for PubMed
    pubmed_match = re.search(r'(?:pubmed\.ncbi\.nlm\.nih\.gov/|PMID:?\s*)(\d+)', url, re.IGNORECASE)
    if pubmed_match:
        try:
            return extract_pubmed_metadata(pubmed_match.group(1))
        except PubMedError:
            # Fall back to webpage extraction if it's a URL
            if url.startswith('http'):
                return extract_webpage_metadata(get_webpage_content(url), url)
            raise
    
    # Handle as webpage
    return extract_webpage_metadata(get_webpage_content(url), url)

def extract_doi_metadata(doi: str) -> Dict[str, Any]:
    """Extract metadata from a DOI using the Crossref API.
    
    Args:
        doi: DOI to extract metadata from
        
    Returns:
        Dictionary containing extracted metadata
        
    Raises:
        DOIError: If metadata extraction fails
    """
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()['message']
        
        # Extract authors
        authors = []
        for author in data.get('author', []):
            if author.get('family') and author.get('given'):
                authors.append({
                    'first_name': author['given'],
                    'last_name': author['family']
                })
        
        return {
            'authors': authors,
            'title': data.get('title', [None])[0],
            'year': data.get('published-print', {}).get('date-parts', [[None]])[0][0],
            'journal': data.get('container-title', [None])[0],
            'volume': data.get('volume'),
            'issue': data.get('issue'),
            'pages': data.get('page'),
            'doi': doi,
            'publisher': data.get('publisher')
        }
    except Exception as e:
        raise DOIError(f"Failed to extract DOI metadata: {str(e)}")

def extract_arxiv_metadata(arxiv_id: str) -> Dict[str, Any]:
    """Extract metadata from an arXiv paper.
    
    Args:
        arxiv_id: arXiv ID to extract metadata from
        
    Returns:
        Dictionary containing extracted metadata
        
    Raises:
        ArXivError: If metadata extraction fails
    """
    from arxiv import Search
    
    try:
        search = Search(id_list=[arxiv_id])
        paper = next(search.results())
        
        # Convert authors to our format
        authors = []
        for author in paper.authors:
            name_parts = str(author).split()
            if len(name_parts) >= 2:
                authors.append({
                    'first_name': name_parts[0],
                    'last_name': ' '.join(name_parts[1:])
                })
        
        return {
            'authors': authors,
            'title': paper.title,
            'year': paper.published.year,
            'journal': 'arXiv',
            'volume': None,
            'issue': None,
            'pages': None,
            'doi': None,
            'publisher': None
        }
    except Exception as e:
        raise ArXivError(f"Failed to extract arXiv metadata: {str(e)}")

def extract_pubmed_metadata(pmid: str) -> Dict[str, Any]:
    """Extract metadata from a PubMed article.
    
    Args:
        pmid: PubMed ID to extract metadata from
        
    Returns:
        Dictionary containing extracted metadata
        
    Raises:
        PubMedError: If metadata extraction fails
    """
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    try:
        response = requests.get(url, headers=HTTP_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()['result'][pmid]
        
        # Extract authors
        authors = []
        for author in data.get('authors', []):
            name = author['name']
            if ',' in name:
                last_name, first_name = name.split(',', 1)
                authors.append({
                    'first_name': first_name.strip(),
                    'last_name': last_name.strip()
                })
        
        return {
            'authors': authors,
            'title': data.get('title'),
            'year': int(data.get('pubdate', '').split()[0]) if data.get('pubdate') else None,
            'journal': data.get('fulljournalname'),
            'volume': data.get('volume'),
            'issue': data.get('issue'),
            'pages': data.get('pages'),
            'doi': None,  # PubMed API doesn't provide DOI directly
            'publisher': None
        }
    except Exception as e:
        raise PubMedError(f"Failed to extract PubMed metadata: {str(e)}")

def extract_webpage_metadata(soup: BeautifulSoup, url: str) -> WebpageMetadata:
    """Extract metadata from a webpage.
    
    Args:
        soup: BeautifulSoup object of the webpage
        url: URL of the webpage
        
    Returns:
        Dictionary containing extracted metadata
        
    Raises:
        MetadataExtractionError: If metadata extraction fails
    """
    metadata: WebpageMetadata = {
        'title': None,
        'authors': [],
        'pub_date': None,
        'site_name': None,
        'doi': None
    }
    
    try:
        # Extract DOI
        metadata['doi'] = extract_doi(soup, url)
        
        # Extract title
        metadata['title'] = extract_title(soup)
        
        # Extract authors
        metadata['authors'] = extract_authors(soup)
        
        # Extract publication date
        metadata['pub_date'] = extract_date(soup)
        
        # Extract site name
        metadata['site_name'] = get_site_name(url)
        
        return metadata
    except Exception as e:
        raise MetadataExtractionError(f"Failed to extract metadata: {str(e)}")

def extract_doi(soup: BeautifulSoup, url: str) -> Optional[str]:
    """Extract DOI from webpage.
    
    Args:
        soup: BeautifulSoup object of the webpage
        url: URL of the webpage
        
    Returns:
        Extracted DOI or None if not found
    """
    doi_found = None
    
    # Special handling for ScienceDirect
    if 'sciencedirect.com' in url:
        doi_found = extract_sciencedirect_doi(soup, url)
        if doi_found:
            return doi_found
    
    # Try citation_doi meta tag first (most reliable)
    doi_meta = soup.find('meta', {'name': ['citation_doi', 'dc.identifier', 'DC.Identifier', 'citation_doi_1', 'doi']}) or \
              soup.find('meta', {'property': ['citation_doi', 'og:doi']})
    if doi_meta and doi_meta.get('content'):
        doi_found = doi_meta['content']
    
    # If not found, try prism.doi
    if not doi_found:
        prism_doi = soup.find('meta', {'name': 'prism.doi'})
        if prism_doi and prism_doi.get('content'):
            doi_found = prism_doi['content']
    
    # If still not found, try data-doi attribute
    if not doi_found:
        doi_elem = soup.find(attrs={'data-doi': True})
        if doi_elem:
            doi_found = doi_elem['data-doi']
    
    # If still not found, try JSON-LD
    if not doi_found:
        doi_found = extract_doi_from_json_ld(soup)
    
    # If still not found, try looking for DOI in the page content
    if not doi_found:
        doi_found = extract_doi_from_text(soup)
    
    # Clean and validate the DOI if found
    if doi_found:
        # Remove any whitespace and normalize
        doi_found = doi_found.strip()
        # Remove any URL prefix if present
        doi_found = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi_found)
        # Validate DOI format
        if re.match(r'^10\.\d{4,}/[-._;()/:\w]+$', doi_found):
            return doi_found
    
    return None

def extract_sciencedirect_doi(soup: BeautifulSoup, url: str) -> Optional[str]:
    """Extract DOI from a ScienceDirect page.
    
    Args:
        soup: BeautifulSoup object of the webpage
        url: URL of the webpage
        
    Returns:
        Extracted DOI or None if not found
    """
    # First try to get DOI from the URL pattern
    pii_match = re.search(r'/article/pii/([A-Z0-9]+)', url)
    if not pii_match:
        return None
        
    # Try to find DOI in meta tags specific to ScienceDirect
    doi_meta = soup.find('meta', {'name': 'citation_doi'}) or \
              soup.find('meta', {'name': 'doi'}) or \
              soup.find('meta', {'scheme': 'doi'}) or \
              soup.find('meta', {'name': 'dc.identifier'})
    if doi_meta and doi_meta.get('content'):
        return doi_meta['content'].strip()
    
    # If meta tags don't work, try to find DOI in JSON-LD data
    for script in soup.find_all('script', {'type': 'application/json'}):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                article = data.get('article', {})
                if 'doi' in article:
                    return article['doi'].strip()
        except:
            continue
    
    # If still not found, try to find DOI in the page content
    doi_elem = soup.find('a', {'class': 'doi'})
    if doi_elem:
        doi_text = doi_elem.get_text()
        doi_match = re.search(r'(10\.\d{4,}/[-._;()/:\w]+)', doi_text)
        if doi_match:
            return doi_match.group(1).strip()
    
    return None

def extract_doi_from_json_ld(soup: BeautifulSoup) -> Optional[str]:
    """Extract DOI from JSON-LD data in the webpage.
    
    Args:
        soup: BeautifulSoup object of the webpage
        
    Returns:
        Extracted DOI or None if not found
    """
    for script in soup.find_all('script', {'type': 'application/ld+json'}):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                if 'doi' in data:
                    return data['doi']
                elif '@graph' in data:
                    for item in data['@graph']:
                        if isinstance(item, dict) and 'doi' in item:
                            return item['doi']
        except:
            continue
    return None

def extract_doi_from_text(soup: BeautifulSoup) -> Optional[str]:
    """Extract DOI from text content of the webpage.
    
    Args:
        soup: BeautifulSoup object of the webpage
        
    Returns:
        Extracted DOI or None if not found
    """
    doi_pattern = r'(?:doi\.org/|DOI:?\s*)(10\.\d{4,}/[-._;()/:\w]+)'
    doi_matches = soup.find_all(string=re.compile(doi_pattern, re.IGNORECASE))
    for match in doi_matches:
        doi_found = re.search(doi_pattern, match, re.IGNORECASE)
        if doi_found:
            return doi_found.group(1)
    return None

def extract_title(soup: BeautifulSoup) -> Optional[str]:
    """Extract title from webpage.
    
    Args:
        soup: BeautifulSoup object of the webpage
        
    Returns:
        Extracted title or None if not found
    """
    for tag, attrs in METADATA_SELECTORS['title']:
        title_elem = soup.find(tag, attrs)
        if title_elem:
            title = title_elem.get('content', '') if tag == 'meta' else title_elem.get_text()
            if title and len(title.strip()) > 0:
                # Clean up title
                title = clean_title(title)
                if title:
                    return title
    return None

def clean_title(title: str) -> Optional[str]:
    """Clean up a webpage title.
    
    Args:
        title: Title to clean
        
    Returns:
        Cleaned title or None if invalid
    """
    if not title:
        return None
        
    title = title.strip()
    
    # Remove common auto-generated prefixes
    prefixes = [
        r'^References\s*[-:]\s*',
        r'^Citation[s]?\s*[-:]\s*',
        r'^Bibliography\s*[-:]\s*',
        r'^\[\d+\]\s*',
        r'^\d+\.\s*'
    ]
    for pattern in prefixes:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    # Remove site names and common suffixes
    site_suffixes = [
        r'\s*[-|]\s*.*$',  # Remove anything after - or |
        r'\s*–\s*.*$',     # Remove anything after en dash
        r'\s*:\s*Latest.*$',  # Remove "Latest..." suffixes
        r'\s*\|.*$',       # Remove anything after |
        r'\s*-\s*\w+\.\w+$',  # Remove domain names
        r'\s*@\s*\w+$'     # Remove social media handles
    ]
    for pattern in site_suffixes:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    # Remove HTML entities
    title = re.sub(r'&[a-zA-Z]+;', '', title)
    
    # Remove extra whitespace
    title = ' '.join(title.split())
    
    # Check if title looks auto-generated
    if re.match(r'^[0-9a-f]{8,}$', title, re.IGNORECASE):  # Hex string
        return None
    if len(title) < 3:  # Too short
        return None
        
    title = title.strip()
    return title if title else None

def extract_authors(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract authors from webpage.
    
    Args:
        soup: BeautifulSoup object of the webpage
        
    Returns:
        List of author dictionaries with first_name and last_name keys
    """
    authors = []
    
    # First try to find JSON-LD metadata
    authors.extend(extract_authors_from_json_ld(soup))
    
    # Then try other methods if no authors found
    if not authors:
        for tag, attrs in METADATA_SELECTORS['author']:
            elements = soup.find_all(tag, attrs)
            for elem in elements:
                if tag == 'meta':
                    author = elem.get('content', '')
                elif tag == 'ul':
                    # For lists, get all child items
                    items = elem.find_all(['li', 'a', 'span'])
                    for item in items:
                        author = item.get_text()
                        if cleaned_name := clean_author_name(author):
                            name_parts = parse_author_name(cleaned_name)
                            if name_parts:
                                authors.append(name_parts)
                    continue
                else:
                    author = elem.get_text()
                
                if author:
                    name_parts = parse_author_name(clean_author_name(author))
                    if name_parts:
                        authors.append(name_parts)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_authors = []
    for author in authors:
        key = (author['first_name'].lower(), author['last_name'].lower())
        if key not in seen:
            seen.add(key)
            unique_authors.append(author)
    
    return unique_authors

def parse_author_name(name: str) -> Optional[Dict[str, str]]:
    """Parse author name into first name and last name.
    
    Args:
        name: Author name string
        
    Returns:
        Dictionary with first_name and last_name keys, or None if parsing fails
    """
    if not name:
        return None
        
    # Remove titles and suffixes
    titles = r'(?:Dr|Prof|Mr|Mrs|Ms|PhD|MD|DDS|DVM|Jr|Sr|I{1,3}|IV|V|VI)'
    name = re.sub(rf'\b{titles}\b\.?\s*', '', name, flags=re.IGNORECASE)
    
    # Try different name formats
    if ',' in name:  # Last, First
        last_name, first_name = name.split(',', 1)
        return {
            'first_name': first_name.strip(),
            'last_name': last_name.strip()
        }
    else:  # First Last
        parts = name.strip().split()
        if len(parts) >= 2:
            return {
                'first_name': ' '.join(parts[:-1]),
                'last_name': parts[-1]
            }
    
    return None

def extract_authors_from_json_ld(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract authors from JSON-LD data in the webpage.
    
    Args:
        soup: BeautifulSoup object of the webpage
        
    Returns:
        List of extracted author dictionaries
    """
    authors = []
    
    for script in soup.find_all('script', {'type': 'application/ld+json'}):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                if '@graph' in data:
                    for item in data['@graph']:
                        if isinstance(item, dict) and 'author' in item:
                            extract_author_from_json_ld_data(item['author'], authors)
                elif 'author' in data:
                    extract_author_from_json_ld_data(data['author'], authors)
        except:
            continue
    
    return authors

def extract_author_from_json_ld_data(author_data: Any, authors: List[Dict[str, str]]) -> None:
    """Extract author names from JSON-LD data and append to authors list.
    
    Args:
        author_data: Author data from JSON-LD
        authors: List to append extracted names to
    """
    if isinstance(author_data, list):
        for author in author_data:
            if isinstance(author, dict):
                if 'name' in author:
                    if cleaned_name := clean_author_name(author['name']):
                        name_parts = parse_author_name(cleaned_name)
                        if name_parts:
                            authors.append(name_parts)
                elif 'url' in author:
                    if cleaned_name := clean_author_name(author['url']):
                        name_parts = parse_author_name(cleaned_name)
                        if name_parts:
                            authors.append(name_parts)
    elif isinstance(author_data, dict):
        if 'name' in author_data:
            if cleaned_name := clean_author_name(author_data['name']):
                name_parts = parse_author_name(cleaned_name)
                if name_parts:
                    authors.append(name_parts)
        elif 'url' in author_data:
            if cleaned_name := clean_author_name(author_data['url']):
                name_parts = parse_author_name(cleaned_name)
                if name_parts:
                    authors.append(name_parts)
    elif isinstance(author_data, str):
        if cleaned_name := clean_author_name(author_data):
            name_parts = parse_author_name(cleaned_name)
            if name_parts:
                authors.append(name_parts)

def extract_date(soup: BeautifulSoup) -> Optional[str]:
    """Extract publication date from webpage.
    
    Args:
        soup: BeautifulSoup object of the webpage
        
    Returns:
        Extracted date string or None if not found
    """
    for tag, attrs in METADATA_SELECTORS['date']:
        date_elem = soup.find(tag, attrs)
        if date_elem:
            date_str = date_elem.get('content') or date_elem.get('datetime') or date_elem.get_text()
            if date_str:
                return date_str.strip()
    return None 