# Baseline testing protocol

## Goal

This protocol compares normal baseline LLM output with GROMACS-Agent output for five representative GROMACS workflow tasks.

## Procedure

1. Give each prompt in `benchmark_baselines/baseline_llm_prompts.md` to a baseline LLM.
2. Save the raw baseline response for each task.
3. Evaluate each baseline response using the same GEQS 10-point rubric.
4. Record baseline scores in `results/benchmark/baseline_score_template.csv`.
5. Compare baseline scores with GROMACS-Agent scores.

## Current status

GROMACS-Agent scores are already available for the five demo tasks. Baseline LLM scores are pending and must be measured before making superiority or time-reduction claims.
