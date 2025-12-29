"""
Main manager class that orchestrates crawling and downloading.
"""
import os
from pathlib import Path
from typing import Optional

from src.config import BASE_URL, OUTPUT_DIR
from src.crawler import Crawler
from src.downloader import Downloader


class CNPJDownloaderManager:
    """Main manager for CNPJ dataset downloading."""
    
    def __init__(self, base_url: str = BASE_URL, output_dir: str = OUTPUT_DIR):
        """
        Initialize the download manager.
        
        Args:
            base_url: Base URL to start crawling from
            output_dir: Directory to save downloaded files
        """
        self.base_url = base_url
        self.output_dir = output_dir
        self.crawler = Crawler(base_url)
        self.downloader = Downloader()
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def crawl_and_download(self, current_url: Optional[str] = None, relative_path: str = "") -> None:
        """
        Recursively crawl directories and download all files.
        
        Args:
            current_url: Current URL to crawl (defaults to base_url)
            relative_path: Relative path for organizing downloaded files
        """
        if current_url is None:
            current_url = self.base_url
        
        print(f"\n[CRAWLING] {current_url}")
        links = self.crawler.get_links(current_url)
        
        for link in links:
            full_url = self.crawler.build_full_url(current_url, link)
            
            if link.endswith("/"):
                # It's a directory - recurse
                print(f"[ENTER DIR] {full_url}")
                sub_path = os.path.join(relative_path, link.strip('/'))
                self.crawl_and_download(full_url, sub_path)
            else:
                # It's a file - download it
                print(f"[FOUND FILE] {link}")
                local_folder = os.path.join(self.output_dir, relative_path)
                Path(local_folder).mkdir(parents=True, exist_ok=True)
                file_path = os.path.join(local_folder, link)
                self.downloader.download_file(full_url, file_path)
    
    def run(self) -> None:
        """Start the download process."""
        print(f"[START] Starting CNPJ downloader")
        print(f"[CONFIG] Base URL: {self.base_url}")
        print(f"[CONFIG] Output Directory: {self.output_dir}")
        self.crawl_and_download()


