# Baseline comparison plan

This file defines the planned comparison between a baseline LLM workflow and the GROMACS-Agent workflow.

## Purpose

The purpose is to evaluate whether GROMACS-Agent improves GROMACS workflow correctness compared with a normal baseline LLM response.

## Benchmark tasks

Five benchmark tasks are used:

1. O-O RDF calculation for pure water
2. Temperature time-series extraction
3. Density calculation
4. MSD and diffusion workflow
5. PBC trajectory preprocessing

## Planned scoring

Each baseline LLM workflow and GROMACS-Agent workflow should be scored using the same 10-point GROMACS evaluator rubric.

## Current status

GROMACS-Agent already achieved final evaluator scores of 10 for the five MDAgent-style demo tasks. Baseline LLM scores are not yet measured and must be added after separate baseline testing.

## Important note

The current manuscript should not claim a measured time reduction or full superiority over baseline LLMs until this comparison is completed.
