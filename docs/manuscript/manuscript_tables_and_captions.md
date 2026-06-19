# Manuscript tables and figure captions

## Table 1. GROMACS-Agent components and functions

| Component | Function | Output |
|---|---|---|
| ManagerAgent | Interprets user request and coordinates the workflow | Parsed task objective |
| PlannerAgent | Decomposes the task into GROMACS workflow steps | Structured workflow plan |
| Retriever | Retrieves related examples from GSCF memory | Relevant validated examples |
| GromacsWorkerAgent | Generates topology-aware GROMACS workflow | Workflow commands and validation notes |
| GromacsEvaluatorAgent | Scores and revises workflow using GEQS rubric | Score, errors, correction suggestions |
| CodeExecutorAgent | Performs selected safe execution | Execution report and output check |

## Table 2. Dataset and benchmark summary

| Item | Count / Result |
|---|---:|
| GSCF workflow records | 100 |
| GEQS evaluator records | 100 |
| Worker SFT records | 100 |
| Evaluator SFT records | 100 |
| MDAgent-style demo tasks | 5 |
| Accepted GROMACS-Agent workflows | 5/5 |
| Average baseline LLM score | 6.6/10 |
| Average GROMACS-Agent score | 10/10 |
| Average evaluator-score improvement | +3.4 points |

## Table 3. Baseline LLM versus GROMACS-Agent comparison

| Task | Baseline LLM score | GROMACS-Agent score | Improvement | Main baseline error |
|---|---:|---:|---:|---|
| O-O RDF calculation | 5 | 10 | +5 | Topology-coordinate mismatch and inconsistent water-box preparation |
| Temperature time-series extraction | 8 | 10 | +2 | Weak validation and assumed time offsets |
| Density calculation | 6 | 10 | +4 | Incorrect water molecule counting and inconsistent topology preparation |
| MSD and diffusion workflow | 7 | 10 | +3 | Mixed PBC handling and unclear MSD fitting workflow |
| PBC trajectory preprocessing | 7 | 10 | +3 | Hard-coded index groups and unclear final trajectory purpose |

## Figure 1 caption

Figure 1. Overall architecture of GROMACS-Agent. The framework follows an MDAgent-style workflow in which ManagerAgent interprets the user task, PlannerAgent decomposes the workflow, Retriever identifies related GSCF examples, GromacsWorkerAgent generates a topology-aware workflow, GromacsEvaluatorAgent scores and corrects the workflow, and CodeExecutorAgent performs selected safe execution.

## Figure 2 caption

Figure 2. GROMACS-Agent dataset construction and benchmark pipeline. The GSCF dataset supports workflow generation, while the GEQS dataset supports workflow scoring and correction. Both datasets are exported into supervised fine-tuning format for future Worker and Evaluator model training.

## Figure 3 caption

Figure 3. Representative GROMACS-Agent benchmark results for five workflow tasks: O-O RDF calculation, temperature time-series extraction, density calculation, MSD/diffusion analysis, and PBC trajectory preprocessing. All five generated workflows were accepted with final evaluator scores of 10/10.

## Figure 4 caption

Figure 4. Baseline LLM versus GROMACS-Agent comparison. Baseline LLM responses achieved an average score of 6.6/10, while GROMACS-Agent achieved 10/10 across the same five tasks, corresponding to an average evaluator-score improvement of +3.4 points.
