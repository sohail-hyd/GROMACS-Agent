# GROMACS-Agent Architecture

GROMACS-Agent follows a modular MDAgent-style architecture:

User task
→ ManagerAgent
→ PlannerAgent
→ Retriever / GSCF memory
→ GromacsWorkerAgent
→ GromacsEvaluatorAgent
→ correction loop if score < 8
→ CodeExecutorAgent
→ final workflow, evaluation report, and transcript

## Agent roles

- ManagerAgent: interprets the user request and coordinates the workflow-generation process.
- PlannerAgent: decomposes the task into GROMACS workflow subtasks.
- Retriever: retrieves related validated examples from the GSCF dataset.
- GromacsWorkerAgent: generates topology-aware GROMACS workflows.
- GromacsEvaluatorAgent: scores generated workflows using the 10-point GROMACS rubric.
- CodeExecutorAgent: performs execution-aware dry-run validation and stores outputs.

## Current implementation status

The current version is a runnable MDAgent-style research prototype. CodeExecutorAgent currently performs dry-run checking. Full automatic GROMACS execution is reserved for selected validated benchmark workflows.
