# CNPJ Downloader

[![CI](https://github.com/fabricioguidine/cnpj-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/fabricioguidine/cnpj-downloader/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/fabricioguidine/cnpj-downloader)

A Python tool to automatically download CNPJ (Brazilian company registration) datasets from the Receita Federal's open data portal. It recursively crawls the monthly directories and downloads all available files, preserving the original folder structure.

> **Cross-platform:** runs on Linux, macOS, and Windows — all paths use `pathlib`, all text I/O is UTF-8, and the full test suite runs on all three operating systems in CI.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

The CNPJ Downloader automates downloading the public CNPJ datasets from
[Receita Federal - Dados Abertos CNPJ](https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/).
The Receita Federal updates these datasets **monthly**, typically publishing a new
folder (e.g. `2025-07/`) each month. The tool detects and downloads new folders on
re-run, skipping files that are already present and complete.

## Features

- **Recursive crawling** of all monthly directories.
- **Smart download** that skips files whose local size already matches the remote.
- **Resume capability**: incomplete or corrupted files are re-downloaded.
- **Progress tracking** with per-file metrics and average-speed estimation.
- **Structure preservation**: the remote folder hierarchy is mirrored locally.
- **Lightweight**: uses only `requests` and `BeautifulSoup` (no browser automation).

## Prerequisites

- Python 3.11 or higher
- pip
- Internet connection
- Sufficient disk space for the downloaded files

## Installation

The same steps work on every platform; only the virtual-environment activation
command differs.

### Linux / macOS

```bash
git clone https://github.com/fabricioguidine/cnpj-downloader.git
cd cnpj-downloader

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
git clone https://github.com/fabricioguidine/cnpj-downloader.git
cd cnpj-downloader

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Install as a package

```bash
# Editable / development install
pip install -e .

# Or a regular install
pip install .
```

## Usage

### Basic usage

```bash
python main.py
```

### Custom output directory

The output directory is configurable through the `CNPJ_OUTPUT_DIR` environment
variable (default: `data`).

Linux / macOS:

```bash
export CNPJ_OUTPUT_DIR=/path/to/your/data
python main.py
```

Windows (PowerShell):

```powershell
$env:CNPJ_OUTPUT_DIR = "D:\path\to\your\data"
python main.py
```

### Programmatic usage

```python
from src.manager import CNPJDownloaderManager

manager = CNPJDownloaderManager(
    base_url="https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/",
    output_dir="custom_data_dir",
)
manager.run()
```

## Testing

The test suite is hermetic and requires **no network access** — all HTTP calls are
mocked and downloads are written to temporary directories, so it behaves
identically on Linux, macOS, and Windows.

Install the development dependencies and run the tests:

```bash
pip install -r requirements-dev.txt
pytest -q
```

The tests cover URL/link parsing, path building, file-size/skip logic, the full
recursive crawl-and-download flow, and the `main.py` entry point invoked as a real
subprocess. Continuous integration runs them on Ubuntu, macOS, and Windows across
Python 3.11, 3.12, and 3.13.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed description of the
components, data flow, and cross-platform strategy. In short:

```
main.py  ->  CNPJDownloaderManager  ->  Crawler   (discover links)
                                    ->  Downloader (fetch files)
             Config / Utils         (settings and formatting helpers)
```

## Configuration

### Environment variables

| Variable          | Description                          | Default |
|-------------------|--------------------------------------|---------|
| `CNPJ_OUTPUT_DIR` | Output directory for downloaded files | `data`  |

### Settings file

Other settings live in `src/config.py`:

```python
BASE_URL = "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/"
OUTPUT_DIR = Path(os.getenv("CNPJ_OUTPUT_DIR", "data"))
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
├── tests/                   # Hermetic, cross-platform test suite
├── data/                    # Downloaded files (git-ignored)
│   └── .gitkeep
├── .github/workflows/ci.yml # CI matrix (OS x Python)
├── main.py                  # Entry point
├── requirements.txt         # Runtime dependencies
├── requirements-dev.txt     # Test dependencies
├── pyproject.toml           # Pytest configuration
├── setup.py                 # Package setup
└── README.md
```

## Performance

The tool tracks download duration per file, average download speed (MB/s), and an
estimated time for similarly sized files. If the script is interrupted mid-download,
the partial file is detected (by size mismatch) and re-downloaded on the next run.

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes.
4. Push the branch and open a Pull Request.

Please follow PEP 8, use type hints where applicable, and keep functions focused.
Run `pytest -q` before opening a PR.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

**Note**: This tool is for educational and research purposes. Please use it
responsibly and in accordance with Receita Federal's data usage policies.
