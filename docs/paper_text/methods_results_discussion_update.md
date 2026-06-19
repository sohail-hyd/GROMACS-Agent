# Paper-ready Methods and Results update

## Updated Methods: Dataset construction

The GROMACS-Agent dataset was expanded to 100 GROMACS Script Construction for Fine-tuning records and 100 GROMACS Expert Quality Scoring records. The GSCF dataset covers topology-aware workflow generation, energy minimization, NVT/NPT equilibration, production MD, trajectory preprocessing, energy extraction, density analysis, radial distribution functions, mean-square displacement, hydrogen bonding, ion coordination, interfacial density profiles, and validation checks. The GEQS dataset contains evaluator-oriented examples of common GROMACS workflow errors, including missing topology files, incorrect command order, invalid selections, unsafe MDP settings, missing validation notes, and incorrect analysis commands.

## Updated Methods: Multi-agent workflow

GROMACS-Agent follows an MDAgent-style multi-agent workflow consisting of ManagerAgent, PlannerAgent, Retriever, GromacsWorkerAgent, GromacsEvaluatorAgent, and CodeExecutorAgent. ManagerAgent interprets the user task, PlannerAgent decomposes it into workflow steps, Retriever identifies related validated examples from GSCF memory, GromacsWorkerAgent generates a topology-aware GROMACS workflow, GromacsEvaluatorAgent scores and corrects the workflow using a 10-point rubric, and CodeExecutorAgent performs safe selected execution for validated tasks.

## Updated Results: Benchmark summary

The 100-record version passed the repository package check with 12/12 required components present. The paper dataset contains 100 GSCF records and 100 GEQS records. Five MDAgent-style demonstration tasks were evaluated: O-O RDF calculation, temperature time-series extraction, density calculation, MSD/diffusion analysis, and PBC trajectory preprocessing. All five tasks were accepted by the evaluator with final scores of 10.

## Updated Results: Fine-tuning readiness

The curated GSCF and GEQS records were exported into supervised fine-tuning format. The Worker SFT file contains 100 instruction-output records for GromacsWorkerAgent, and the Evaluator SFT file contains 100 instruction-output records for GromacsEvaluatorAgent. A supervised fine-tuning script was added to support future model-specific training.

## Updated Results: Safe execution evidence

CodeExecutorAgent supports safe execution of selected validated GROMACS workflows. It verifies required files, runs only allow-listed commands, captures stdout/stderr, checks expected output files, and stores structured execution reports. Selected validated execution tasks include temperature extraction, density extraction, O-O RDF calculation, MSD with nojump preprocessing, and PBC nojump preprocessing.

## Limitation statement

The current version should be reported as a model-agnostic, MDAgent-style GROMACS workflow generation, evaluation, correction, and selected-execution framework. It does not yet claim a measured human time-reduction percentage or full superiority over external LLM baselines. Such claims require a controlled comparison against baseline LLM outputs and manual expert workflows.
