import time

download_speeds = []

def format_seconds(seconds):
    """Format seconds as H:M:S."""
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02}:{mins:02}:{secs:02}"

def get_avg_speed():
    """Return average speed in MB/s."""
    if not download_speeds:
        return 0
    return sum(download_speeds) / len(download_speeds)

def download_file(url, save_path):
    """Download file if not present or if size mismatch."""
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
    start_time = time.time()

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    elapsed = time.time() - start_time
    downloaded_mb = os.path.getsize(save_path) / (1024 * 1024)
    speed = downloaded_mb / elapsed
    download_speeds.append(speed)

    print(f"[DONE] Saved to: {save_path} — {downloaded_mb:.2f} MB in {elapsed:.2f}s ({speed:.2f} MB/s)")

    # Show average and estimate
    if remote_size:
        avg_speed = get_avg_speed()
        remaining_files = '?'  # Could estimate if you pass a count
        est_time = format_seconds((remote_size / (1024 * 1024)) / avg_speed)
        print(f"[ESTIMATE] Avg Speed: {avg_speed:.2f} MB/s — Estimated time for similar files: {est_time}")
