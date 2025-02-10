"""
Citation styles module providing different citation format implementations.

This module contains the base CitationStyle class and implementations for
APA, MLA, and Chicago citation styles.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import re

@dataclass
class Author:
    """Represents an author with first name, last name, and middle name."""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    
    def __str__(self) -> str:
        """Format author name as 'Last, F.'"""
        return f"{self.last_name}, {self.first_name[0]}."
    
    def full_name(self) -> str:
        """Format author name as 'First Last'"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

@dataclass
class Citation:
    """Base class containing metadata for a citation."""
    authors: List[Author]
    title: str
    year: Optional[int]
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    accessed_date: Optional[datetime] = None
    publisher: Optional[str] = None
    location: Optional[str] = None

def sentence_case(text: str) -> str:
    """Convert text to sentence case (capitalize first letter and proper nouns)."""
    if not text:
        return text
    
    # Split into sentences
    sentences = re.split(r'([.!?]+\s+)', text)
    result = []
    
    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        if not sentence:
            continue
            
        # Capitalize first letter
        sentence = sentence[0].upper() + sentence[1:].lower()
        
        # Capitalize proper nouns (simplified approach)
        proper_nouns = [
            'I', 'AI', 'GPT', 'Google', 'Facebook', 'OpenAI', 'Microsoft',
            'Python', 'JavaScript', 'Linux', 'Windows', 'Mac', 'Internet',
            'Web', 'API', 'REST', 'GraphQL', 'HTTP', 'URL', 'HTML', 'CSS'
        ]
        
        for noun in proper_nouns:
            sentence = re.sub(
                rf'\b{noun.lower()}\b',
                noun,
                sentence,
                flags=re.IGNORECASE
            )
        
        result.append(sentence)
        if i + 1 < len(sentences):
            result.append(sentences[i + 1])
    
    return ''.join(result)

def clean_url(url: str) -> str:
    """Clean URL by removing trailing slashes and periods."""
    return url.rstrip('/.')

class CitationStyle(ABC):
    """Abstract base class for citation styles."""
    
    @abstractmethod
    def format_authors(self, authors: List[Author]) -> str:
        """Format the author list according to the citation style."""
        pass
    
    @abstractmethod
    def format_citation(self, citation: Citation) -> str:
        """Format the complete citation according to the style guidelines."""
        pass

class APAStyle(CitationStyle):
    """APA (7th edition) citation style implementation."""
    
    def format_authors(self, authors: List[Author]) -> str:
        if not authors:
            return ""
        
        if len(authors) == 1:
            return str(authors[0])
        
        if len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
            
        return f"{', '.join(str(a) for a in authors[:-1])}, & {authors[-1]}"
    
    def format_citation(self, citation: Citation) -> str:
        parts = []
        
        # Authors and year
        authors = self.format_authors(citation.authors)
        if authors:
            parts.append(f"{authors}")
            if citation.year:
                parts.append(f"({citation.year})")
        
        # Title in sentence case
        if citation.title:
            parts.append(sentence_case(citation.title))
        
        # Journal info
        if citation.journal:
            journal_parts = [citation.journal]
            
            # Volume and issue
            if citation.volume:
                if citation.issue:
                    journal_parts.append(f"{citation.volume}({citation.issue})")
                else:
                    journal_parts.append(citation.volume)
                    
            # Pages
            if citation.pages:
                journal_parts.append(citation.pages)
                
            parts.append(", ".join(journal_parts))
        
        # DOI or URL (without "Retrieved from" for stable URLs)
        if citation.doi:
            parts.append(clean_url(f"https://doi.org/{citation.doi}"))
        elif citation.url:
            parts.append(clean_url(citation.url))
        
        return ". ".join(p for p in parts if p) + "."

class MLAStyle(CitationStyle):
    """MLA (9th edition) citation style implementation."""
    
    def format_authors(self, authors: List[Author]) -> str:
        if not authors:
            return ""
        
        if len(authors) == 1:
            return authors[0].full_name()
        
        if len(authors) == 2:
            return f"{authors[0].full_name()} and {authors[1].full_name()}"
            
        return f"{authors[0].full_name()} et al."
    
    def format_citation(self, citation: Citation) -> str:
        parts = []
        
        # Authors
        authors = self.format_authors(citation.authors)
        if authors:
            parts.append(authors)
        
        # Title
        if citation.title:
            parts.append(f'"{citation.title}"')
        
        # Container (journal, etc.)
        if citation.journal:
            parts.append(citation.journal)
            
        # Publication details
        pub_details = []
        if citation.volume:
            pub_details.append(f"vol. {citation.volume}")
        if citation.issue:
            pub_details.append(f"no. {citation.issue}")
        if citation.year:
            pub_details.append(str(citation.year))
        if pub_details:
            parts.append(", ".join(pub_details))
            
        # Pages
        if citation.pages:
            parts.append(f"pp. {citation.pages}")
            
        # DOI or URL
        if citation.doi:
            parts.append(clean_url(f"https://doi.org/{citation.doi}"))
        elif citation.url:
            parts.append(clean_url(citation.url))
        
        return ", ".join(p for p in parts if p) + "."

class ChicagoStyle(CitationStyle):
    """Chicago (17th edition) citation style implementation."""
    
    def format_authors(self, authors: List[Author]) -> str:
        if not authors:
            return ""
        
        if len(authors) == 1:
            return authors[0].full_name()
        
        # Remove extra period after "et al"
        return f"{authors[0].full_name()} et al"
    
    def format_citation(self, citation: Citation) -> str:
        parts = []
        
        # Authors
        authors = self.format_authors(citation.authors)
        if authors:
            parts.append(authors)
        
        # Title
        if citation.title:
            parts.append(f'"{citation.title}"')
        
        # Journal info
        if citation.journal:
            journal_info = [citation.journal]
            if citation.volume:
                journal_info.append(citation.volume)
            if citation.issue:
                journal_info.append(f"no. {citation.issue}")
            parts.append(" ".join(journal_info))
        
        # Year and pages
        pub_info = []
        if citation.year:
            pub_info.append(f"({citation.year})")
        if citation.pages:
            pub_info.append(f": {citation.pages}")
        if pub_info:
            parts.append("".join(pub_info))
        
        # DOI or URL
        if citation.doi:
            parts.append(clean_url(f"https://doi.org/{citation.doi}"))
        elif citation.url:
            parts.append(clean_url(citation.url))
        
        return ". ".join(p for p in parts if p) + "." 