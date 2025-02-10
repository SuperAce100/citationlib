"""
Output formatters for different citation formats.

This module provides formatters for converting citations to different output formats:
- Plain text
- HTML
- Markdown
- LaTeX
- BibTeX
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from .styles import Citation
import re

class OutputFormatter(ABC):
    """Abstract base class for output formatters."""
    
    def _extract_url(self, text: str) -> str:
        """Extract URL from text."""
        url_match = re.search(r'https?://[^\s]+', text)
        return url_match.group(0) if url_match else None
    
    def _handle_error_with_url(self, error_text: str) -> str:
        """Extract URL from error message and create a basic citation."""
        url = self._extract_url(error_text)
        if url:
            # Try to extract a title from the URL path
            path = url.split('/')[-1].replace('-', ' ').title()
            return f"{path}. Retrieved from {url}"
        return error_text
    
    @abstractmethod
    def format(self, citation: str) -> str:
        """Format the citation string into the desired output format."""
        pass

class PlainTextFormatter(OutputFormatter):
    """Plain text output formatter."""
    
    def format(self, citation: str) -> str:
        if "Error creating citation:" in citation:
            return self._handle_error_with_url(citation)
        return citation

class HTMLFormatter(OutputFormatter):
    """HTML output formatter."""
    
    def format(self, citation: str) -> str:
        if "Error creating citation:" in citation:
            citation = self._handle_error_with_url(citation)
        return f'<p class="citation">{citation}</p>'

class MarkdownFormatter(OutputFormatter):
    """Markdown output formatter."""
    
    def format(self, citation: str) -> str:
        if "Error creating citation:" in citation:
            citation = self._handle_error_with_url(citation)
        return f"> {citation}"

class LaTeXFormatter(OutputFormatter):
    """LaTeX output formatter."""
    
    def format(self, citation: str) -> str:
        if "Error creating citation:" in citation:
            citation = self._handle_error_with_url(citation)
        # Escape special LaTeX characters
        escaped = citation.replace('&', '\\&').replace('%', '\\%')
        return f"\\begin{{quote}}\n{escaped}\n\\end{{quote}}"

class BibTeXFormatter(OutputFormatter):
    """BibTeX output formatter."""
    
    def _generate_key(self, title: str) -> str:
        """Generate a BibTeX citation key from title."""
        # Take first word of title and clean it
        title_word = ''.join(c.lower() for c in title.split()[0] if c.isalnum())
        return f"citation_{title_word}"
    
    def format(self, citation_text: str) -> str:
        """Format a citation string as a BibTeX entry."""
        try:
            # Check for error messages first
            if "Error creating citation:" in citation_text:
                url = self._extract_url(citation_text)
                if url:
                    # Try to extract a title from the URL path
                    path = url.split('/')[-1].replace('-', ' ').title()
                    return f"@misc{{citation_website,\n  title = {{{path}}},\n  howpublished = {{{url}}},\n  note = {{Retrieved from website}}\n}}"
                return citation_text
            
            # Try to match standard academic citation first
            author_year_match = re.match(r'(.*?)\. \((\d{4})\)', citation_text)
            if author_year_match:
                authors = author_year_match.group(1)
                year = author_year_match.group(2)
                
                # Extract title and rest
                remaining_text = citation_text[author_year_match.end():].strip('. ')
                title_match = re.match(r'(.*?)(?:\. |$)(.*)', remaining_text)
                if not title_match:
                    return citation_text
                    
                title = title_match.group(1)
                rest = title_match.group(2)
                
                # Generate citation key
                key = self._generate_key(title)
                
                # Format BibTeX entry
                entry = [
                    f"@article{{{key},",
                    f"  author = {{{authors}}},",
                    f"  year = {{{year}}},",
                    f"  title = {{{title}}}"
                ]
                
                # Add journal/url if present
                if rest:
                    if 'http' in rest:
                        entry.append(f"  url = {{{rest}}}")
                    else:
                        parts = rest.split(', ')
                        if len(parts) >= 1:
                            entry.append(f"  journal = {{{parts[0]}}}")
                        if len(parts) >= 2:
                            # Handle volume and issue
                            vol_issue = parts[1]
                            if 'vol.' in vol_issue:
                                vol = vol_issue.split('vol.')[1].strip()
                                entry.append(f"  volume = {{{vol}}}")
                            if 'no.' in vol_issue:
                                issue = vol_issue.split('no.')[1].strip()
                                entry.append(f"  number = {{{issue}}}")
                        if len(parts) >= 3:
                            # Handle pages
                            if 'pp.' in parts[2]:
                                pages = parts[2].split('pp.')[1].strip()
                                entry.append(f"  pages = {{{pages}}}")
                
            else:
                # Handle web resources without traditional citation format
                # Extract title and URL
                parts = citation_text.split('. ')
                if len(parts) < 1:
                    return citation_text
                
                title = parts[0].strip('"')  # Remove quotes if present
                url = self._extract_url(citation_text)
                
                key = self._generate_key(title)
                entry = [
                    f"@misc{{{key},",
                    f"  title = {{{title}}}"
                ]
                
                if url:
                    entry.append(f"  howpublished = {{{url}}}")
                    
            entry.append("}")
            return "\n".join(entry)
            
        except Exception as e:
            # Final fallback - if URL is present, create minimal citation
            url = self._extract_url(citation_text)
            if url:
                path = url.split('/')[-1].replace('-', ' ').title()
                return f"@misc{{citation_website,\n  title = {{{path}}},\n  howpublished = {{{url}}},\n  note = {{Retrieved from website}}\n}}"
            return f"Error creating BibTeX: {str(e)}" 