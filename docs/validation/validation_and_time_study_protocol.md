# GROMACS-Agent validation and time-reduction study protocol

## Goal

This protocol defines how GROMACS-Agent will be validated against baseline LLM responses and manual GROMACS workflow construction.

## Validation levels

1. Dataset validation: verify GSCF and GEQS record counts and completeness.
2. Baseline comparison: compare baseline LLM workflow scores with GROMACS-Agent scores.
3. Execution validation: run selected GROMACS workflows using CodeExecutorAgent.
4. Ablation validation: compare full agent with versions without Retriever or without Evaluator.
5. Human/expert validation: ask MD/GROMACS users to score workflow correctness and usability.

## Time-reduction measurement

For each benchmark task, record:

- manual workflow construction time
- baseline LLM workflow correction time
- GROMACS-Agent workflow generation and correction time
- number of errors found
- whether the workflow executed successfully

## Time-reduction formula

Time reduction (%) = (manual time - agent time) / manual time × 100

## Tasks for timing study

1. O-O RDF calculation
2. Temperature time-series extraction
3. Density calculation
4. MSD and diffusion workflow
5. PBC trajectory preprocessing
6. Li-O and Br-O RDF for LiBr solution
7. Hydrogen-bond analysis
8. Density profile along z direction
9. Coordination number calculation
10. Equilibration validation using energy terms

## Important limitation

No time-reduction claim should be reported until real timing data are collected.
