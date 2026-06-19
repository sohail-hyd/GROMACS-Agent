# MDAgent-style GROMACS-Agent prototype demonstration

The implemented GROMACS-Agent prototype was evaluated on five natural-language GROMACS workflow-generation tasks. Each task was processed through a modular agent sequence:

ManagerAgent > PlannerAgent > Retriever > GromacsWorkerAgent > GromacsEvaluatorAgent > CodeExecutorAgent

The tested tasks covered:
1. O-O radial distribution function calculation for pure water at 300 K.
2. Temperature time-series extraction for pure water at 300 K.
3. Density calculation for pure water at 300 K.
4. MSD/diffusion workflow generation for pure water at 300 K.
5. Periodic-boundary-condition trajectory preprocessing for pure water.

For each task, the agent retrieved related GSCF memory records, generated a topology-aware GROMACS workflow, evaluated the workflow using a GROMACS-specific scientific rubric, and saved the final workflow, evaluation JSON, retrieved examples, and MDAgent-style transcript.

All five demonstration tasks were accepted by the evaluator with final scores of 10/10. This confirms that GROMACS-Agent is implemented as a runnable multi-agent research prototype rather than only a conceptual framework. In the current implementation, CodeExecutorAgent performs execution-aware dry-run checking; full automatic execution is reserved for selected validated benchmark workflows.
