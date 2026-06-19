# GROMACS-Agent Generated Workflow

## User task
Generate a GROMACS workflow to calculate O-O RDF of pure water at 600 K

## Retrieved validated workflow examples
['GSCF_002', 'GSCF_006', 'GSCF_007']

## Required input files
- `topol.top`
- coordinate file such as `water_box.gro`, `npt.gro`, or `md.gro`
- trajectory file such as `md.xtc` when post-processing is required
- run input file such as `md.tpr`
- energy file such as `md.edr` when energy analysis is required

## Topology and preparation check
Before running `gmx grompp`, confirm that `topol.top` exists and that the molecule count in `[ molecules ]` matches the coordinate file.

If the system is solvated using `gmx solvate`, count the final water molecules after solvation and write the correct `SOL` number into `topol.top`.

## Main analysis command
```bash
gmx rdf -f md.xtc -s md.tpr -o rdf_OW_OW.xvg -ref "name OW" -sel "name OW"
```

## Expected output
rdf_OW_OW.xvg

## Common errors and fixes
- Missing topology file: create or verify `topol.top`.
- Wrong solvent count: update `[ molecules ]` after `gmx solvate`.
- Wrong atom selection: check atom names in `.gro`, `.top`, or index groups.
- Interactive selection problem: use `echo` or explicit selections where possible.
- Short trajectory: do not claim publication-quality physical properties from very short tests.

## Validation note
Check that the first O-O RDF peak is physically reasonable. For pure water, the first O-O peak is commonly near 0.28 nm.

The generated workflow is considered valid only if commands run without fatal GROMACS errors and outputs are physically meaningful.
