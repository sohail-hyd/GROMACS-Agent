# GROMACS-Agent benchmark and evaluation summary

## Dataset scale

- GSCF curated workflow records: 100
- GEQS curated evaluator records: 100
- Worker SFT Alpaca records: 100
- Evaluator SFT Alpaca records: 100

## Agent benchmark summary

The current benchmark uses the MDAgent-style multi-agent demo results stored in `results/mdagent_style_demo/`.
These results report generation, retrieval, evaluation, correction-loop behavior, and final evaluator scores.

## Executor evidence

- density: success | outputs: density_executor.xvg
- rdf_oo: success | outputs: rdf_OW_OW_executor.xvg
- temperature: success | outputs: temperature_executor.xvg

## Important limitation

This benchmark summary does not yet claim a measured human time-reduction percentage or superiority over external LLM baselines. Those claims require a separate controlled baseline/user study.

## Generated CSV files

- `results/benchmark/dataset_scale_summary.csv`
- `results/benchmark/gromacs_agent_benchmark_summary.csv`
- `results/benchmark/executor_evidence_summary.csv`
