"""
File downloader module with progress tracking and resume capability.
"""

import time
from pathlib import Path
from typing import List, Optional, Union

import requests

from src.config import HEAD_TIMEOUT, CHUNK_SIZE
from src.utils import format_seconds, calculate_average_speed


class Downloader:
    """Handles file downloads with progress tracking and resume capability."""

    def __init__(self):
        """Initialize the downloader with empty speed tracking."""
        self.download_speeds: List[float] = []

    def get_remote_file_size(self, url: str) -> Optional[int]:
        """
        Get the size of a remote file via HEAD request.

        Args:
            url: URL of the file

        Returns:
            File size in bytes, or None if unavailable
        """
        try:
            head = requests.head(url, allow_redirects=True, timeout=HEAD_TIMEOUT)
            head.raise_for_status()
            return int(head.headers.get("Content-Length", 0))
        except Exception as e:
            print(f"[ERROR] Could not get remote size: {e}")
            return None

    def should_skip_download(
        self, file_path: Union[str, Path], remote_size: Optional[int]
    ) -> bool:
        """
        Check if a file should be skipped (already downloaded and complete).

        Args:
            file_path: Local file path
            remote_size: Remote file size in bytes

        Returns:
            True if file should be skipped, False otherwise
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return False

        local_size = file_path.stat().st_size

        if remote_size and local_size == remote_size:
            print(f"[SKIP] {file_path} already downloaded (size matches)")
            return True
        else:
            print(f"[RE-DOWNLOAD] {file_path} (size mismatch or incomplete)")
            return False

    def download_file(self, url: str, save_path: Union[str, Path]) -> bool:
        """
        Download a file from URL to local path.

        Args:
            url: URL to download from
            save_path: Local path to save the file

        Returns:
            True if download succeeded, False otherwise
        """
        save_path = Path(save_path)

        # Ensure directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Check remote file size
        remote_size = self.get_remote_file_size(url)

        # Check if we should skip
        if self.should_skip_download(save_path, remote_size):
            return True

        print(f"[DOWNLOAD] {url}")
        start = time.time()

        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(save_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        f.write(chunk)

            elapsed = time.time() - start
            downloaded_mb = save_path.stat().st_size / (1024 * 1024)
            speed = downloaded_mb / elapsed if elapsed > 0 else 0
            self.download_speeds.append(speed)

            print(f"[DONE] {downloaded_mb:.2f} MB in {elapsed:.2f}s ({speed:.2f} MB/s)")

            # Show estimate for similar files
            avg_speed = calculate_average_speed(self.download_speeds)
            if remote_size and avg_speed > 0:
                est_time = format_seconds((remote_size / (1024 * 1024)) / avg_speed)
                print(
                    f"[ESTIMATE] Avg Speed: {avg_speed:.2f} MB/s - Est. for similar: {est_time}"
                )

            return True

        except Exception as e:
            print(f"[ERROR] Failed to download {url}: {e}")
            # Remove partial file on error
            if save_path.exists():
                try:
                    save_path.unlink()
                except OSError:
                    pass
            return False

    def get_average_speed(self) -> float:
        """
        Get the average download speed.

        Returns:
            Average speed in MB/s
        """
        return calculate_average_speed(self.download_speeds)
