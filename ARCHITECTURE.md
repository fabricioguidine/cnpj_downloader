# Architecture

`cnpj-downloader` is a single-file command-line tool that mirrors the Receita
Federal CNPJ open-data portal to a local directory.

## Components

```
cnpj_downloader.py   CLI + core logic:
  list_months()        parse the portal index into sorted YYYY-MM snapshots
  download_file()      streamed, resumable (HTTP Range) chunked download
  cmd_list/cmd_download command handlers
  build_parser()       argparse CLI definition
  human()              byte-size formatting
run_example.py       usage example
tests/               offline e2e suite
```

## Data flow

1. `list_months()` GETs the portal index and extracts `YYYY-MM` snapshot dirs.
2. `cmd_download()` resolves the target month, lists its `.zip` files, and
   filters them by `--types`.
3. `download_file()` streams each ZIP to `<out>/<month>/`, resuming via a
   `Range` header when a partial file already exists (a `416` means complete).

All paths are built with `pathlib.Path` and output dirs are created on demand,
so the tool behaves identically on Linux, macOS and Windows.

## Cross-platform strategy

- No OS-specific paths or shell-outs; everything goes through `pathlib`.
- Network access is isolated behind an injectable `requests.Session`, which is
  what makes the suite hermetic — tests pass a fake session and exercise the
  same code CI runs.
- `.gitattributes` normalizes line endings to LF.
- CI runs the offline suite on ubuntu/macos/windows × Python 3.11–3.13.

## Testing

`tests/test_e2e.py` injects fake sessions to drive: month-index parsing,
type filtering in `cmd_download`, chunked download to a temp dir, resume
behavior (Range header + 416), `human()` formatting, CLI argument parsing,
and a real `--help` subprocess invocation.
