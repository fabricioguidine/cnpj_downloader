import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/"
OUTPUT_DIR = "data"
download_speeds = []

os.makedirs(OUTPUT_DIR, exist_ok=True)

def format_seconds(seconds):
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02}:{mins:02}:{secs:02}"

def get_avg_speed():
    if not download_speeds:
        return 0
    return sum(download_speeds) / len(download_speeds)

def get_links(url):
    print(f"[SCAN] {url}")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to access {url}: {e}")
        return []

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
    try:
        head = requests.head(url, allow_redirects=True, timeout=10)
        head.raise_for_status()
        remote_size = int(head.headers.get("Content-Length", 0))
    except Exception as e:
        print(f"[ERROR] Could not get remote size: {e}")
        remote_size = None

    if os.path.exists(save_path):
        local_size = os.path.getsize(save_path)
        if remote_size and local_size == remote_size:
            print(f"[SKIP] {save_path} already downloaded (size matches)")
            return
        else:
            print(f"[RE-DOWNLOAD] {save_path} (size mismatch)")

    print(f"[DOWNLOAD] {url}")
    start = time.time()
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    elapsed = time.time() - start
    downloaded_mb = os.path.getsize(save_path) / (1024 * 1024)
    speed = downloaded_mb / elapsed
    download_speeds.append(speed)

    print(f"[DONE] {downloaded_mb:.2f} MB in {elapsed:.2f}s ({speed:.2f} MB/s)")
    if remote_size:
        est_time = format_seconds((remote_size / (1024 * 1024)) / get_avg_speed())
        print(f"[ESTIMATE] Avg Speed: {get_avg_speed():.2f} MB/s — Est. for similar: {est_time}")

def crawl_and_download(current_url, relative_path=""):
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
