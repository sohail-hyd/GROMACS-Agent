# Fresh local clone usability test

This test checks whether GROMACS-Agent can run from a fresh cloned copy of the repository.

## Test type

Local fresh-clone test.

The public GitHub HTTPS clone was attempted, but the network connection failed due to TLS/GitHub connection errors. Therefore, a local fresh clone was used to verify that the repository can run from a clean copied clone.

## Test command

git clone ~/gromacs_llm_agent_paper GROMACS-Agent
cd GROMACS-Agent
python3 agent/gromacs_agent.py --task "Generate a complete GROMACS workflow to calculate O-O RDF of pure water at 300 K."

## Result

The local fresh-clone test successfully generated a GROMACS workflow output from a natural-language task and saved output files in agent/outputs/agent_runs/.

## Interpretation

This confirms that the repository can run from a fresh local clone. A true public GitHub fresh-clone test should be repeated later using a stable internet connection.
