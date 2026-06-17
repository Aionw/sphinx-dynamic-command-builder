from __future__ import annotations

from html import escape
from typing import Any

from docutils import nodes
from docutils.parsers.rst import Directive
import yaml


def _as_str(value: Any, field: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    return value


def _choice_button(group_key: str, group_default: str, choice: dict[str, Any]) -> str:
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

    command_base = _as_str(choice.get("base"), "choice.base")
    env = _as_str(choice.get("env"), "choice.env")
    args = _as_str(choice.get("args"), "choice.args")
    if command_base:
        attrs["data-sdc-base"] = command_base
    if env:
        attrs["data-sdc-env"] = env
    if args:
        attrs["data-sdc-args"] = args
    if value == group_default:
        attrs["data-sdc-default"] = "true"

    rendered_attrs = " ".join(
        f'{escape(name)}="{escape(attr_value, quote=True)}"'
        for name, attr_value in attrs.items()
    )
    return f"<button {rendered_attrs}>{escape(label)}</button>"


def _option_group(group: dict[str, Any]) -> str:
    label = _as_str(group.get("label"), "options.label")
    key = _as_str(group.get("key"), "options.key")
    default = _as_str(group.get("default"), "options.default")
    choices = group.get("choices")

    if not label:
        raise ValueError("options.label is required")
    if not key:
        raise ValueError("options.key is required")
    if not isinstance(choices, list) or not choices:
        raise ValueError(f"options.{key}.choices must be a non-empty list")

    if not default:
        default = _as_str(choices[0].get("value"), "choice.value")

    buttons = "\n".join(_choice_button(key, default, choice) for choice in choices)
    return f"""
    <div class="sdc-group">
      <div class="sdc-label">{escape(label)}</div>
      <div class="sdc-buttons">
        {buttons}
      </div>
    </div>
"""


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
      {rendered_groups}
    </div>
    <div class="sdc-command">
      <div class="sdc-command-label">{escape(command_label)}</div>
      <pre><code class="language-bash" data-sdc-output data-sdc-base="{escape(base, quote=True)}"></code></pre>
    </div>
  </div>
</div>
"""
        return [nodes.raw("", html, format="html")]

