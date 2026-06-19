# GEQS 10-point baseline scoring rubric

Use the same 10-point rubric for both baseline LLM workflows and GROMACS-Agent workflows.

## Score categories

1. Syntax correctness: 0-2 points
2. Workflow sequence: 0-2 points
3. Parameter rationality: 0-2 points
4. Analysis correctness: 0-2 points
5. Completeness and reproducibility: 0-2 points

## Common error checks

- Missing topology file
- Wrong GROMACS command order
- Invalid GROMACS option
- Unsafe or weak MDP settings
- Missing analysis command
- Missing validation note
- Use of short trajectory without warning
- Incorrect interactive selection handling
- Missing expected output files

## Decision rule

Score 8-10: accept
Score below 8: revise
