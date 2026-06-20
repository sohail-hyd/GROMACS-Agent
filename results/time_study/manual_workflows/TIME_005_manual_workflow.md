# TIME_005: PBC trajectory preprocessing

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

Before analysis, the trajectory should be corrected for periodic boundary conditions. The goal is to make molecules whole, remove jumps, and center the system if needed.

Commands:
gmx trjconv -s md.tpr -f md.xtc -o traj_whole.xtc -pbc whole

Then remove jumps:
gmx trjconv -s md.tpr -f traj_whole.xtc -o traj_nojump.xtc -pbc nojump

If centering is needed:
gmx trjconv -s md.tpr -f traj_nojump.xtc -o traj_centered.xtc -center -pbc mol

Expected output:
traj_whole.xtc
traj_nojump.xtc
traj_centered.xtc

Validation:
I will visually check the cleaned trajectory in VMD or another viewer. Molecules should not appear broken across the periodic boundary. The final trajectory should be suitable for RDF, MSD, density profile or hydrogen-bond analysis.
