"""
Web crawler module for discovering files and directories.
"""
import requests
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin

from src.config import REQUEST_TIMEOUT


class Crawler:
    """Handles crawling and link discovery from web directories."""
    
    def __init__(self, base_url: str):
        """
        Initialize the crawler.
        
        Args:
            base_url: Base URL to start crawling from
        """
        self.base_url = base_url
    
    def get_links(self, url: str) -> List[str]:
        """
        Extract all links from a directory listing page.
        
        Args:
            url: URL to crawl
            
        Returns:
            List of link names (files and directories)
        """
        print(f"[SCAN] {url}")
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Failed to access {url}: {e}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Skip navigation links
            if href.startswith('?') or href.startswith('/'):
                continue
            if href in ('../', 'Parent Directory'):
                continue
            links.append(href)
        
        return links
    
    def build_full_url(self, base_url: str, link: str) -> str:
        """
        Build a full URL from base URL and relative link.
        
        Args:
            base_url: Base URL
            link: Relative link
            
        Returns:
            Full URL
        """
        return urljoin(base_url, link)

