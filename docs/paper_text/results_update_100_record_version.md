# Results update for 100-record GROMACS-Agent version

## Dataset construction

The GROMACS-Agent benchmark dataset was expanded to include 100 GROMACS Script Construction for Fine-tuning records and 100 GROMACS Expert Quality Scoring records. The GSCF records cover topology-aware workflow generation, equilibration, production MD, trajectory preprocessing, energy extraction, density analysis, radial distribution functions, mean-square displacement, hydrogen bonding, ion coordination, interfacial density profiles, and validation checks. The GEQS records contain evaluator-oriented examples of common GROMACS workflow errors, including missing topology files, incorrect command order, invalid selections, unsafe MDP settings, missing validation notes, and incorrect analysis commands.

## Fine-tuning readiness

The curated GSCF and GEQS records were exported into supervised fine-tuning format. The resulting Worker dataset contains 100 instruction-output examples for GromacsWorkerAgent, while the Evaluator dataset contains 100 instruction-output examples for GromacsEvaluatorAgent. These files provide a model-agnostic basis for future supervised fine-tuning of workflow generation and workflow evaluation modules.

## Multi-agent benchmark

The MDAgent-style GROMACS-Agent workflow was evaluated using benchmark summary tables generated from the current repository. The benchmark records document the dataset scale, multi-agent workflow generation behavior, retrieval of related examples, final evaluator decisions, and execution evidence from selected validated GROMACS tasks.

## Safe execution evidence

CodeExecutorAgent was upgraded from dry-run checking to safe execution of selected validated GROMACS workflows. The executor verifies required files, runs only allow-listed GROMACS commands, captures stdout/stderr, checks expected output files, and stores structured execution reports. Selected validated tasks include temperature extraction, density extraction, O-O radial distribution function calculation, mean-square displacement with nojump preprocessing, and PBC nojump preprocessing.

For the pure-water validation system, the executor successfully extracted temperature from the GROMACS energy file and produced `temperature_executor.xvg`, with an average temperature of approximately 299.75 K for the 300 K system. This confirms that the execution module can perform controlled, reproducible analysis for selected validated workflows.

## Current limitation

The current benchmark does not claim a measured human time-reduction percentage or full superiority over external LLM baselines. Such claims require a controlled comparison against baseline LLM outputs and manual expert workflows. The present version should therefore be described as a model-agnostic, MDAgent-style GROMACS workflow generation, evaluation, correction, and selected-execution framework.
