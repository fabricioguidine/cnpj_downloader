"""
Utility functions for formatting and calculations.
"""
from typing import List


def format_seconds(seconds: float) -> str:
    """
    Format seconds into HH:MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string (HH:MM:SS)
    """
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02}:{mins:02}:{secs:02}"


def calculate_average_speed(speeds: List[float]) -> float:
    """
    Calculate average download speed.
    
    Args:
        speeds: List of download speeds in MB/s
        
    Returns:
        Average speed in MB/s, or 0 if list is empty
    """
    if not speeds:
        return 0.0
    return sum(speeds) / len(speeds)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


