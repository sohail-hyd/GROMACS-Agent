# GROMACS-Agent manuscript outline

## Proposed title

GROMACS-Agent: An MDAgent-style multi-agent framework for automated GROMACS workflow generation, evaluation, correction, and selected execution

## Abstract draft

Large language models can assist molecular dynamics simulation setup, but direct generation of GROMACS workflows remains challenging because GROMACS requires coordinated handling of topology files, MDP settings, run-input files, trajectories, energy files, and post-processing commands. Here we present GROMACS-Agent, a model-agnostic, MDAgent-style multi-agent framework for topology-aware GROMACS workflow generation, evaluation, correction, and selected safe execution. The framework combines ManagerAgent, PlannerAgent, Retriever, GromacsWorkerAgent, GromacsEvaluatorAgent, and CodeExecutorAgent. A curated benchmark dataset was constructed with 100 GROMACS Script Construction for Fine-tuning records and 100 GROMACS Expert Quality Scoring records. The records were exported into supervised fine-tuning format for Worker and Evaluator modules. Five representative GROMACS tasks were evaluated, including O-O RDF calculation, temperature time-series extraction, density calculation, MSD/diffusion analysis, and PBC trajectory preprocessing. GROMACS-Agent achieved evaluator scores of 10/10 for all five tasks, while baseline LLM responses achieved an average score of 6.6/10. The average evaluator-score improvement was +3.4 points. CodeExecutorAgent further demonstrated selected safe execution for validated analysis tasks. The current version demonstrates improved workflow correctness and reproducibility, while controlled human time-reduction experiments remain future work.

## Main contributions

1. A GROMACS-specific MDAgent-style multi-agent architecture.
2. A 100-record GSCF workflow-generation dataset.
3. A 100-record GEQS workflow-evaluation dataset.
4. Supervised fine-tuning-ready Worker and Evaluator datasets.
5. Safe selected CodeExecutorAgent execution.
6. Baseline LLM versus GROMACS-Agent comparison on five representative tasks.

## Methods summary

GROMACS-Agent uses ManagerAgent to interpret user requests, PlannerAgent to decompose workflow steps, Retriever to select related examples from the GSCF dataset, GromacsWorkerAgent to generate topology-aware GROMACS workflows, GromacsEvaluatorAgent to score and revise outputs using a 10-point rubric, and CodeExecutorAgent to perform selected safe execution. The evaluator rubric scores syntax correctness, workflow sequence, parameter rationality, analysis correctness, and completeness/reproducibility.

## Results summary

The repository package check confirmed 12/12 required components. The paper dataset contains 100 GSCF records and 100 GEQS records. Five MDAgent-style demo tasks were accepted with final evaluator scores of 10/10. Baseline LLM responses scored 5, 8, 6, 7, and 7 across the five tasks, giving an average of 6.6/10. GROMACS-Agent achieved an average of 10/10, corresponding to an average evaluator-score improvement of +3.4 points.

## Limitation statement

The current version demonstrates evaluator-score improvement and selected safe execution. It does not yet claim a controlled human time-reduction percentage or full superiority over all external LLM baselines. Such claims require a controlled user study and broader model comparison.

## Code availability

The source code, datasets, benchmark summaries, fine-tuning files, and documentation are available at: https://github.com/sohail-hyd/GROMACS-Agent
