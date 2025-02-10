"""Citation formatting functionality for the citations package."""

import re
from typing import List, Optional, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from habanero import Crossref
from arxiv import Search
from urllib.parse import urlparse

from .config import HTTP_HEADERS, REQUEST_TIMEOUT, TOOL_NAME
from .exceptions import (
    DOIError,
    ArXivError,
    PubMedError,
    PMCError,
    WebpageError
)
from .metadata import extract_webpage_metadata
from .utils import format_author_list, get_site_name
from .scraper import get_webpage_content

class CitationFormatter:
    """A class to handle creation of APA citations for different types of sources."""
    
    def __init__(self):
        """Initialize the CitationFormatter."""
        self.crossref = Crossref()
        self.tool = TOOL_NAME
    
    def create_doi_citation(self, doi: str) -> str:
        """Create an APA citation for a DOI.
        
        Args:
            doi: The DOI to create a citation for
            
        Returns:
            HTML formatted APA citation
            
        Raises:
            DOIError: If citation creation fails
        """
        try:
            work = self.crossref.works(ids=doi)['message']
            
            # Extract authors
            authors = work.get('author', [])
            if authors:
                if len(authors) == 1:
                    author_text = f"{authors[0]['family']}, {authors[0]['given'][0]}."
                elif len(authors) == 2:
                    author_text = f"{authors[0]['family']}, {authors[0]['given'][0]}., & {authors[1]['family']}, {authors[1]['given'][0]}."
                else:
                    author_text = f"{authors[0]['family']}, {authors[0]['given'][0]}., et al."
            else:
                author_text = ""
            
            # Extract metadata
            title = work.get('title', [''])[0]
            journal = work.get('container-title', [''])[0]
            year = work.get('published-print', {}).get('date-parts', [['']])[0][0]
            volume = work.get('volume', '')
            issue = work.get('issue', '')
            pages = work.get('page', '')
            
            # Format citation
            citation = f"{author_text} ({year}). {title}. "
            if journal:
                citation += f"<i>{journal}</i>"
                if volume:
                    citation += f", <i>{volume}</i>"
                if issue:
                    citation += f"({issue})"
                if pages:
                    citation += f", {pages}"
            citation += f". https://doi.org/{doi}"
            
            return citation
        except Exception as e:
            raise DOIError(f"Error processing DOI citation: {str(e)}")
    
    def create_arxiv_citation(self, arxiv_id: str) -> str:
        """Create an APA citation for an arXiv paper.
        
        Args:
            arxiv_id: The arXiv ID to create a citation for
            
        Returns:
            HTML formatted APA citation
            
        Raises:
            ArXivError: If citation creation fails
        """
        try:
            search = Search(id_list=[arxiv_id])
            paper = next(search.results())
            
            # Convert arxiv Author objects to strings and format them
            author_names = [str(author) for author in paper.authors]
            author_text = format_author_list(author_names)
            if not author_text:
                author_text = ""
            
            return f"{author_text} ({paper.published.year}). {paper.title}. <i>arXiv preprint arXiv:{arxiv_id}</i>"
        except Exception as e:
            raise ArXivError(f"Error processing arXiv citation: {str(e)}")
    
    def create_pubmed_citation(self, pubmed_id: str) -> str:
        """Create an APA citation for a PubMed article using E-utilities.
        
        Args:
            pubmed_id: The PubMed ID to create a citation for
            
        Returns:
            HTML formatted APA citation
            
        Raises:
            PubMedError: If citation creation fails
        """
        try:
            # Remove 'PMID:' prefix if present
            pubmed_id = pubmed_id.replace('PMID:', '').strip()
            
            # First try to get the DOI using E-utilities
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pubmed_id}&retmode=json&tool={self.tool}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if 'result' not in data or pubmed_id not in data['result']:
                raise PubMedError(f"No data found for PubMed ID: {pubmed_id}")
            
            article = data['result'][pubmed_id]
            
            # Try to get DOI from the article data
            article_ids = article.get('articleids', [])
            doi = next((id_obj['value'] for id_obj in article_ids if id_obj['idtype'].lower() == 'doi'), None)
            
            # If we found a DOI, use it for citation
            if doi:
                return self.create_doi_citation(doi)
            
            # If no DOI found, proceed with PubMed citation
            # Extract authors
            authors = article.get('authors', [])
            if authors:
                formatted_authors = []
                for author in authors:
                    name = author.get('name', '')
                    if name:
                        # Split name into parts (assuming last, first format)
                        parts = name.split(',', 1)
                        if len(parts) == 2:
                            last_name = parts[0].strip()
                            first_name = parts[1].strip()
                            formatted_name = f"{last_name}, {first_name[0]}."
                            formatted_authors.append(formatted_name)
                        else:
                            formatted_authors.append(name)
                
                if len(formatted_authors) == 1:
                    author_text = formatted_authors[0]
                elif len(formatted_authors) == 2:
                    author_text = f"{formatted_authors[0]} & {formatted_authors[1]}"
                else:
                    author_text = f"{formatted_authors[0]} et al."
            else:
                author_text = ""
            
            # Extract other metadata
            title = article.get('title', '')
            journal = article.get('fulljournalname', article.get('source', ''))
            volume = article.get('volume', '')
            issue = article.get('issue', '')
            pages = article.get('pages', '')
            year = article.get('pubdate', '').split()[0]
            
            # Format citation
            citation_parts = []
            
            if author_text:
                citation_parts.append(f"{author_text}")
                citation_parts.append(f"({year})")
            else:
                citation_parts.append(title)
                citation_parts.append(f"({year})")
            
            if author_text:
                citation_parts.append(title)
            
            if journal:
                journal_part = f"<i>{journal}</i>"
                if volume:
                    journal_part += f", {volume}"
                if issue:
                    journal_part += f"({issue})"
                if pages:
                    journal_part += f", {pages}"
                citation_parts.append(journal_part)
            
            citation_parts.append(f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/")
            
            return ". ".join(citation_parts)
            
        except Exception as e:
            raise PubMedError(f"Error processing PubMed citation: {str(e)}")
    
    def create_pmc_citation(self, pmc_id: str) -> str:
        """Create an APA citation for a PMC article using E-utilities.
        
        Args:
            pmc_id: The PMC ID to create a citation for
            
        Returns:
            HTML formatted APA citation
            
        Raises:
            PMCError: If citation creation fails
        """
        try:
            # Remove 'PMC' prefix if present
            pmc_id = pmc_id.replace('PMC', '').strip()
            
            # Fetch article metadata using E-utilities
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id={pmc_id}&retmode=json&tool={self.tool}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if 'result' not in data or pmc_id not in data['result']:
                raise PMCError(f"No data found for PMC ID: {pmc_id}")
            
            article = data['result'][pmc_id]
            
            # Extract authors
            authors = article.get('authors', [])
            if authors:
                if len(authors) == 1:
                    author_text = f"{authors[0]['name']}"
                elif len(authors) == 2:
                    author_text = f"{authors[0]['name']} & {authors[1]['name']}"
                else:
                    author_text = f"{authors[0]['name']} et al."
            else:
                author_text = ""
            
            # Extract other metadata
            title = article.get('title', '')
            journal = article.get('fulljournalname', article.get('source', ''))
            volume = article.get('volume', '')
            issue = article.get('issue', '')
            pages = article.get('pages', '')
            year = article.get('pubdate', '').split()[0]
            
            # Format citation
            citation_parts = []
            
            if author_text:
                citation_parts.append(f"{author_text}")
                citation_parts.append(f"({year})")
            else:
                citation_parts.append(title)
                citation_parts.append(f"({year})")
            
            if author_text:
                citation_parts.append(title)
            
            if journal:
                journal_part = f"<i>{journal}</i>"
                if volume:
                    journal_part += f", {volume}"
                if issue:
                    journal_part += f"({issue})"
                if pages:
                    journal_part += f", {pages}"
                citation_parts.append(journal_part)
            
            citation_parts.append(f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/")
            
            return ". ".join(citation_parts)
            
        except Exception as e:
            raise PMCError(f"Error processing PMC citation: {str(e)}")
    
    def create_webpage_citation(self, url: str) -> str:
        """Create an APA citation for a webpage.
        
        Args:
            url: The URL to create a citation for
            
        Returns:
            HTML formatted APA citation
        """
        citation_parts = []
        current_year = datetime.now().year
        
        try:
            # Try to get full metadata
            soup = get_webpage_content(url)
            metadata = extract_webpage_metadata(soup, url)
            
            # Try DOI citation first if available
            if metadata.get('doi'):
                try:
                    return self.create_doi_citation(metadata['doi'])
                except DOIError:
                    pass  # Fall back to webpage citation
            
            # Get whatever data we can
            title = metadata.get('title')
            authors = metadata.get('authors', [])
            pub_date = metadata.get('pub_date')
            site_name = metadata.get('site_name')
            
        except Exception as e:
            # If scraping fails, create citation with minimal data
            title = None
            authors = []
            pub_date = None
            site_name = None
        
        # If we couldn't get the site name from metadata, extract it from URL
        if not site_name:
            site_name = get_site_name(url)
        
        # If we couldn't get the title, create one from the URL path
        if not title:
            path = urlparse(url).path.strip('/')
            if path:
                # Convert URL path to title case, replace hyphens and underscores with spaces
                title = ' '.join(word.capitalize() for word in re.split(r'[-_/]', path))
            else:
                title = site_name
        
        # Get publication year
        pub_year = current_year
        if pub_date:
            try:
                pub_datetime = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                pub_year = pub_datetime.year
            except (ValueError, AttributeError):
                pass
        
        # Format based on whether authors exist
        author_text = format_author_list(authors) if authors else None
        if author_text:
            # Case 1: Authors exist - standard format
            citation_parts.append(author_text)
            citation_parts.append(f"({pub_year})")
            if title:
                citation_parts.append(title)
        else:
            # Case 2: No authors - move title to first position
            if title:
                citation_parts.append(title)
            citation_parts.append(f"({pub_year})")
        
        # Add site name
        if site_name:
            citation_parts.append(f"<i>{site_name}</i>")
        
        # Add retrieval date and URL
        citation_parts.append(f"Retrieved {datetime.now().strftime('%B %d, %Y')}, from {url}")
        
        return ". ".join(citation_parts) 