"""
CitationLib - A Python library for generating academic citations from various sources.

This library supports multiple citation styles (APA, MLA, Chicago) and
output formats (plain text, HTML, Markdown, LaTeX, BibTeX).
"""

__version__ = "0.1.7"

from .types import Style, Format
from .api import create_citation

__all__ = [
    "create_citation",
    "Style",
    "Format"
] 