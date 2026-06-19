# GROMACS-Agent

GROMACS-Agent is a runnable MDAgent-style multi-agent framework for automated GROMACS workflow generation, evaluation, and correction.

The framework is designed for molecular dynamics workflow generation using GROMACS. It converts natural-language simulation or post-processing tasks into topology-aware, reproducible, and scientifically checked GROMACS workflows.

## Agent architecture

GROMACS-Agent follows this modular sequence:

User task  
→ ManagerAgent  
→ PlannerAgent  
→ Retriever / GSCF memory  
→ GromacsWorkerAgent  
→ GromacsEvaluatorAgent  
→ CodeExecutorAgent  
→ Final workflow, evaluation report, retrieved examples, and transcript

## Agent roles

- ManagerAgent: interprets the user task and coordinates the agent workflow.
- PlannerAgent: decomposes the task into GROMACS workflow subtasks.
- Retriever: retrieves related validated examples from the GSCF dataset.
- GromacsWorkerAgent: generates topology-aware GROMACS workflows.
- GromacsEvaluatorAgent: scores workflows using a 10-point GROMACS-specific scientific rubric.
- CodeExecutorAgent: performs execution-aware dry-run validation and stores outputs.

## Main datasets

- GSCF: GROMACS Scientific Code-generation Framework for workflow-generation tasks.
- GEQS: GROMACS Evaluation Quality Set for evaluator and error-pattern testing.

## Current benchmark status

- GSCF records: 100
- GEQS records: 100
- MDAgent-style demo tasks: 5
- Accepted demo tasks: 5 / 5
- Final demo score: 10 / 10 for all five demo tasks

## Demonstration tasks

The MDAgent-style demo covers:

1. O-O RDF workflow for pure water at 300 K.
2. Temperature time-series extraction for pure water at 300 K.
3. Density calculation for pure water at 300 K.
4. MSD/diffusion workflow for pure water at 300 K.
5. PBC trajectory preprocessing workflow for pure water.

## Run one GROMACS-Agent task

    python3 agent/gromacs_agent.py --task "Generate a GROMACS workflow to calculate O-O RDF of pure water at 300 K"

## Run MDAgent-style demo

    python3 agent_v2/run_mdagent_style_demo.py

The demo summary is saved at:

    results/mdagent_style_demo/mdagent_style_demo_summary.csv

## Web interface

Run:

    python3 app.py

Then open:

    http://127.0.0.1:7860

## Repository structure

    agent/                    Core GROMACS-Agent prototype
    agent_v2/                 MDAgent-style wrapper, transcripts, and demo runs
    data/gscf_dataset/        GSCF workflow-generation records
    data/geqs_dataset/        GEQS evaluator-quality records
    paper_dataset/            Paper-ready GSCF, GEQS, and demo result files
    results/                  Benchmark outputs and result summaries
    docs/                     Architecture and manuscript-support notes
    fine_tuning/              Future SFT/Alpaca-format export files
    utils/                    Package-checking utilities
    app.py                    Simple web UI

## Current implementation status

This repository is a runnable model-agnostic MDAgent-style GROMACS-Agent research prototype. The current CodeExecutorAgent performs execution-aware dry-run checking. Full automatic GROMACS execution is reserved for selected validated benchmark workflows.

## Difference from reference MDAgent

The reference MDAgent focuses on LAMMPS script generation for thermodynamic properties. GROMACS-Agent is redesigned for GROMACS-specific multi-file and multi-stage workflows, including topology consistency, MDP preparation, trajectory preprocessing, post-processing commands, atom/group selection, and validation warnings.

## Citation

If you use this repository, please cite the associated manuscript after publication.


## CodeExecutorAgent

CodeExecutorAgent supports safe execution of selected validated GROMACS workflows. The executor verifies required files, runs only allow-listed GROMACS commands, captures stdout/stderr, checks expected output files, and saves an execution report.

Supported selected execution tasks include temperature extraction, density extraction, O-O RDF calculation, MSD with nojump preprocessing, and PBC nojump preprocessing.

Validated executor tests are stored in results/executor_tests/.

Example validated result: temperature extraction status success, average temperature 299.75 K, generated output temperature_executor.xvg.

## Baseline LLM vs GROMACS-Agent benchmark

Five representative GROMACS workflow tasks were used to compare normal baseline LLM responses with GROMACS-Agent outputs.

| Task | Baseline LLM score | GROMACS-Agent score | Improvement |
|---|---:|---:|---:|
| O-O RDF calculation | 5 | 10 | +5 |
| Temperature time-series extraction | 8 | 10 | +2 |
| Density calculation | 6 | 10 | +4 |
| MSD and diffusion workflow | 7 | 10 | +3 |
| PBC trajectory preprocessing | 7 | 10 | +3 |

Average baseline LLM score: **6.6/10**

Average GROMACS-Agent score: **10/10**

Average evaluator-score improvement: **+3.4 points**

This benchmark reports evaluator-score improvement only. It is not yet a controlled human time-reduction study.
