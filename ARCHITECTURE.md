# Architecture

`cnpj-downloader` mirrors the CNPJ open-data tree published by the Receita
Federal. It is a small, modular package under `src/` driven by a thin
`main.py` entry point.

## Components

| Module               | Responsibility                                                        |
| -------------------- | -------------------------------------------------------------------- |
| `main.py`            | Entry point; constructs the manager and calls `run()`.               |
| `src/config.py`      | Constants: `BASE_URL`, `OUTPUT_DIR` (env-overridable), timeouts, chunk size. |
| `src/crawler.py`     | `Crawler`: fetches a directory-listing page and returns the relevant `<a href>` links, filtering navigation entries. |
| `src/downloader.py`  | `Downloader`: HEAD size check, skip/resume logic, streamed download, progress and speed tracking, partial-file cleanup. |
| `src/manager.py`     | `CNPJDownloaderManager`: recursively walks directories and downloads files, preserving the remote folder hierarchy. |
| `src/utils.py`       | Pure helpers: `format_seconds`, `calculate_average_speed`, `format_file_size`. |

## Data flow

```
main()
  -> CNPJDownloaderManager(base_url, output_dir)   # output_dir.mkdir(parents=True)
  -> run()
       -> crawl_and_download(url, relative_path)    # recursive
            -> Crawler.get_links(url)               # GET listing, parse <a href>
            -> for each link:
                 build_full_url(url, link)          # urljoin
                 if link endswith "/":  recurse into subdirectory
                 else:
                   Downloader.download_file(full_url, output_dir / relative_path / link)
                     -> get_remote_file_size()      # HEAD
                     -> should_skip_download()       # size match -> skip
                     -> streamed GET -> write "wb"
                     -> record speed, print estimate
```

## Cross-platform strategy

- **Paths.** All local paths are built with `pathlib.Path`. URL path segments
  are joined with `urljoin` (URLs always use `/`), while local destinations use
  `Path` division, so the OS-specific separator is applied automatically. There
  are no hardcoded separators or absolute paths like `/tmp`.
- **No import side effects.** Directory creation happens lazily inside the
  manager (`output_dir.mkdir(parents=True, exist_ok=True)`) and the downloader
  (`save_path.parent.mkdir(...)`), not at module import time. Importing
  `src.config` no longer touches the filesystem, which keeps tests hermetic.
- **Configurable output.** The destination is `CNPJ_OUTPUT_DIR` or the `data`
  default, and can also be passed directly to the manager.
- **Encoding & binary I/O.** Downloaded files are written in binary (`"wb"`);
  text files (e.g. in `setup.py`) are opened with `encoding="utf-8"`.
- **Line endings.** `.gitattributes` normalizes text to LF and marks `.zip` as
  binary, so checkouts are identical across platforms.

## Testing strategy

The suite under `tests/` is hermetic and OS-agnostic:

- **Network is always mocked.** Both `crawler` and `downloader` do
  `import requests`, so they share one `requests` module object; the fakes route
  on the call site (listings have no `stream`, downloads pass `stream=True`).
  Unit tests use `monkeypatch`; the end-to-end CLI test runs the entry point in a
  subprocess (`sys.executable`) and injects a `sitecustomize.py` shim via
  `PYTHONPATH` that patches `requests` before the app starts, so the full
  pipeline runs with zero network access.
- **Filesystem under `tmp_path`.** Every test writes only into pytest's
  per-test temporary directory.
- **CI matrix.** `.github/workflows/ci.yml` runs `pytest -q` on
  `ubuntu-latest`, `macos-latest`, and `windows-latest` across Python 3.11,
  3.12, and 3.13 (9 jobs, `fail-fast: false`).
