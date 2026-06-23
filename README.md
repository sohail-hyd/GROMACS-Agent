# GROMACS-Agent

GROMACS-Agent is a runnable, model-agnostic, MDAgent-style multi-agent research prototype for automated GROMACS workflow generation, evaluation, correction, and selected safe execution.

It converts a natural-language molecular dynamics task into a topology-aware GROMACS workflow with required files, command sequence, post-processing steps, validation notes, an evaluator score, and correction suggestions — with a human always in the loop for final execution and interpretation.

<img width="1122" height="1402" alt="ChatGPT Image Jun 21, 2026, 01_46_58 AM (1)" src="https://github.com/user-attachments/assets/80c308aa-b0e5-4a3a-8411-1b473cf0fd5d" />

**[👉 Visit the GROMACS-Agent Website](https://sohail-hyd.github.io/GROMACS-Agent/)**


## Why GROMACS-Agent

A complete GROMACS workflow is rarely a single script. It usually spans coordinate files, topology files, MDP parameter files, TPR run-input files, trajectories, energy files, index files, and analysis outputs — all of which need to stay consistent with one another. Many GROMACS mistakes are not syntax errors at all: a command can run cleanly and still be scientifically wrong if the wrong atom group is selected, the trajectory is too short, or an earlier preprocessing step quietly invalidates a later analysis.

GROMACS-Agent treats this as a **text-to-workflow** problem rather than a text-to-code problem. A dedicated Worker agent generates the workflow; a separate Evaluator agent checks it against a GROMACS-specific rubric and proposes corrections before anything is handed back to the user.

---

## Agent architecture

GROMACS-Agent follows this modular sequence:

```
User task
  → ManagerAgent
  → PlannerAgent
  → Retriever / GSCF memory
  → GromacsWorkerAgent
  → GromacsEvaluatorAgent
  → CodeExecutorAgent
  → Final workflow, evaluation report, retrieved examples, and transcript
```

### Agent roles

| Agent | Role |
|---|---|
| **ManagerAgent** | Interprets the user task and coordinates the agent workflow |
| **PlannerAgent** | Decomposes the task into GROMACS workflow subtasks |
| **Retriever** | Retrieves related, validated examples from the GSCF dataset |
| **GromacsWorkerAgent** | Generates topology-aware GROMACS workflows |
| **GromacsEvaluatorAgent** | Scores workflows using a 10-point GROMACS-specific scientific rubric |
| **CodeExecutorAgent** | Performs execution-aware, allow-listed dry-run validation and stores outputs |

---

## Main datasets

- **GSCF** — GROMACS Scientific Code-generation Framework, for workflow-generation tasks
- **GEQS** — GROMACS Evaluation Quality Set, for evaluator and error-pattern testing

## Current benchmark status

| Metric | Value |
|---|---|
| GSCF records | 100 |
| GEQS records | 100 |
| MDAgent-style demo tasks | 5 |
| Accepted demo tasks | 5 / 5 |
| Final demo score | 10 / 10 for all five demo tasks |

---

## Demonstration tasks

The MDAgent-style demo covers:

1. O–O RDF workflow for pure water at 300 K
2. Temperature time-series extraction for pure water at 300 K
3. Density calculation for pure water at 300 K
4. MSD/diffusion workflow for pure water at 300 K
5. PBC trajectory preprocessing workflow for pure water

---

## Quick start

Clone the repository:

```bash
git clone https://github.com/sohail-hyd/GROMACS-Agent.git
cd GROMACS-Agent
```

### Run one GROMACS-Agent task

```bash
python3 agent/gromacs_agent.py --task "Generate a GROMACS workflow to calculate O-O RDF of pure water at 300 K."
```

### Run the MDAgent-style demo

```bash
python3 agent_v2/run_mdagent_style_demo.py
```

The demo summary is saved at:

```
results/mdagent_style_demo/mdagent_style_demo_summary.csv
```

### Web interface

Run:

```bash
python3 app.py
```

Then open:

```
http://127.0.0.1:7860
```

---

## Repository structure

```
agent/              Core GROMACS-Agent prototype
agent_v2/           MDAgent-style wrapper, transcripts, and demo runs
data/gscf_dataset/  GSCF workflow-generation records
data/geqs_dataset/  GEQS evaluator-quality records
paper_dataset/      Paper-ready GSCF, GEQS, and demo result files
results/            Benchmark outputs and result summaries
docs/               Architecture and manuscript-support notes
fine_tuning/        SFT / Alpaca-format export files (in progress)
utils/              Package-checking utilities
app.py              Simple web UI
```

---

## CodeExecutorAgent

CodeExecutorAgent supports safe execution of selected, validated GROMACS workflows. The executor verifies required input files, runs an allow-listed set of GROMACS analysis commands, and records execution status, expected outputs, and stdout/stderr for every check.

Supported selected execution tasks include temperature extraction, density extraction, O–O RDF calculation, MSD preprocessing, and PBC-related trajectory handling.

Validated executor tests are stored in `results/executor_tests/`.

**Example validated result:** temperature extraction status: success, average temperature 299.75 K, generated successfully.

---

## Baseline LLM vs. GROMACS-Agent benchmark

Five representative GROMACS workflow tasks were used to compare unassisted baseline LLM responses with GROMACS-Agent output, scored 0–10 by the GromacsEvaluatorAgent rubric.

| Task | Baseline LLM score | GROMACS-Agent score | Improvement |
|---|---|---|---|
| O–O RDF calculation | 5 | 10 | +5 |
| Temperature time-series extraction | 8 | 10 | +2 |
| Density calculation | 6 | 10 | +4 |
| MSD and diffusion workflow | 7 | 10 | +3 |
| PBC trajectory preprocessing | 7 | 10 | +3 |

**Average baseline LLM score:** 6.6/10
**Average GROMACS-Agent score:** 10/10
**Average evaluator-score improvement:** +3.4 points

This benchmark reports evaluator-score improvement only. It is not yet a controlled, multi-user, human time-reduction study, and should be read as pilot-scale evidence rather than a general productivity claim.

---

## Text-to-workflow generation

GROMACS-Agent extends MDAgent-style text-to-code molecular dynamics automation into a GROMACS-specific text-to-workflow design, where the unit of generation is a coordinated set of files, commands, and validation checks rather than a single script.

Core components include ManagerAgent, PlannerAgent, Retriever, GromacsWorkerAgent, GromacsEvaluatorAgent, and CodeExecutorAgent.

---

## Difference from reference MDAgent

The reference MDAgent focuses on LAMMPS script generation for material thermodynamic properties. GROMACS-Agent is built specifically around GROMACS's multi-file, multi-stage workflow structure, pairing a dedicated workflow-generation agent with a separate GROMACS-specific evaluator agent rather than relying on single-script generation.

---

## Public project status

GROMACS-Agent is a research prototype inspired by MDAgent-style molecular dynamics automation. It extends that approach to GROMACS's distributed, multi-file workflow structure.

The current repository includes a runnable Python prototype, GSCF and GEQS datasets, benchmark results, executor validation tests, and public-facing documentation.

This project is under active development. Reported timing results should be interpreted as single-user pilot evidence rather than a general productivity claim.

---

## Citation

If you use this repository, please cite the associated manuscript after publication.

## License

See [LICENSE](LICENSE) for details.
