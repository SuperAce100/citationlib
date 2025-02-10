"""
CitationLib - A library for generating citations from various sources.

This library supports multiple citation styles (APA, MLA, Chicago) and
output formats (plain text, HTML, Markdown, LaTeX, BibTeX).
"""

__version__ = "1.0.0"

from .api import (
    create_citation,
    create_apa_citation,
    extract_authors,
    Style,
    Format,
    Author,
    Citation,
    CitationError
)

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