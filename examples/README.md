# Interactive example

This directory is a minimal Sphinx project that uses the local
`sphinx_dynamic_command_builder` extension.

Build it from the repository root:

```bash
sphinx-build -M html examples examples/_build
```

Then open `examples/_build/html/index.html` in a browser. The generated page
loads the extension's CSS and JavaScript through Sphinx instead of relying on a
hand-written HTML mockup.
