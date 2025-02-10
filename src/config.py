"""Configuration settings for the citations package."""

from typing import Dict

# User agent for HTTP requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# HTTP headers for requests
HTTP_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# Tool name for NCBI E-utilities
TOOL_NAME = "CitationLib"

# Common name suffixes to ignore
NAME_SUFFIXES = ["jr", "sr", "ii", "iii", "iv"]

# Common professional titles to remove
PROFESSIONAL_TITLES = [
    "phd", "md", "dds", "jd", "esq", "professor", "dr",
    "staff writer", "reporter", "editor", "correspondent",
    "writer", "author", "contributor"
]

# Site name mappings for common domains
SITE_NAME_MAPPING: Dict[str, str] = {
    "plato.stanford.edu": "Stanford Encyclopedia of Philosophy",
    "research.google": "Google Research",
    "research.facebook.com": "Meta Research",
    "openai.com": "OpenAI",
    "arxiv.org": "arXiv",
    "nih.gov": "National Institutes of Health",
    "who.int": "World Health Organization",
    "unesco.org": "UNESCO",
    "whitehouse.gov": "The White House",
    "nytimes.com": "The New York Times",
    "theguardian.com": "The Guardian",
    "wsj.com": "The Wall Street Journal",
    "washingtonpost.com": "The Washington Post",
    "bbc.com": "BBC News",
    "bbc.co.uk": "BBC News",
    "reuters.com": "Reuters",
    "bloomberg.com": "Bloomberg",
    "forbes.com": "Forbes",
    "cnn.com": "CNN",
    "nbcnews.com": "NBC News",
    "foxnews.com": "Fox News",
    "apnews.com": "Associated Press",
    "npr.org": "NPR",
    "latimes.com": "Los Angeles Times",
    "chicagotribune.com": "Chicago Tribune",
    "usatoday.com": "USA Today",
    "sciencedirect.com": "ScienceDirect",
    "nature.com": "Nature",
    "science.org": "Science",
    "wired.com": "WIRED",
    "pubmed.ncbi.nlm.nih.gov": "PubMed"
}

# HTML selectors for metadata extraction
METADATA_SELECTORS = {
    "title": [
        ("meta", {"property": "og:title"}),
        ("meta", {"property": "twitter:title"}),
        ("meta", {"name": "title"}),
        ("meta", {"name": "citation_title"}),
        ("meta", {"name": "dc.title"}),
        ("h1", {"class": ["article-title", "entry-title", "title", "heading-title", "article-header__title"]}),
        ("h1", {}),
        ("title", {})
    ],
    "author": [
        ("meta", {"itemprop": "author"}),
        ("meta", {"property": "article:author"}),
        ("meta", {"name": "author"}),
        ("meta", {"name": "citation_author"}),
        ("meta", {"name": "dc.creator"}),
        ("span", {"class": ["author", "byline", "writer", "contributor", "article__author-name"]}),
        ("div", {"class": ["author", "byline", "writer", "contributor", "article__author-name"]}),
        ("a", {"class": ["author", "byline", "writer", "contributor", "article__author-name"]}),
        ("a", {"rel": "author"}),
        ("ul", {"class": ["authors-list", "author-list", "contributors", "article__author-list"]}),
        ("div", {"class": "authors-list"}),
        ("span", {"class": "authors-list-item"})
    ],
    "date": [
        ("meta", {"property": "article:published_time"}),
        ("meta", {"property": "og:article:published_time"}),
        ("meta", {"name": "publication_date"}),
        ("meta", {"name": "citation_date"}),
        ("meta", {"name": "dc.date"}),
        ("time", {"datetime": True}),
        ("time", {"class": ["publish-date", "publication-date", "date", "article__date"]}),
        ("span", {"class": "publish-date"})
    ]
} 