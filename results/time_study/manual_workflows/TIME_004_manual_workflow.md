# TIME_004: MSD and diffusion

Write the complete manual GROMACS workflow below.

Include:
1. Required input files
2. Required topology/MDP/TPR files
3. Command sequence
4. Analysis command
5. Expected output files
6. Validation note

Manual workflow:
Required input files:
md.tpr, md.xtc, topol.top, index file if needed.

For diffusion calculation, the trajectory should be corrected for periodic boundary conditions. I will first make molecules whole and remove jumps using trjconv.

Commands:
gmx trjconv -s md.tpr -f md.xtc -o md_nojump.xtc -pbc nojump

Then calculate MSD:
gmx msd -s md.tpr -f md_nojump.xtc -o msd_water.xvg

When GROMACS asks for group, I will select Water or System depending on the system. For pure water, Water is preferred if available.

Expected output:
md_nojump.xtc
msd_water.xvg

Validation:
The MSD curve should increase approximately linearly after the initial short-time region. The diffusion coefficient should be calculated from the linear fit region using D = slope / 6 for 3D diffusion. If the trajectory is short, I will report it only as workflow validation, not as final physical diffusion data.
