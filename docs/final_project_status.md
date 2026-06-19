# GROMACS-Agent final project status

## Repository

GitHub: https://github.com/sohail-hyd/GROMACS-Agent

## Completed components

- MDAgent-style multi-agent architecture
- ManagerAgent
- PlannerAgent
- Retriever
- GromacsWorkerAgent
- GromacsEvaluatorAgent
- CodeExecutorAgent
- Web UI
- GSCF dataset
- GEQS dataset
- Fine-tuning export files
- Fine-tuning training script
- Benchmark summary tables
- Baseline LLM comparison table
- Paper-ready Methods and Results text

## Dataset scale

- GSCF records: 100
- GEQS records: 100
- Worker SFT records: 100
- Evaluator SFT records: 100

## Agent benchmark

Five MDAgent-style GROMACS demo tasks were evaluated:

1. O-O RDF calculation
2. Temperature time-series extraction
3. Density calculation
4. MSD and diffusion workflow
5. PBC trajectory preprocessing

All five GROMACS-Agent workflows achieved evaluator scores of 10/10.

## Baseline comparison

- Baseline LLM average score: 6.6/10
- GROMACS-Agent average score: 10/10
- Average evaluator-score improvement: +3.4 points

## Safe execution evidence

CodeExecutorAgent supports selected safe execution tasks, including temperature extraction, density extraction, O-O RDF calculation, MSD with nojump preprocessing, and PBC nojump preprocessing.

## Current limitation

The current version demonstrates evaluator-score improvement and selected safe execution. It does not yet claim a controlled human time-reduction percentage.
