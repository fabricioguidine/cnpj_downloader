# CNPJ Downloader

[![CI](https://github.com/fabricioguidine/cnpj-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/fabricioguidine/cnpj-downloader/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/fabricioguidine/cnpj-downloader/branch/main/graph/badge.svg)](https://codecov.io/gh/fabricioguidine/cnpj-downloader)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/fabricioguidine/cnpj-downloader)

A Python tool to automatically download CNPJ (Brazilian company registration) datasets from the Receita Federal's open data portal. This tool recursively crawls through monthly directories and downloads all available files, preserving the original folder structure.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Overview

The CNPJ Downloader automates the process of downloading public CNPJ datasets from the [Receita Federal - Dados Abertos CNPJ](https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/) website. The Receita Federal updates these datasets monthly, and this tool is designed to detect and download new folders automatically.

### Data Source

> 🔗 **Source**: [Receita Federal - Dados Abertos CNPJ](https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/)

### Update Frequency

The Receita Federal updates CNPJ datasets **monthly**, typically publishing a new folder (e.g., `2025-07/`) each month. This script automatically detects and downloads new folders on re-run.

## Features

- ✅ **Recursive Crawling**: Automatically crawls through all monthly directories
- ✅ **Smart Download**: Skips already downloaded files if size matches
- ✅ **Resume Capability**: Re-downloads incomplete or corrupted files
- ✅ **Progress Tracking**: Real-time download metrics and speed estimation
- ✅ **Structure Preservation**: Maintains original folder hierarchy
- ✅ **Error Handling**: Robust error handling with automatic retry logic
- ✅ **Lightweight**: Uses only `requests` and `BeautifulSoup` (no browser automation)

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Internet connection
- Sufficient disk space for downloaded files

## Installation

### Option 1: Using pip (Recommended)

```bash
# Clone the repository
git clone https://github.com/fabricioguidine/cnpj-downloader.git
cd cnpj-downloader

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Install as a package

```bash
# Install in development mode
pip install -e .

# Or install directly
pip install .
```

## Usage

### Basic Usage

Run the downloader with default settings:

```bash
python main.py
```

### Custom Configuration

You can customize the output directory using environment variables:

```bash
# Set custom output directory
export CNPJ_OUTPUT_DIR=/path/to/your/data
python main.py
```

### Programmatic Usage

```python
from src.manager import CNPJDownloaderManager

# Create manager with custom settings
manager = CNPJDownloaderManager(
    base_url="https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/",
    output_dir="custom_data_dir"
)

# Start downloading
manager.run()
```

## Architecture

The project follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐
│   main.py       │  Entry point
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Manager       │  Orchestrates crawling and downloading
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────┐
│ Crawler │ │Downloader│  Core functionality
└─────────┘ └──────────┘
    │         │
    └────┬────┘
         ▼
┌─────────────────┐
│  Config & Utils │  Configuration and utilities
└─────────────────┘
```

### Components

- **Manager**: Orchestrates the overall download process
- **Crawler**: Handles web crawling and link discovery
- **Downloader**: Manages file downloads with progress tracking
- **Config**: Centralized configuration management
- **Utils**: Utility functions for formatting and calculations

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CNPJ_OUTPUT_DIR` | Output directory for downloaded files | `data` |

### Configuration File

You can modify settings in `src/config.py`:

```python
BASE_URL = "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/"
OUTPUT_DIR = "data"
REQUEST_TIMEOUT = 15
HEAD_TIMEOUT = 10
CHUNK_SIZE = 8192
```

## Project Structure

```
cnpj-downloader/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration settings
│   ├── crawler.py           # Web crawling logic
│   ├── downloader.py        # File download logic
│   ├── manager.py           # Main orchestration
│   └── utils.py             # Utility functions
├── data/                    # Downloaded files (git-ignored)
│   ├── .gitkeep
│   ├── 2025-06/
│   ├── 2025-05/
│   └── ...
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Performance

### Download Speed Tracking

The tool tracks:
- ⏱️ Download duration for each file
- 📊 Average download speed (MB/s)
- 🧮 Estimated time to download similar files

This helps monitor progress and ensure downloads complete efficiently.

### Limitations

> ⚠️ **Important**: If the script is interrupted during a file download (e.g., closed, killed, or lost connection), that partial file will be re-downloaded on the next run. The script checks file size to detect incomplete downloads.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and setup
git clone https://github.com/fabricioguidine/cnpj-downloader.git
cd cnpj-downloader
pip install -r requirements.txt

# Make your changes and test
python main.py
```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where applicable
- Add docstrings to functions and classes
- Keep functions focused and modular

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

### Issues

If you encounter any issues or have questions:

1. Check existing [Issues](https://github.com/fabricioguidine/cnpj-downloader/issues)
2. Create a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS

### Questions

For questions or discussions, please open a [Discussion](https://github.com/fabricioguidine/cnpj-downloader/discussions).

## Acknowledgments

- [Receita Federal](https://www.gov.br/receitafederal) for providing open CNPJ data
- Contributors and users of this project

---

**Note**: This tool is for educational and research purposes. Please use it responsibly and in accordance with Receita Federal's data usage policies.
