"""End-to-end tests for the offline logic of the CNPJ downloader.

The tool fetches from the Receita Federal portal over HTTPS, which can't run
in CI, so these tests inject fake ``requests``-style sessions and exercise the
real code paths — month listing (HTML parse), file filtering, chunked download
with resume, byte formatting and argument parsing — end to end against
synthetic data. Pure-Python + pathlib, so identical on Linux, macOS, Windows.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cnpj_downloader as cd

ROOT = Path(__file__).resolve().parent.parent


class FakeResp:
    def __init__(self, text="", content=b"", status_code=200):
        self.text = text
        self._content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400 and self.status_code != 416:
            raise cd.requests.HTTPError(f"status {self.status_code}")

    def iter_content(self, chunk):
        for i in range(0, len(self._content), chunk):
            yield self._content[i:i + chunk]

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeSession:
    """Minimal stand-in for requests.Session used by the downloader."""

    def __init__(self, listing="", file_bytes=b"", status_code=200):
        self.listing = listing
        self.file_bytes = file_bytes
        self.status_code = status_code
        self.calls = []

    def get(self, url, **kw):
        self.calls.append((url, kw))
        if kw.get("stream"):
            return FakeResp(content=self.file_bytes, status_code=self.status_code)
        return FakeResp(text=self.listing)


LISTING = """
<html><body>
<a href="/2024-04/">2024-04/</a>
<a href="/2024-05/">2024-05/</a>
<a href="../">parent</a>
</body></html>
"""

MONTH_LISTING = """
<html><body>
<a href="Empresas0.zip">Empresas0.zip</a>
<a href="Estabelecimentos0.zip">Estabelecimentos0.zip</a>
<a href="Socios0.zip">Socios0.zip</a>
<a href="readme.txt">readme.txt</a>
</body></html>
"""


def test_human_formatting():
    assert cd.human(512) == "512.0B"
    assert cd.human(1536) == "1.5KB"
    assert cd.human(1 << 20) == "1.0MB"


def test_list_months_parses_and_sorts():
    s = FakeSession(listing=LISTING)
    assert cd.list_months(s) == ["2024-04", "2024-05"]


def test_build_parser_defaults_and_flags():
    p = cd.build_parser()
    ns = p.parse_args([])
    assert ns.out == str(cd.DEFAULT_OUT)
    assert ns.retries == 3
    ns2 = p.parse_args(["--list", "--month", "2024-05",
                        "--types", "empresas", "socios"])
    assert ns2.list and ns2.month == "2024-05"
    assert ns2.types == ["empresas", "socios"]


def test_download_file_writes_bytes(tmp_path):
    payload = b"x" * (3 * cd.CHUNK + 7)
    s = FakeSession(file_bytes=payload)
    dest = tmp_path / "nested" / "Empresas0.zip"
    cd.download_file(s, "http://example/Empresas0.zip", dest)
    assert dest.exists()
    assert dest.read_bytes() == payload


def test_download_file_resume_skips_when_complete(tmp_path):
    dest = tmp_path / "done.zip"
    dest.write_bytes(b"already there")
    # server replies 416 (range not satisfiable) -> nothing to append
    s = FakeSession(file_bytes=b"IGNORED", status_code=416)
    cd.download_file(s, "http://example/done.zip", dest)
    assert dest.read_bytes() == b"already there"
    # the request carried a Range header derived from the existing size
    _, kw = s.calls[-1]
    assert kw["headers"]["Range"].startswith("bytes=")


def test_cmd_download_filters_by_type(tmp_path, monkeypatch):
    captured = []

    def fake_list_months(session):
        return ["2024-05"]

    def fake_download(session, url, dest, retries=3):
        captured.append(Path(dest).name)
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        Path(dest).write_bytes(b"ok")

    monkeypatch.setattr(cd, "list_months", fake_list_months)
    monkeypatch.setattr(cd, "download_file", fake_download)

    real_get = FakeSession(listing=MONTH_LISTING).get
    monkeypatch.setattr(cd.requests, "Session",
                        lambda: FakeSession(listing=MONTH_LISTING))

    args = cd.build_parser().parse_args(
        ["--month", "2024-05", "--types", "empresas", "socios",
         "--out", str(tmp_path)])
    cd.cmd_download(args)
    assert sorted(captured) == ["Empresas0.zip", "Socios0.zip"]


def test_cli_help_runs():
    import subprocess
    res = subprocess.run(
        [sys.executable, "cnpj_downloader.py", "--help"],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    assert res.returncode == 0
    assert "CNPJ" in res.stdout
