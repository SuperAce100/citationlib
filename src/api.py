"""
Main API for the citations library.

This module provides the main interface for generating citations in various
styles and output formats.
"""

from typing import List, Optional, Union, Dict, Any
from enum import Enum, auto
from datetime import datetime

from .styles import (
    Author, Citation, CitationStyle,
    APAStyle, MLAStyle, ChicagoStyle
)
from .output import (
    OutputFormatter, PlainTextFormatter, HTMLFormatter,
    MarkdownFormatter, LaTeXFormatter, BibTeXFormatter
)
from .metadata import extract_metadata
from .exceptions import CitationError

class Style(Enum):
    """Supported citation styles."""
    APA = auto()
    MLA = auto()
    CHICAGO = auto()

class Format(Enum):
    """Supported output formats."""
    PLAIN = auto()
    HTML = auto()
    MARKDOWN = auto()
    LATEX = auto()
    BIBTEX = auto()

def _convert_author_dict_to_object(author_dict: Dict[str, str]) -> Author:
    """Convert an author dictionary to an Author object."""
    return Author(
        first_name=author_dict['first_name'],
        last_name=author_dict['last_name'],
        middle_name=author_dict.get('middle_name')
    )

def create_citation(
    url: str,
    style: Style = Style.APA,
    output_format: Format = Format.PLAIN
) -> str:
    """
    Create a citation for the given URL in the specified style and format.
    
    Args:
        url: The URL to create a citation for
        style: The citation style to use (default: APA)
        output_format: The output format (default: plain text)
        
    Returns:
        str: The formatted citation
        
    Raises:
        CitationError: If the citation cannot be created
    """
    # Extract metadata
    try:
        metadata = extract_metadata(url)
    except Exception as e:
        raise CitationError(f"Failed to extract metadata: {str(e)}")
    
    # Convert author dictionaries to Author objects if needed
    authors = []
    for author in metadata.get('authors', []):
        if isinstance(author, dict):
            authors.append(_convert_author_dict_to_object(author))
        else:
            authors.append(author)
    
    # Create Citation object
    citation = Citation(
        authors=authors,
        title=metadata.get('title', ''),
        year=metadata.get('year'),
        journal=metadata.get('journal'),
        volume=metadata.get('volume'),
        issue=metadata.get('issue'),
        pages=metadata.get('pages'),
        doi=metadata.get('doi'),
        url=url,
        accessed_date=datetime.now(),
        publisher=metadata.get('publisher'),
        location=metadata.get('location')
    )
    
    # Get citation style
    style_map = {
        Style.APA: APAStyle(),
        Style.MLA: MLAStyle(),
        Style.CHICAGO: ChicagoStyle()
    }
    citation_style = style_map[style]
    
    # Format citation according to style
    citation_text = citation_style.format_citation(citation)
    
    # Get output formatter
    format_map = {
        Format.PLAIN: PlainTextFormatter(),
        Format.HTML: HTMLFormatter(),
        Format.MARKDOWN: MarkdownFormatter(),
        Format.LATEX: LaTeXFormatter(),
        Format.BIBTEX: BibTeXFormatter()
    }
    formatter = format_map[output_format]
    
    # Special handling for BibTeX
    if output_format == Format.BIBTEX:
        return formatter.format_entry(citation)
    
    # Format output
    return formatter.format(citation_text)

def create_apa_citation(url: str) -> str:
    """
    Create an APA citation for the given URL (plain text format).
    Maintained for backwards compatibility.
    """
    return create_citation(url, Style.APA, Format.PLAIN)

def extract_authors(url: str) -> List[Author]:
    """
    Extract authors from the given URL.
    Maintained for backwards compatibility.
    """
    try:
        metadata = extract_metadata(url)
        authors = []
        for author in metadata.get('authors', []):
            if isinstance(author, dict):
                authors.append(_convert_author_dict_to_object(author))
            else:
                authors.append(author)
        return authors
    except Exception as e:
        raise CitationError(f"Failed to extract authors: {str(e)}")

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