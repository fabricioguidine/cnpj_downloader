# cnpj-downloader

Baixador de dados públicos de CNPJ da Receita Federal.

Downloads the Brazilian Federal Revenue (Receita Federal) public CNPJ company
registry — the full open dataset published monthly. Runs on Linux, macOS and
Windows; the offline logic is tested on all three via CI.

## Features

- Lists available monthly snapshots from the Receita Federal open-data portal
- Downloads selected ZIP files (Empresas, Estabelecimentos, Sócios, Simples, …)
- Resumes interrupted downloads (HTTP Range), retries on failure
- Output directory is configurable and created automatically

## Setup

Requires Python 3.11+.

**Linux / macOS**

```bash
git clone https://github.com/fabricioguidine/cnpj-downloader.git
cd cnpj-downloader
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/fabricioguidine/cnpj-downloader.git
cd cnpj-downloader
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Usage

```bash
python cnpj_downloader.py --list
python cnpj_downloader.py --latest --types empresas estabelecimentos
python cnpj_downloader.py --month 2024-05 --out ./cnpj_data
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

The suite is hermetic and offline: it injects fake HTTP sessions and drives the
real month-listing parse, type filtering, chunked download + resume, byte
formatting and CLI parsing end to end — no network required, so it runs
identically on every OS. See [ARCHITECTURE.md](ARCHITECTURE.md).
