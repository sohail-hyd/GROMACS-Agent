# GROMACS-Agent Generated Workflow

## User task
Generate a complete GROMACS workflow to calculate density of pure water at 280 K and 1 bar.

## Retrieved validated workflow examples
['GSCF_001', 'GSCF_005', 'GSCF_100']

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
echo Density | gmx energy -f md.edr -o density.xvg
```

## Expected output
density.xvg

## Common errors and fixes
- Missing topology file: create or verify `topol.top`.
- Wrong solvent count: update `[ molecules ]` after `gmx solvate`.
- Wrong atom selection: check atom names in `.gro`, `.top`, or index groups.
- Interactive selection problem: use `echo` or explicit selections where possible.
- Short trajectory: do not claim publication-quality physical properties from very short tests.

## Validation note
Average density should be checked against expected water density near the simulated thermodynamic state.

The generated workflow is considered valid only if commands run without fatal GROMACS errors and outputs are physically meaningful.
