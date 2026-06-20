# Public project overview

## What is GROMACS-Agent?

GROMACS-Agent is a research prototype inspired by MDAgent-style molecular dynamics automation. It extends text-to-code molecular dynamics agent ideas toward GROMACS-specific text-to-workflow generation.

GROMACS workflows are different from single-script workflows because they require multiple files and steps, including `.gro`, `.top`, `.mdp`, `.tpr`, `.xtc`, `.edr`, `.xvg`, post-processing commands, atom/group selections, and validation checks.

## Main purpose

The purpose of GROMACS-Agent is to convert a natural-language GROMACS task into a checked and corrected GROMACS workflow.

Example task:

```bash
Generate a complete GROMACS workflow to calculate O-O RDF of pure water at 300 K.
