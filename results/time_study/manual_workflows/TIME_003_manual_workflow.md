# TIME_003: Density calculation

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
md.edr, md.tpr, md.log if available.

The density value can be extracted from the GROMACS energy file. I will not count water molecules manually from conf.gro because that can count atoms incorrectly. The correct way is to use gmx energy and select Density.

Commands:
gmx energy -f md.edr -o density.xvg

When GROMACS asks for the energy term, I will select Density.

Alternative command:
echo Density | gmx energy -f md.edr -o density.xvg

Expected output:
density.xvg

Validation:
For pure water near 300 K and 1 bar, the density should be close to about 1000 kg/m3. Small differences are possible because of force field, box size and short trajectory length. I will calculate the average density from the stable part of the trajectory.
