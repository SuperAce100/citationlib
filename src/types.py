"""Type definitions for the citations package."""

from typing import Dict, List, Optional, Any, TypedDict, Tuple, Union

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