"""
Configuration settings for the CNPJ Downloader.
"""
import os
from pathlib import Path

# Base URL for Receita Federal CNPJ open data
BASE_URL = "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/"

# Output directory for downloaded files
OUTPUT_DIR = os.getenv("CNPJ_OUTPUT_DIR", "data")

# Request settings
REQUEST_TIMEOUT = 15
HEAD_TIMEOUT = 10
CHUNK_SIZE = 8192

# Ensure output directory exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


