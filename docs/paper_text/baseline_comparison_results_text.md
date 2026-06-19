# Paper-ready baseline comparison results

## Baseline comparison summary

Five representative GROMACS workflow tasks were used to compare normal baseline LLM responses with the GROMACS-Agent outputs. The tasks included O-O RDF calculation, temperature time-series extraction, density calculation, MSD/diffusion analysis, and PBC trajectory preprocessing.

The baseline LLM responses were scored using the same 10-point GEQS rubric used by GromacsEvaluatorAgent. The baseline scores were 5, 8, 6, 7, and 7 for the five tasks, giving an average baseline score of 6.6/10. In contrast, the corresponding GROMACS-Agent workflows achieved evaluator scores of 10/10 for all five tasks, giving an average score of 10/10.

The average improvement was therefore 3.4 points on the 10-point rubric. The largest improvement occurred for the O-O RDF and density workflows, where the baseline LLM responses contained topology-coordinate mismatch risks, inconsistent system preparation, or incorrect water molecule counting. GROMACS-Agent avoided these errors by retrieving related validated examples, applying a GROMACS-specific evaluation rubric, and producing corrected workflow outputs.

The comparison demonstrates that GROMACS-Agent improves workflow correctness and reproducibility for representative GROMACS analysis tasks compared with unassisted baseline LLM responses. However, this comparison measures evaluator score improvement only. It does not yet constitute a controlled human time-reduction study.
