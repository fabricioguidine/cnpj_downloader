"""Smoke tests: verify the package and its public modules import cleanly."""


def test_package_imports():
    """The top-level package imports and exposes a version."""
    import src

    assert hasattr(src, "__version__")
    assert isinstance(src.__version__, str)
    assert src.__version__


def test_submodules_import():
    """Every submodule used by the CLI imports without side-effect errors."""
    from src import config, crawler, downloader, manager, utils  # noqa: F401

    assert config is not None
    assert crawler is not None
    assert downloader is not None
    assert manager is not None
    assert utils is not None


def test_main_module_importable():
    """The `main` entry-point module imports and exposes `main`."""
    import main

    assert callable(main.main)
