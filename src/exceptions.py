"""Custom exceptions for the citations package."""

class CitationError(Exception):
    """Base exception for citation-related errors."""
    pass

class DOIError(CitationError):
    """Exception raised for DOI-related errors."""
    pass

class ArXivError(CitationError):
    """Exception raised for arXiv-related errors."""
    pass

class PubMedError(CitationError):
    """Exception raised for PubMed-related errors."""
    pass

class PMCError(CitationError):
    """Exception raised for PMC-related errors."""
    pass

class WebpageError(CitationError):
    """Exception raised for webpage-related errors."""
    pass

class MetadataExtractionError(CitationError):
    """Exception raised for metadata extraction errors."""
    pass

class AuthorExtractionError(CitationError):
    """Exception raised for author extraction errors."""
    pass 