# Manuscript Table: Baseline LLM vs GROMACS-Agent

| Task | Baseline LLM score | GROMACS-Agent score | Improvement | Main baseline error |
|---|---:|---:|---:|---|
| O-O RDF calculation | 5 | 10 | +5 | Topology-coordinate mismatch and inconsistent water-box preparation |
| Temperature time-series extraction | 8 | 10 | +2 | Weak validation and assumed time offsets |
| Density calculation | 6 | 10 | +4 | Incorrect water molecule counting and inconsistent topology preparation |
| MSD and diffusion workflow | 7 | 10 | +3 | Mixed PBC handling and unclear MSD fitting workflow |
| PBC trajectory preprocessing | 7 | 10 | +3 | Hard-coded index groups and unclear final trajectory purpose |

Average baseline score: 6.6/10

Average GROMACS-Agent score: 10/10

Average improvement: +3.4 points

This table reports evaluator-score improvement only. It should not be described as a measured human time-reduction result.
