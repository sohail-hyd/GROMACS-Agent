# Baseline LLM prompts for comparison

Use these prompts with a normal baseline LLM without giving it access to GSCF, GEQS, Retriever, GromacsEvaluatorAgent, or CodeExecutorAgent.

## BASE_001: O-O RDF calculation

Generate a complete and reproducible GROMACS workflow to calculate the O-O radial distribution function of pure water at 300 K. Include required input files, topology preparation, command sequence, expected output files, common possible errors, and validation notes.

## BASE_002: Temperature time series

Generate a complete GROMACS post-processing workflow to extract and validate the temperature time series of pure water at 300 K from an energy file. Include required input files, command sequence, expected outputs, common possible errors, and validation notes.

## BASE_003: Density calculation

Generate a complete GROMACS workflow to calculate the density of pure water at 300 K and 1 bar. Include topology preparation, MDP requirements, command sequence, expected outputs, common possible errors, and validation notes.

## BASE_004: MSD and diffusion

Generate a complete GROMACS workflow to calculate the mean-square displacement and diffusion coefficient of pure water at 300 K. Include trajectory preprocessing, command sequence, expected outputs, fitting note, common possible errors, and short-trajectory limitation.

## BASE_005: PBC trajectory preprocessing

Generate a complete GROMACS workflow to preprocess a pure water trajectory by correcting periodic boundary conditions, making molecules whole, centering the system, and producing a cleaned trajectory for later analysis. Include required files, command sequence, expected outputs, common errors, and validation notes.
