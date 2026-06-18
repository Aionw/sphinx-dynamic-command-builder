# sphinx-dynamic-command-builder

```{toctree}
:maxdepth: 2

configuration
```

```{dynamic-command}
base: python -m sglang.launch_server --model-path [model_path]
format:
  line_break: options
  indent: "  "
options:
  - label: Integration path
    key: path
    default: hicache
    choices:
      - label: HiCache L3
        value: hicache
        env: MOONCAKE_MASTER=127.0.0.1:50051
        args: --enable-hierarchical-cache --hicache-storage-backend mooncake
      - label: PD disaggregation
        value: pd
        args: --disaggregation-mode prefill
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
  - label: Parallelism
    key: tp
    default: "4"
    choices:
      - label: TP 1
        value: "1"
        args: --tp-size 1
      - label: TP 4
        value: "4"
        args: --tp-size 4
      - label: TP 8
        value: "8"
        args: --tp-size 8
  - label: Runtime features
    key: features
    multiple: true
    default:
      - cuda-graphs
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
