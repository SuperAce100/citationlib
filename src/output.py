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

class OutputFormatter(ABC):
    """Abstract base class for output formatters."""
    
    @abstractmethod
    def format(self, citation: str) -> str:
        """Format the citation string into the desired output format."""
        pass

class PlainTextFormatter(OutputFormatter):
    """Plain text output formatter."""
    
    def format(self, citation: str) -> str:
        return citation

class HTMLFormatter(OutputFormatter):
    """HTML output formatter."""
    
    def format(self, citation: str) -> str:
        return f'<p class="citation">{citation}</p>'

class MarkdownFormatter(OutputFormatter):
    """Markdown output formatter."""
    
    def format(self, citation: str) -> str:
        return f"> {citation}"

class LaTeXFormatter(OutputFormatter):
    """LaTeX output formatter."""
    
    def format(self, citation: str) -> str:
        # Escape special LaTeX characters
        escaped = citation.replace('&', '\\&').replace('%', '\\%')
        return f"\\begin{{quote}}\n{escaped}\n\\end{{quote}}"

class BibTeXFormatter(OutputFormatter):
    """BibTeX output formatter."""
    
    def _generate_key(self, citation: Citation) -> str:
        """Generate a BibTeX citation key."""
        if citation.authors:
            author = citation.authors[0].last_name.lower()
        else:
            author = "unknown"
            
        year = citation.year or "unknown"
        
        # Take first word of title
        title_word = citation.title.split()[0].lower()
        
        return f"{author}{year}{title_word}"
    
    def format_entry(self, citation: Citation) -> str:
        """Format a Citation object as a BibTeX entry."""
        key = self._generate_key(citation)
        
        # Determine entry type
        if citation.journal:
            entry_type = "article"
        elif citation.publisher:
            entry_type = "book"
        else:
            entry_type = "misc"
            
        fields: Dict[str, Any] = {
            "title": citation.title,
            "year": citation.year,
        }
        
        # Add authors if present
        if citation.authors:
            authors = " and ".join(
                f"{a.last_name}, {a.first_name}" for a in citation.authors
            )
            fields["author"] = authors
            
        # Add other fields if present
        if citation.journal:
            fields["journal"] = citation.journal
        if citation.volume:
            fields["volume"] = citation.volume
        if citation.issue:
            fields["number"] = citation.issue
        if citation.pages:
            fields["pages"] = citation.pages
        if citation.doi:
            fields["doi"] = citation.doi
        if citation.url:
            fields["url"] = citation.url
        if citation.publisher:
            fields["publisher"] = citation.publisher
            
        # Format BibTeX entry
        lines = [f"@{entry_type}{{{key},"]
        for field, value in fields.items():
            if value is not None:  # Skip None values
                # Escape special characters and wrap in braces
                value_str = str(value).replace('"', '\\"')
                lines.append(f'    {field} = {{{value_str}}},')
        lines.append("}")
        
        return "\n".join(lines)
    
    def format(self, citation: str) -> str:
        """
        Note: This method expects a string, but BibTeX formatting requires
        the original Citation object. Use format_entry() instead for proper
        BibTeX output.
        """
        raise NotImplementedError(
            "BibTeX formatting requires the original Citation object. "
            "Use format_entry() instead."
        ) 