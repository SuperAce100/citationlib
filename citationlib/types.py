"""Type definitions for the citations package."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, TypedDict, Tuple, Union

class Style(Enum):
    """Citation style enumeration."""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"

class Format(Enum):
    """Output format enumeration."""
    PLAIN = "plain"
    HTML = "html"
    MARKDOWN = "markdown"
    LATEX = "latex"
    BIBTEX = "bibtex"

@dataclass
class Author:
    """Author information."""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    suffix: Optional[str] = None
    
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
    """Citation information."""
    authors: List[Author]
    title: str
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    arxiv_id: Optional[str] = None
    pubmed_id: Optional[str] = None
    pmc_id: Optional[str] = None
    accessed_date: Optional[datetime] = None

# Type aliases
HTMLTag = str
HTMLAttrs = Dict[str, Union[str, List[str], bool]]
HTMLSelector = Tuple[HTMLTag, HTMLAttrs]

class WebpageMetadata(TypedDict):
    """Type definition for webpage metadata."""
    title: Optional[str]
    authors: List[str]
    pub_date: Optional[str]
    site_name: Optional[str]
    doi: Optional[str]

class CrossrefAuthor(TypedDict):
    """Type definition for Crossref author data."""
    family: str
    given: str

class CrossrefWork(TypedDict):
    """Type definition for Crossref work data."""
    author: List[CrossrefAuthor]
    title: List[str]
    container_title: List[str]
    published_print: Dict[str, List[List[str]]]
    volume: str
    issue: str
    page: str

class PubMedAuthor(TypedDict):
    """Type definition for PubMed author data."""
    name: str

class PubMedArticle(TypedDict):
    """Type definition for PubMed article data."""
    authors: List[PubMedAuthor]
    title: str
    fulljournalname: str
    volume: str
    issue: str
    pages: str
    pubdate: str
    articleids: List[Dict[str, str]]

class PMCArticle(TypedDict):
    """Type definition for PMC article data."""
    authors: List[PubMedAuthor]
    title: str
    fulljournalname: str
    volume: str
    issue: str
    pages: str
    pubdate: str 