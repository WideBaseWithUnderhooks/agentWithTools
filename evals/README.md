# Evals

This folder contains a golden-dataset evaluation harness for the LangGraph agent.

## What gets scored

- Tool-use correctness
- Factuality (deterministic checks plus optional LLM judge)
- Latency
- Failure rate

Weighted aggregate defaults to:

- tool-use 40%
- factuality 30%
- latency 20%
- failure 10%

## Dataset

Default dataset: `evals/cases/golden_v1.json`

Fast smoke dataset: `evals/cases/golden_smoke_v1.json` (3 active cases)

Each case includes behavior expectations (tool policy, expected tools, answer constraints, and latency target), not exact answer strings.

## Run

```bash
python -m evals.runner
```

Run fast local smoke evals:

```bash
python -m evals.runner --dataset evals/cases/golden_smoke_v1.json
```

Run with minimal console output:

```bash
python -m evals.runner --dataset evals/cases/golden_smoke_v1.json --quiet
```

Optional with judge model:

```bash
python -m evals.runner --judge-model llama3.2:3b
```

Fail CI if below gate:

```bash
python -m evals.runner --aggregate-gate 0.70 --fail-on-gate
```

Fail CI with metric floors:

```bash
python -m evals.runner \
	--aggregate-gate 0.70 \
	--min-tool-use 0.70 \
	--min-failure 0.90 \
	--fail-on-gate
```

Reports are written to `evals/results/` as JSON and Markdown files.
