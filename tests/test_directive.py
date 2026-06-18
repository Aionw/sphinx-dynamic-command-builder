import pytest
from docutils import nodes
from docutils.core import publish_doctree
from docutils.parsers.rst import directives

import sphinx_dynamic_command_builder as extension
from sphinx_dynamic_command_builder.directive import (
    DynamicCommandDirective,
    _choice_button,
    _format_attrs,
    _option_group,
)


directives.register_directive("dynamic-command", DynamicCommandDirective)


def render_dynamic_command(content: str) -> str:
    indented = "\n".join(f"   {line}" if line else "" for line in content.splitlines())
    doctree = publish_doctree(f".. dynamic-command::\n\n{indented}\n")
    raw_nodes = list(doctree.findall(nodes.raw))
    assert len(raw_nodes) == 1
    return raw_nodes[0].astext()


def render_dynamic_command_error(content: str) -> str:
    indented = "\n".join(f"   {line}" if line else "" for line in content.splitlines())
    doctree = publish_doctree(f".. dynamic-command::\n\n{indented}\n")
    messages = list(doctree.findall(nodes.system_message))
    assert len(messages) == 1
    return messages[0].astext()


def test_directive_registered_importable():
    assert DynamicCommandDirective.has_content is True


def test_format_attrs_defaults_to_option_line_breaks():
    assert _format_attrs({}) == {
        "data-sdc-line-break": "options",
        "data-sdc-indent": "  ",
    }


def test_format_attrs_rejects_unknown_line_break_mode():
    with pytest.raises(ValueError, match="format.line_break"):
        _format_attrs({"format": {"line_break": "always"}})


def test_directive_renders_configured_command_builder_html():
    html = render_dynamic_command(
        """
base: python -m tool --model "a b"
command_label: Run <now> & "fast"
format:
  line_break: none
  indent: "    "
options:
  - label: Mode <select>
    key: mode
    default: fast
    choices:
      - label: Fast & safe
        value: fast
        env: CUDA_VISIBLE_DEVICES=0
        args: --batch-size 4 --name "x y"
      - label: Slow "quoted"
        value: slow
        base: python -m slow
        args: --debug
""".strip()
    )

    assert 'data-sdc-base="python -m tool --model &quot;a b&quot;"' in html
    assert 'data-sdc-line-break="none"' in html
    assert 'data-sdc-indent="    "' in html
    assert "Run &lt;now&gt; &amp; &quot;fast&quot;" in html
    assert "Mode &lt;select&gt;" in html
    assert 'data-sdc-option="mode"' in html
    assert 'data-sdc-value="fast"' in html
    assert 'data-sdc-default="true"' in html
    assert 'data-sdc-env="CUDA_VISIBLE_DEVICES=0"' in html
    assert 'data-sdc-args="--batch-size 4 --name &quot;x y&quot;"' in html
    assert 'data-sdc-base="python -m slow"' in html
    assert "Slow &quot;quoted&quot;" in html


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("- item", "dynamic-command content must be a YAML mapping"),
        ("options: []", "base is required"),
        ("base: run\noptions: []", "options must be a non-empty list"),
        (
            """
base: run
options:
  - key: mode
    choices:
      - label: Fast
        value: fast
""".strip(),
            "options.label is required",
        ),
        (
            """
base: run
options:
  - label: Mode
    choices:
      - label: Fast
        value: fast
""".strip(),
            "options.key is required",
        ),
        (
            """
base: run
options:
  - label: Mode
    key: mode
    choices: []
""".strip(),
            "options.mode.choices must be a non-empty list",
        ),
        (
            """
base: run
options:
  - label: Mode
    key: mode
    choices:
      - value: fast
""".strip(),
            "choice.label is required",
        ),
        (
            """
base: run
options:
  - label: Mode
    key: mode
    choices:
      - label: Fast
""".strip(),
            "choice.value is required",
        ),
        (
            """
base: run
options:
  - label: Mode
    key: mode
    multiple: "true"
    choices:
      - label: Fast
        value: fast
""".strip(),
            "options.mode.multiple must be a boolean",
        ),
        (
            """
base: run
options:
  - label: Mode
    key: mode
    multiple: true
    default:
      - fast
      - 2
    choices:
      - label: Fast
        value: fast
""".strip(),
            "options.mode.default must be a string or list of strings",
        ),
    ],
)
def test_directive_reports_configuration_errors(content, message):
    assert message in render_dynamic_command_error(content)


def test_format_attrs_accepts_explicit_options():
    assert _format_attrs({"format": {"line_break": "none", "indent": "    "}}) == {
        "data-sdc-line-break": "none",
        "data-sdc-indent": "    ",
    }


@pytest.mark.parametrize(
    ("config", "message"),
    [
        ({"format": []}, "format must be a YAML mapping"),
        ({"format": {"indent": 2}}, "format.indent must be a string"),
    ],
)
def test_format_attrs_rejects_invalid_format_config(config, message):
    with pytest.raises(ValueError, match=message):
        _format_attrs(config)


def test_option_group_defaults_to_first_choice():
    html = _option_group(
        {
            "label": "Mode",
            "key": "mode",
            "choices": [
                {"label": "Fast", "value": "fast"},
                {"label": "Slow", "value": "slow"},
            ],
        }
    )

    assert 'data-sdc-value="fast" data-sdc-default="true"' in html
    assert 'data-sdc-value="slow" data-sdc-default="true"' not in html


def test_option_group_supports_multiple_choice_defaults():
    html = _option_group(
        {
            "label": "Features",
            "key": "features",
            "multiple": True,
            "default": ["cuda", "graphs"],
            "choices": [
                {"label": "CUDA", "value": "cuda", "args": "--cuda"},
                {"label": "FlashInfer", "value": "flashinfer", "args": "--flashinfer"},
                {"label": "CUDA graphs", "value": "graphs", "args": "--cuda-graphs"},
            ],
        }
    )

    assert '<div class="sdc-group" data-sdc-multiple="true">' in html
    assert html.count('data-sdc-multiple="true"') == 4
    assert html.count('data-sdc-default="true"') == 2
    assert 'data-sdc-value="cuda" data-sdc-multiple="true"' in html
    assert 'data-sdc-value="graphs" data-sdc-multiple="true"' in html
    assert 'data-sdc-value="flashinfer" data-sdc-multiple="true"' in html


def test_multiple_option_group_defaults_to_no_choice():
    html = _option_group(
        {
            "label": "Features",
            "key": "features",
            "multiple": True,
            "choices": [
                {"label": "CUDA", "value": "cuda"},
                {"label": "FlashInfer", "value": "flashinfer"},
            ],
        }
    )

    assert 'data-sdc-multiple="true"' in html
    assert 'data-sdc-default="true"' not in html


def test_choice_button_escapes_attribute_and_label_values():
    html = _choice_button(
        "mode",
        {"fast"},
        {
            "label": "Fast <safe>",
            "value": "fast",
            "env": 'A="1&2"',
            "args": '--name "x<y>"',
            "base": "run <tool>",
        },
        False,
    )

    assert "Fast &lt;safe&gt;" in html
    assert 'data-sdc-env="A=&quot;1&amp;2&quot;"' in html
    assert 'data-sdc-args="--name &quot;x&lt;y&gt;&quot;"' in html
    assert 'data-sdc-base="run &lt;tool&gt;"' in html


def test_setup_registers_directive_assets_and_build_hook():
    class FakeApp:
        def __init__(self):
            self.directives = []
            self.css_files = []
            self.js_files = []
            self.events = []

        def add_directive(self, name, directive):
            self.directives.append((name, directive))

        def add_css_file(self, filename):
            self.css_files.append(filename)

        def add_js_file(self, filename):
            self.js_files.append(filename)

        def connect(self, event, callback):
            self.events.append((event, callback))

    app = FakeApp()

    metadata = extension.setup(app)

    assert app.directives == [("dynamic-command", DynamicCommandDirective)]
    assert app.css_files == ["sphinx-dynamic-command-builder.css"]
    assert app.js_files == ["sphinx-dynamic-command-builder.js"]
    assert app.events == [("build-finished", extension._copy_static_assets)]
    assert metadata == {
        "version": extension.__version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def test_copy_static_assets_copies_files_for_html_build(tmp_path, monkeypatch):
    copied = []

    def fake_copy_asset(src, dst):
        copied.append((src, dst))

    class FakeBuilder:
        format = "html"

    class FakeApp:
        builder = FakeBuilder()
        outdir = tmp_path

    monkeypatch.setattr(extension, "copy_asset", fake_copy_asset)

    extension._copy_static_assets(FakeApp(), None)

    assert copied == [
        (
            str(extension.STATIC_DIR / "sphinx-dynamic-command-builder.css"),
            str(tmp_path / "_static"),
        ),
        (
            str(extension.STATIC_DIR / "sphinx-dynamic-command-builder.js"),
            str(tmp_path / "_static"),
        ),
    ]


@pytest.mark.parametrize(("builder_format", "exc"), [("latex", None), ("html", Exception())])
def test_copy_static_assets_skips_non_html_or_failed_build(
    tmp_path, monkeypatch, builder_format, exc
):
    copied = []

    class FakeBuilder:
        format = builder_format

    class FakeApp:
        builder = FakeBuilder()
        outdir = tmp_path

    monkeypatch.setattr(extension, "copy_asset", lambda src, dst: copied.append((src, dst)))

    extension._copy_static_assets(FakeApp(), exc)

    assert copied == []
