
## Pilot workflow-preparation timing study

A single-user pilot timing study was conducted to estimate the local workflow-preparation speed of GROMACS-Agent compared with manual workflow writing. Five representative GROMACS workflow tasks were evaluated, and each manual workflow was saved as text evidence during timing.

The cleaned timing dataset contained 5 valid tasks. The average manual workflow-writing time was 47.04 s, whereas the average local GROMACS-Agent generation time was 0.0580 s. This corresponds to an average local workflow-preparation time reduction of 99.74% in this pilot test.

| Task | Manual time (s) | Agent time (s) | Reduction (%) | Manual word count |
|---|---:|---:|---:|---:|
| O-O RDF calculation | 165.20 | 0.0600 | 99.96 | 181 |
| Temperature time-series extraction | 22.84 | 0.1100 | 99.52 | 134 |
| Density calculation | 15.55 | 0.0400 | 99.74 | 158 |
| MSD and diffusion | 16.68 | 0.0400 | 99.76 | 170 |
| PBC trajectory preprocessing | 14.94 | 0.0400 | 99.73 | 152 |

This result is reported as a single-user pilot timing result. It measures local workflow preparation only and does not include full GROMACS simulation runtime, model fine-tuning runtime, or broader multi-user productivity testing.
