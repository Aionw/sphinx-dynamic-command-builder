# Configuration

The `dynamic-command` directive reads a YAML mapping. The YAML describes the
base command, the generated command format, and the option groups rendered as
selectors.

## Minimal Example

````md
```{dynamic-command}
base: python -m sglang.launch_server --model-path [model_path]
options:
  - label: Topology
    key: nodes
    default: single
    choices:
      - label: Single node
        value: single
        args: --host 0.0.0.0 --port 30000
      - label: Multi node
        value: multi
        args: --host 0.0.0.0 --port 30000 --disaggregation-ib-device mlx5_1
```
````

## Top-Level Fields

- `base`: required string. The default command before selected choices add or replace anything.
- `command_label`: optional string. Label shown above the generated command. Defaults to `Generated command`.
- `format`: optional mapping. Controls how the generated command is displayed.
- `options`: required non-empty list. Each item defines one selector row.

## Format Fields

`format.line_break` controls command wrapping:

- `options`: default. Render the command as shell-continuation lines and put each `--option` group on its own line.
- `none`: render the command as a single line.

`format.indent` controls indentation for continuation lines. It defaults to two spaces.

Example:

```yaml
format:
  line_break: options
  indent: "  "
```

This renders:

```bash
python -m sglang.launch_server \
  --model-path [model_path] \
  --host 0.0.0.0 \
  --port 30000
```

Use `line_break: none` when the exact single-line command matters:

```yaml
format:
  line_break: none
```

## Option Fields

Each item in `options` defines one selector group:

- `options[].label`: required string. Visible group label.
- `options[].key`: required string. Stable key used to track the selected choice.
- `options[].default`: optional string. Default choice value. Defaults to the first choice.
- `options[].choices`: required non-empty list. Available choices for the group.

Each item in `choices` defines one selectable command fragment:

- `choices[].label`: required string. Visible button label.
- `choices[].value`: required string. Stable choice value.
- `choices[].env`: optional string. Prepended before the command when selected.
- `choices[].args`: optional string. Appended after the command when selected.
- `choices[].base`: optional string. Replaces the top-level `base` command when selected.

## Command Assembly

The generated command is assembled in this order:

1. Selected `env` fragments.
2. The active command, either top-level `base` or the selected choice `base`.
3. Selected `args` fragments in option group order.

With `format.line_break: options`, tokens beginning with `--` start a new
continuation line. Values following an option stay on the same line as that
option.
