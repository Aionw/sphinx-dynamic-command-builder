from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

project = "sphinx-dynamic-command-builder example"
extensions = [
    "sphinx_dynamic_command_builder",
]

html_title = project
html_theme = "basic"
html_static_path = ["_static"]
html_css_files = ["example.css"]
html_sidebars = {"**": []}
html_show_sourcelink = False
html_use_index = False
exclude_patterns = ["_build"]
