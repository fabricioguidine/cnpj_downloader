# Architecture

This document describes the components of CNPJ Downloader, how data flows
through them, and the strategy that keeps the tool portable across Linux,
macOS, and Windows.

## Overview

CNPJ Downloader mirrors a remote Apache-style directory listing
(Receita Federal's open CNPJ data) onto the local filesystem. It is a small,
single-purpose CLI built on `requests` (HTTP) and `BeautifulSoup` (HTML parsing).

## Components

| Component | File | Responsibility |
|-----------|------|----------------|
| Entry point | `main.py` | Constructs the manager with defaults and starts the run. |
| Manager | `src/manager.py` | Orchestrates the recursive crawl-and-download, mapping remote paths to local directories. |
| Crawler | `src/crawler.py` | Fetches a directory page and extracts the file/sub-directory links, filtering navigation links. |
| Downloader | `src/downloader.py` | Performs HEAD/GET requests, skips already-complete files, streams downloads to disk, tracks speed, and cleans up partial files on error. |
| Config | `src/config.py` | Centralizes the base URL, the (env-configurable) output directory as a `Path`, timeouts, and chunk size. |
| Utils | `src/utils.py` | Pure formatting/calculation helpers (time, average speed, human-readable sizes). |

## Data Flow

```
main.main()
    |
    v
CNPJDownloaderManager.run()
    |
    v
CNPJDownloaderManager.crawl_and_download(url, relative_path)
    |
    +-- Crawler.get_links(url) ----------> requests.get -> BeautifulSoup -> [links]
    |
    +-- for each link:
            +-- build_full_url(url, link)            (urllib.parse.urljoin)
            +-- if link ends with "/":  recurse into the sub-directory
            +-- else: Downloader.download_file(full_url, output_dir / relative_path / link)
                          |
                          +-- get_remote_file_size()  (HEAD, Content-Length)
                          +-- should_skip_download()   (compare local vs remote size)
                          +-- stream GET -> write chunks -> record speed
```

The remote URL hierarchy is reproduced as a local directory tree rooted at
`OUTPUT_DIR`. A `relative_path` string (joined with `/`, matching the URL
structure) is combined with the output directory using `pathlib`, which yields
OS-native separators on each platform.

## Cross-Platform Strategy

- **Paths via `pathlib`.** Filesystem paths are `Path` objects. The output
  directory is a `Path` (`src/config.py`), and directory creation uses
  `Path.mkdir(parents=True, exist_ok=True)`. This avoids hardcoded separators
  and works identically on POSIX and Windows. URL joining stays in
  `urllib.parse.urljoin`, which always uses `/`.

- **Configurable, non-cwd-bound output.** The download location is driven by the
  `CNPJ_OUTPUT_DIR` environment variable (default `data`). No path is hardcoded
  to `/tmp`, `C:\`, or a fixed working directory, and the output directory is
  created on demand by the manager rather than as an import-time side effect.

- **UTF-8 text I/O.** Text files (e.g. `README.md`, `requirements.txt` in
  `setup.py`) are opened with `encoding="utf-8"` so behaviour does not depend on
  the platform's default code page. Downloads are binary (`"wb"`), which is
  encoding-agnostic.

- **No shell invocation.** The tool performs all work in-process through
  `requests` and the standard library; it never shells out via `os.system`, so
  there are no shell-quoting or platform-shell differences.

- **Hermetic, OS-agnostic tests.** The test suite mocks all network access and
  writes only into pytest's `tmp_path`. The CLI is exercised through a real
  subprocess using `sys.executable`. The CI matrix runs the suite on
  `ubuntu-latest`, `macos-latest`, and `windows-latest` across Python 3.11-3.13.

## Error Handling

- Crawl failures return an empty link list, so one unreachable directory does not
  abort the whole run.
- Download failures are caught; any partially written file is removed
  (`Path.unlink`) so the next run re-downloads it cleanly.
- Size mismatches between a local file and the remote `Content-Length` trigger a
  re-download, providing a simple resume mechanism.
