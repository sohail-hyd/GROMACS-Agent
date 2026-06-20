# TIME_002: Temperature time-series extraction

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

The energy file md.edr contains temperature, pressure, density and energy terms. I will use gmx energy to extract the temperature time series.

Commands:
gmx energy -f md.edr -o temperature.xvg

When GROMACS asks for energy term, I will select Temperature.

Alternative non-interactive command:
echo Temperature | gmx energy -f md.edr -o temperature.xvg

Expected output:
temperature.xvg

Validation:
I will check that the average temperature is close to the target temperature, for example 300 K for pure water. I will also check that the temperature is stable with no strong drift after equilibration.
