# 📦 CNPJ Downloader — Receita Federal CNPJ Open Data Scraper

This Python script automates the download of **all public CNPJ datasets** available on the Receita Federal website. It crawls through each dated directory and downloads **every available file** (.zip, .txt, etc.), saving them in a structured local folder.

> 🔗 Source: [Receita Federal - Dados Abertos CNPJ](https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/)

---

## 📅 Update Frequency

The Receita Federal updates these CNPJ datasets **monthly**, usually publishing a new folder (e.g., `2025-07/`) each month. This script is designed to detect and download new folders automatically on re-run.

---

## ⏱️ Download Speed & Time Estimation

This script now tracks:

- ⏱️ Download duration for each file
- 📊 Average download speed (MB/s)
- 🧮 Estimated time to download similar files

This helps monitor your progress and ensure downloads are completing efficiently.

---

## 🚀 Features

- ✅ Recursively crawls every monthly folder
- ✅ Downloads all files inside each folder
- ✅ Skips already downloaded files if size matches
- ✅ Preserves original folder structure
- ✅ Shows real-time download metrics and ETA
- ✅ Uses only `requests` and `BeautifulSoup` (no browser automation needed)

---

## ⚠️ Important Limitation

> 💡 If the script is **interrupted during a file download** (e.g., closed, killed, or lost connection), that **partial file will still be skipped** the next time you run it.

This is because the script checks if the file **exists** before downloading it — it doesn’t verify if the file is **complete or corrupted**.

To avoid this:
- Delete any incomplete files manually before restarting the script
- Or enhance the script to verify file size or checksum after download (not included by default)

---

## 📁 GitHub Repository Tip

If you're adding this project to GitHub, avoid pushing the `data/` directory (which can contain many large files). To do that, add this to your `.gitignore` file:

```
data/
```

If you want to keep the empty `data/` folder structure in the repo, create a `.gitkeep` file inside it and update `.gitignore` like this:

```
data/*
!data/.gitkeep
```

---

## 🛠️ Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:

```
requests
beautifulsoup4
```

---

## 🧩 Project Structure

```
cnpj_downloader/
├── main.py               # Main script
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
└── data/                 # Where files are saved
    ├── 2025-06/
    ├── 2025-05/
    └── ...
```

---

## 🖥️ How to Use

1. Clone this repo or copy the files.
2. Run the script:

```bash
python main.py
```

All files will be downloaded into the `data/` folder, organized by month.

---

## 💡 Customization Tips

Want to enhance the script?

- ✅ **Download only `.zip`**: add a filter in the loop
- ✅ **Unzip after download**: integrate with `zipfile` or `shutil`
- ✅ **Add logging or CSV reports**: use Python `logging` or `csv` modules
- ✅ **Verify file integrity**: check file size or hash to avoid partial downloads

---

## 📄 License

This script is open-source and free to use for personal or research purposes. Use it responsibly in accordance with Receita Federal’s data usage policies.

---

## ✨ Author

Made by [Your Name Here]  
Feel free to contribute or suggest improvements!
