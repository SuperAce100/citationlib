"""Web scraping functionality for the citations package."""

import time
import random
import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse

from .config import HTTP_HEADERS, REQUEST_TIMEOUT
from .exceptions import WebpageError

def get_random_user_agent() -> str:
    """Get a random user agent string to avoid detection."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
    ]
    return random.choice(user_agents)

def get_webpage_content(url: str) -> BeautifulSoup:
    """Get webpage content and return BeautifulSoup object.
    
    Args:
        url: URL to fetch
        
    Returns:
        BeautifulSoup object of the webpage
        
    Raises:
        WebpageError: If webpage cannot be fetched
    """
    try:
        return fetch_with_retry(url)
    except Exception as e:
        raise WebpageError(f"Error fetching webpage: {str(e)}")

def fetch_with_retry(url: str, max_retries: int = 3, initial_delay: float = 1.0) -> BeautifulSoup:
    """Fetch webpage with retry logic and exponential backoff.
    
    Args:
        url: URL to fetch
        max_retries: Maximum number of retries
        initial_delay: Initial delay between retries in seconds
        
    Returns:
        BeautifulSoup object of the webpage
        
    Raises:
        WebpageError: If webpage cannot be fetched after retries
    """
    headers = HTTP_HEADERS.copy()
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            # Add random user agent
            headers['User-Agent'] = get_random_user_agent()
            
            # Add random delay
            time.sleep(delay * (1 + random.random()))
            
            response = requests.get(
                url,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )
            
            # Check for anti-bot challenges
            if any(text in response.text.lower() for text in [
                'captcha',
                'access denied',
                'rate limit',
                'blocked',
                'too many requests'
            ]):
                raise WebpageError("Access blocked by anti-bot measures")
            
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise WebpageError(f"Failed to fetch webpage after {max_retries} attempts: {str(e)}")
            
            # Exponential backoff
            delay *= 2
            continue
        
        except Exception as e:
            raise WebpageError(f"Error fetching webpage: {str(e)}")

def is_valid_url(url: str) -> bool:
    """Check if URL is valid.
    
    Args:
        url: URL to check
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False 