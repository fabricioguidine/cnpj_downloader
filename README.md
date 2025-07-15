# 📦 CNPJ Downloader — Receita Federal CNPJ Open Data Scraper

This Python script automates the download of **all public CNPJ datasets** available on the Receita Federal website. It crawls through each dated directory and downloads **every available file** (.zip, .txt, etc.), saving them in a structured local folder.

> 🔗 Source: [Receita Federal - Dados Abertos CNPJ](https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/)

---

## 🚀 Features

- ✅ Recursively crawls every monthly folder
- ✅ Downloads all files inside each folder
- ✅ Skips already downloaded files
- ✅ Preserves original folder structure
- ✅ Uses only `requests` and `BeautifulSoup` (no browser automation needed)

---

## 🛠️ Requirements

Install dependencies:

```bash
pip install -r requirements.txt
