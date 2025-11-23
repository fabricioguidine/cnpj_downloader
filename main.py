"""
Main entry point for CNPJ Downloader.
"""
from src.manager import CNPJDownloaderManager


def main():
    """Main function to run the CNPJ downloader."""
    manager = CNPJDownloaderManager()
    manager.run()


if __name__ == "__main__":
    main()
