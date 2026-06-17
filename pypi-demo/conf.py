project = "PyPI demo for sphinx-dynamic-command-builder"

extensions = [
    "sphinx_dynamic_command_builder",
]

html_title = project
html_theme = "basic"
html_sidebars = {"**": []}
html_show_sourcelink = False
exclude_patterns = [".venv", "_build", "_build-*"]
