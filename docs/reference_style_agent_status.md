# GROMACS-Agent status compared with reference MDAgent

The reference MDAgent framework is a LAMMPS-focused fine-tuned text-to-code molecular dynamics agent. Our GROMACS-Agent follows the same high-level agent paradigm but is redesigned for GROMACS.

## Equivalent components

Reference MDAgent:
- Manager
- Planner
- Worker
- Evaluator
- LSCF dataset
- LEQS dataset
- UI
- fine-tuning files
- paper dataset

GROMACS-Agent:
- ManagerAgent
- PlannerAgent
- Retriever / GSCF memory
- GromacsWorkerAgent
- GromacsEvaluatorAgent
- CodeExecutorAgent
- GSCF dataset
- GEQS dataset
- Web UI
- fine_tuning export files
- paper_dataset folder

## Current difference

The current GROMACS-Agent is a runnable model-agnostic research prototype. It has not yet been fine-tuned into a dedicated GromacsWorkerLLM or GromacsEvaluatorLLM. Fine-tuning data are exported in Alpaca format for future SFT.

## Current evidence

A five-task MDAgent-style demo was completed. All five GROMACS tasks were accepted with final score 10/10.
