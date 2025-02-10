"""
Main API for the citations library.

This module provides the main interface for generating citations in various
styles and output formats.
"""

from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

from .types import Style, Format, Author, Citation
from .styles import CitationStyle, APAStyle, MLAStyle, ChicagoStyle
from .output import (
    OutputFormatter, PlainTextFormatter, HTMLFormatter,
    MarkdownFormatter, LaTeXFormatter, BibTeXFormatter
)
from .metadata import extract_metadata
from .exceptions import CitationError
from .utils import get_site_name

def _convert_author_dict_to_object(author_dict: Dict[str, str]) -> Author:
    """Convert an author dictionary to an Author object."""
    return Author(
        first_name=author_dict.get('first_name', ''),
        last_name=author_dict.get('last_name', ''),
        middle_name=author_dict.get('middle_name'),
        suffix=author_dict.get('suffix')
    )

def _create_fallback_citation(url: str) -> Citation:
    """Create a fallback citation from just the URL."""
    # Parse URL to get domain and path
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.strip('/')
    
    # Create a title from the path
    title = path.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
    if not title:
        title = domain
    
    # Get site name
    site_name = get_site_name(url)
    
    return Citation(
        authors=[],  # No authors available
        title=title,
        year=datetime.now().year,  # Current year as access year
        url=url,
        accessed_date=datetime.now(),
        publisher=site_name
    )

def create_citation(
    url: str,
    style: Style = Style.APA,
    output_format: Format = Format.PLAIN
) -> str:
    """Create a citation for a given URL.
    
    Args:
        url: The URL to create a citation for
        style: The citation style to use
        output_format: The output format to use
        
    Returns:
        The formatted citation string
        
    Raises:
        CitationError: If there was an error creating the citation
    """
    try:
        # Extract metadata
        try:
            metadata = extract_metadata(url)
            citation = Citation(
                authors=[_convert_author_dict_to_object(a) for a in metadata['authors']],
                title=metadata['title'],
                year=metadata.get('year'),
                journal=metadata.get('journal'),
                volume=metadata.get('volume'),
                issue=metadata.get('issue'),
                pages=metadata.get('pages'),
                publisher=metadata.get('publisher'),
                doi=metadata.get('doi'),
                url=url,
                arxiv_id=metadata.get('arxiv_id'),
                pubmed_id=metadata.get('pubmed_id'),
                pmc_id=metadata.get('pmc_id'),
                accessed_date=datetime.now()
            )
        except Exception as e:
            # If metadata extraction fails, create a fallback citation
            citation = _create_fallback_citation(url)
        
        # Format citation
        if style == Style.APA:
            citation_style = APAStyle()
        elif style == Style.MLA:
            citation_style = MLAStyle()
        else:  # CHICAGO
            citation_style = ChicagoStyle()
            
        citation_text = citation_style.format_citation(citation)
        
        # Format output
        if output_format == Format.PLAIN:
            formatter = PlainTextFormatter()
        elif output_format == Format.HTML:
            formatter = HTMLFormatter()
        elif output_format == Format.MARKDOWN:
            formatter = MarkdownFormatter()
        elif output_format == Format.LATEX:
            formatter = LaTeXFormatter()
        else:  # BIBTEX
            formatter = BibTeXFormatter()
            
        return formatter.format(citation_text)
        
    except Exception as e:
        raise CitationError(f"Error creating citation: {str(e)}")

def create_apa_citation(url: str) -> str:
    """Create an APA citation for a given URL."""
    return create_citation(url, style=Style.APA)

def extract_authors(url: str) -> List[Author]:
    """Extract authors from a given URL."""
    metadata = extract_metadata(url)
    return [_convert_author_dict_to_object(a) for a in metadata['authors']]

__all__ = [
    "create_citation",
    "create_apa_citation",
    "extract_authors",
    "Style",
    "Format",
    "Author",
    "Citation",
    "CitationError"
] 