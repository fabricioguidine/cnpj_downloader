"""
Configuration settings for the CNPJ Downloader.
"""

import os
from pathlib import Path

# Base URL for Receita Federal CNPJ open data
BASE_URL = "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/"

# Output directory for downloaded files (configurable via env var).
# Kept as a Path so callers get OS-native separators on every platform.
# Created on demand by the manager, not at import time.
OUTPUT_DIR = Path(os.getenv("CNPJ_OUTPUT_DIR", "data"))

# Request settings
REQUEST_TIMEOUT = 15
HEAD_TIMEOUT = 10
CHUNK_SIZE = 8192
