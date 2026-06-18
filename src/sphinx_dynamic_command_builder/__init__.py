from __future__ import annotations

from pathlib import Path

from sphinx.util.fileutil import copy_asset

from .directive import DynamicCommandDirective

__version__ = "0.2.2"

STATIC_DIR = Path(__file__).parent / "static"


def _copy_static_assets(app, exc):
    if exc is not None or app.builder.format != "html":
        return

    static_out = Path(app.outdir) / "_static"
    copy_asset(str(STATIC_DIR / "sphinx-dynamic-command-builder.css"), str(static_out))
    copy_asset(str(STATIC_DIR / "sphinx-dynamic-command-builder.js"), str(static_out))


def setup(app):
    app.add_directive("dynamic-command", DynamicCommandDirective)
    app.add_css_file("sphinx-dynamic-command-builder.css")
    app.add_js_file("sphinx-dynamic-command-builder.js")
    app.connect("build-finished", _copy_static_assets)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
