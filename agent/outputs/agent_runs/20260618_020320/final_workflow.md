# GROMACS-Agent Generated Workflow

## User task
Generate a GROMACS workflow to calculate MSD and diffusion of pure water at 300 K

## Retrieved validated workflow examples
['GSCF_003', 'GSCF_001', 'GSCF_002']

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
echo System | gmx trjconv -s md.tpr -f md.xtc -o md_nojump.xtc -pbc nojump
gmx msd -f md_nojump.xtc -s md.tpr -o msd_water.xvg
```

## Expected output
md_nojump.xtc, msd_water.xvg

## Common errors and fixes
- Missing topology file: create or verify `topol.top`.
- Wrong solvent count: update `[ molecules ]` after `gmx solvate`.
- Wrong atom selection: check atom names in `.gro`, `.top`, or index groups.
- Interactive selection problem: use `echo` or explicit selections where possible.
- Short trajectory: do not claim publication-quality physical properties from very short tests.

## Validation note
Use the linear MSD region only. Short trajectories are workflow-validation tests, not final diffusion estimates.

The generated workflow is considered valid only if commands run without fatal GROMACS errors and outputs are physically meaningful.
