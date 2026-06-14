"""End-to-end CLI test: runs the entry point as a subprocess with network mocked.

A `sitecustomize.py` shim is placed on PYTHONPATH so it is imported
automatically by the child interpreter before the app runs. The shim patches
`requests` (crawler and downloader share one `requests` module object) to serve
synthetic listings and file bytes, so the whole pipeline (entry point ->
manager -> crawler -> downloader -> filesystem) runs end to end with zero
network access.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_SHIM = r"""
import src.crawler as crawler
import src.downloader as downloader

LISTINGS = {
    "https://fake.test/cnpj/":
        '<a href="2025-05/">2025-05/</a><a href="Empresas0.zip">Empresas0.zip</a>',
    "https://fake.test/cnpj/2025-05/":
        '<a href="Estabelecimentos0.zip">Estabelecimentos0.zip</a>',
}
FILE_BODY = b"synthetic-zip-bytes"


class _Listing:
    def __init__(self, text):
        self.text = text
    def raise_for_status(self):
        return None


class _Head:
    headers = {"Content-Length": "0"}
    def raise_for_status(self):
        return None


class _Get:
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        return False
    def raise_for_status(self):
        return None
    def iter_content(self, chunk_size=8192):
        yield FILE_BODY


def _fake_get(url, timeout=None, stream=False, **kwargs):
    if stream:
        return _Get()
    return _Listing(LISTINGS[url])


def _fake_head(url, allow_redirects=True, timeout=None):
    return _Head()


# Both modules reference the same requests module; patch via either handle.
crawler.requests.get = _fake_get
downloader.requests.get = _fake_get
downloader.requests.head = _fake_head
"""

_RUNNER = (
    "import os\n"
    "from src.manager import CNPJDownloaderManager\n"
    "CNPJDownloaderManager(\n"
    "    base_url='https://fake.test/cnpj/',\n"
    "    output_dir=os.environ['CNPJ_OUTPUT_DIR'],\n"
    ").run()\n"
)


def test_cli_end_to_end(tmp_path):
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir()
    (shim_dir / "sitecustomize.py").write_text(_SHIM, encoding="utf-8")

    runner = tmp_path / "run_app.py"
    runner.write_text(_RUNNER, encoding="utf-8")

    out_dir = tmp_path / "out"

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(shim_dir), str(ROOT)])
    env["CNPJ_OUTPUT_DIR"] = str(out_dir)
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, str(runner)],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
        env=env,
    )

    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    assert "[START] Starting CNPJ downloader" in result.stdout
    assert "[DONE]" in result.stdout

    top_file = out_dir / "Empresas0.zip"
    nested_file = out_dir / "2025-05" / "Estabelecimentos0.zip"
    assert top_file.is_file()
    assert nested_file.is_file()
    assert top_file.read_bytes() == b"synthetic-zip-bytes"
    assert nested_file.read_bytes() == b"synthetic-zip-bytes"


def test_main_entrypoint_importable():
    """main.main must be importable and wired to the manager."""
    import importlib

    main_mod = importlib.import_module("main")
    assert callable(main_mod.main)
