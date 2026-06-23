# Configuration

The `dynamic-command` directive reads a YAML mapping. The YAML describes the
base command, user inputs, the generated command format, and the option groups
rendered as selectors.

## Minimal Example

````md
```{dynamic-command}
base: python -m sglang.launch_server --model-path {model_path}
inputs:
  - label: Model path
    key: model_path
    default: meta-llama/Llama-3.1-8B-Instruct
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
- `inputs`: optional list. Each item defines one text input row. Use `{key}` placeholders in `base`, `choices[].env`, `choices[].args`, or `choices[].base` to insert the current value.
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
  --model-path meta-llama/Llama-3.1-8B-Instruct \
  --host 0.0.0.0 \
  --port 30000
```

Use `line_break: none` when the exact single-line command matters:

```yaml
format:
  line_break: none
```

## Input Fields

Each item in `inputs` defines one text input:

- `inputs[].label`: required string. Visible input label.
- `inputs[].key`: required string. Placeholder key used as `{key}` in command fragments.
- `inputs[].default`: optional string. Initial input value.
- `inputs[].placeholder`: optional string. Placeholder text shown when the input is empty.

Input values are shell-quoted before they are inserted into command fragments:

```yaml
base: rg {query} .
inputs:
  - label: Search text
    key: query
    default: dynamic command
```

This renders `rg 'dynamic command' .` by default.

## Option Fields

Each item in `options` defines one selector group:

- `options[].label`: required string. Visible group label.
- `options[].key`: required string. Stable key used to track the selected choice.
- `options[].multiple`: optional boolean. Use `true` when the group should allow more than one selected choice. Defaults to `false`.
- `options[].default`: optional string, or list of strings when `multiple: true`. Single-select groups default to the first choice. Multi-select groups default to no selected choices.
- `options[].choices`: required non-empty list. Available choices for the group.

Each item in `choices` defines one selectable command fragment:

- `choices[].label`: required string. Visible button label.
- `choices[].value`: required string. Stable choice value.
- `choices[].env`: optional string. Prepended before the command when selected.
- `choices[].args`: optional string. Appended after the command when selected.
- `choices[].base`: optional string. Replaces the top-level `base` command when selected.

Multi-select groups toggle each choice independently:

```yaml
options:
  - label: Features
    key: features
    multiple: true
    default:
      - cuda-graphs
      - metrics
    choices:
      - label: CUDA graphs
        value: cuda-graphs
        args: --enable-cuda-graph
      - label: Metrics
        value: metrics
        args: --show-time-cost
      - label: Torch compile
        value: compile
        args: --enable-torch-compile
```

Omit `default` in a multi-select group when no choices should be selected
initially. Use a string when only one default choice is needed, or a list of
strings when several choices should start selected.

## Command Assembly

The generated command is assembled in this order:

1. Selected `env` fragments.
2. The active command, either top-level `base` or the selected choice `base`.
3. Selected `args` fragments in option group order. Multi-select groups append
   selected choices in the order they appear in YAML.

With `format.line_break: options`, tokens beginning with `--` start a new
continuation line. Values following an option stay on the same line as that
option. Selected `env` fragments are rendered as separate continuation lines
before the active command.
