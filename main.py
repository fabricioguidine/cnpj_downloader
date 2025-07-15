import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/"
OUTPUT_DIR = "data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_links(url):
    """Get all href links from a directory page, excluding query strings and parent links."""
    print(f"[SCAN] {url}")
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('?') or href.startswith('/'):
            continue
        if href in ('../', 'Parent Directory'):
            continue
        links.append(href)
    return links

def download_file(url, save_path):
    """Download a file to disk, skipping if already exists."""
    if os.path.exists(save_path):
        print(f"[SKIP] Already downloaded: {save_path}")
        return
    print(f"[DOWNLOAD] {url}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"[DONE] Saved to: {save_path}")

def crawl_and_download(current_url, relative_path=""):
    """Recursively go into directories and download all files."""
    print(f"\n[CRAWLING] {current_url}")
    links = get_links(current_url)

    for link in links:
        full_url = urljoin(current_url, link)
        if link.endswith("/"):
            print(f"[ENTER DIR] {full_url}")
            sub_path = os.path.join(relative_path, link.strip('/'))
            crawl_and_download(full_url, sub_path)
        else:
            print(f"[FOUND FILE] {link}")
            local_folder = os.path.join(OUTPUT_DIR, relative_path)
            os.makedirs(local_folder, exist_ok=True)
            file_path = os.path.join(local_folder, link)
            download_file(full_url, file_path)


if __name__ == "__main__":
    crawl_and_download(BASE_URL)
