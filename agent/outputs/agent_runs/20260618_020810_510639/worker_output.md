# GROMACS-Agent Generated Workflow

## User task
Generate a GROMACS workflow to extract temperature time series of pure water at 300 K

## Retrieved validated workflow examples
['GSCF_008', 'GSCF_010', 'GSCF_001']

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
echo Temperature | gmx energy -f md.edr -o temperature.xvg
```

## Expected output
temperature.xvg

## Common errors and fixes
- Missing topology file: create or verify `topol.top`.
- Wrong solvent count: update `[ molecules ]` after `gmx solvate`.
- Wrong atom selection: check atom names in `.gro`, `.top`, or index groups.
- Interactive selection problem: use `echo` or explicit selections where possible.
- Short trajectory: do not claim publication-quality physical properties from very short tests.

## Validation note
Temperature should fluctuate around the target temperature, for example 300 K.

The generated workflow is considered valid only if commands run without fatal GROMACS errors and outputs are physically meaningful.
