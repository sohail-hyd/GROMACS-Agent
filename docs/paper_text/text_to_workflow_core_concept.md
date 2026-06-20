# Text-to-workflow generation and agent design

GROMACS-Agent follows an MDAgent-style text-to-workflow generation strategy. A natural-language molecular dynamics request is first interpreted by a ManagerAgent and decomposed by a PlannerAgent into required simulation and analysis steps. The Retriever identifies related examples from the GSCF dataset, and the GromacsWorkerAgent generates a topology-aware GROMACS workflow including required input files, MDP/topology/TPR dependencies, GROMACS command sequences, post-processing commands, expected outputs, and validation notes.

The GromacsEvaluatorAgent then evaluates the generated workflow using the GEQS scoring rubric, identifies syntax, sequence, parameter, analysis, and reproducibility errors, and provides correction suggestions. For selected safe tasks, the CodeExecutorAgent can execute allow-listed GROMACS commands and generate an execution report.

Therefore, the framework extends text-to-code molecular dynamics agent concepts into a GROMACS-specific text-to-workflow, evaluation, correction, and safe-execution pipeline.
