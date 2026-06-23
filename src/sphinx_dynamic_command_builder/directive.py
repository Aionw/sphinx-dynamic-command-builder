from __future__ import annotations

from html import escape
import re
from typing import Any

from docutils import nodes
from docutils.parsers.rst import Directive
import yaml


INPUT_KEY_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _as_str(value: Any, field: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value


def _as_bool(value: Any, field: str) -> bool:
    if value is None:
        return False
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be a boolean")
    return value


def _default_values(group: dict[str, Any], key: str, multiple: bool) -> set[str]:
    default = group.get("default")
    choices = group["choices"]

    if multiple:
        if default is None:
            return set()
        if isinstance(default, str):
            return {default} if default else set()
        if isinstance(default, list) and all(isinstance(value, str) for value in default):
            return set(default)
        raise ValueError(f"options.{key}.default must be a string or list of strings")

    default_value = _as_str(default, f"options.{key}.default")
    if not default_value:
        default_value = _as_str(choices[0].get("value"), "choice.value")
    return {default_value}


def _choice_button(
    group_key: str, group_defaults: set[str], choice: dict[str, Any], multiple: bool
) -> str:
    label = _as_str(choice.get("label"), "choice.label")
    value = _as_str(choice.get("value"), "choice.value")
    if not label:
        raise ValueError("choice.label is required")
    if not value:
        raise ValueError("choice.value is required")

    attrs = {
        "class": "sdc-button",
        "type": "button",
        "data-sdc-option": group_key,
        "data-sdc-value": value,
    }
    if multiple:
        attrs["data-sdc-multiple"] = "true"

    command_base = _as_str(choice.get("base"), "choice.base")
    env = _as_str(choice.get("env"), "choice.env")
    args = _as_str(choice.get("args"), "choice.args")
    if command_base:
        attrs["data-sdc-base"] = command_base
    if env:
        attrs["data-sdc-env"] = env
    if args:
        attrs["data-sdc-args"] = args
    if value in group_defaults:
        attrs["data-sdc-default"] = "true"

    rendered_attrs = " ".join(
        f'{escape(name)}="{escape(attr_value, quote=True)}"'
        for name, attr_value in attrs.items()
    )
    return f"<button {rendered_attrs}>{escape(label)}</button>"


def _option_group(group: dict[str, Any]) -> str:
    label = _as_str(group.get("label"), "options.label")
    key = _as_str(group.get("key"), "options.key")
    choices = group.get("choices")

    if not label:
        raise ValueError("options.label is required")
    if not key:
        raise ValueError("options.key is required")
    if not isinstance(choices, list) or not choices:
        raise ValueError(f"options.{key}.choices must be a non-empty list")

    multiple = _as_bool(group.get("multiple"), f"options.{key}.multiple")
    defaults = _default_values(group, key, multiple)
    group_attrs = {"class": "sdc-group"}
    if multiple:
        group_attrs["data-sdc-multiple"] = "true"

    rendered_group_attrs = " ".join(
        f'{escape(name)}="{escape(attr_value, quote=True)}"'
        for name, attr_value in group_attrs.items()
    )
    buttons = "\n".join(
        _choice_button(key, defaults, choice, multiple) for choice in choices
    )
    return f"""
    <div {rendered_group_attrs}>
      <div class="sdc-label">{escape(label)}</div>
      <div class="sdc-buttons">
        {buttons}
      </div>
    </div>
"""


def _input_group(input_config: dict[str, Any]) -> str:
    label = _as_str(input_config.get("label"), "inputs.label")
    key = _as_str(input_config.get("key"), "inputs.key")
    default = _as_str(input_config.get("default"), f"inputs.{key}.default")
    placeholder = _as_str(input_config.get("placeholder"), f"inputs.{key}.placeholder")

    if not label:
        raise ValueError("inputs.label is required")
    if not key:
        raise ValueError("inputs.key is required")
    if not INPUT_KEY_PATTERN.match(key):
        raise ValueError("inputs.key may only contain letters, numbers, underscores, and hyphens")

    attrs = {
        "class": "sdc-input",
        "type": "text",
        "data-sdc-input": key,
        "value": default,
    }
    if placeholder:
        attrs["placeholder"] = placeholder

    rendered_attrs = " ".join(
        f'{escape(name)}="{escape(attr_value, quote=True)}"'
        for name, attr_value in attrs.items()
    )
    return f"""
    <div class="sdc-group">
      <label class="sdc-label">{escape(label)}</label>
      <input {rendered_attrs}>
    </div>
"""


def _input_groups(config: dict[str, Any]) -> str:
    inputs = config.get("inputs", [])
    if inputs is None:
        inputs = []
    if not isinstance(inputs, list):
        raise ValueError("inputs must be a list")
    return "\n".join(_input_group(input_config) for input_config in inputs)


def _format_attrs(config: dict[str, Any]) -> dict[str, str]:
    format_config = config.get("format", {})
    if format_config is None:
        format_config = {}
    if not isinstance(format_config, dict):
        raise ValueError("format must be a YAML mapping")

    line_break = _as_str(format_config.get("line_break", "options"), "format.line_break")
    if line_break not in {"options", "none"}:
        raise ValueError("format.line_break must be one of: options, none")

    indent = _as_str(format_config.get("indent", "  "), "format.indent")

    return {
        "data-sdc-line-break": line_break,
        "data-sdc-indent": indent,
    }


class DynamicCommandDirective(Directive):
    """Render a selector-driven command generator from YAML content."""

    has_content = True

    def run(self) -> list[nodes.Node]:
        try:
            config = yaml.safe_load("\n".join(self.content)) or {}
            if not isinstance(config, dict):
                raise ValueError("dynamic-command content must be a YAML mapping")

            base = _as_str(config.get("base"), "base")
            if not base:
                raise ValueError("base is required")

            groups = config.get("options")
            if not isinstance(groups, list) or not groups:
                raise ValueError("options must be a non-empty list")

            command_label = _as_str(
                config.get("command_label", "Generated command"), "command_label"
            )
            format_attrs = _format_attrs(config)
            rendered_format_attrs = " ".join(
                f'{escape(name)}="{escape(value, quote=True)}"'
                for name, value in format_attrs.items()
            )
            rendered_inputs = _input_groups(config)
            rendered_groups = "\n".join(_option_group(group) for group in groups)
        except Exception as exc:
            error = self.state_machine.reporter.error(
                f"dynamic-command: {exc}",
                line=self.lineno,
            )
            return [error]

        html = f"""
<div class="sdc-card">
  <div data-sdc>
    <div class="sdc-controls">
      {rendered_inputs}
      {rendered_groups}
    </div>
    <div class="sdc-command">
      <div class="sdc-command-label">{escape(command_label)}</div>
      <pre><code class="language-bash" data-sdc-output data-sdc-base="{escape(base, quote=True)}" {rendered_format_attrs}></code></pre>
    </div>
  </div>
</div>
"""
        return [nodes.raw("", html, format="html")]
