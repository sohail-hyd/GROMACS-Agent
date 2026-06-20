
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

First I will check that the simulation files exist. The md.tpr file contains topology and atom information, while md.xtc contains the trajectory. For O-O RDF of water, I need to select oxygen atoms of water, usually OW for SPC/E or TIP water.

Commands:
gmx check -f md.xtc
gmx check -s md.tpr

Then calculate RDF:
gmx rdf -f md.xtc -s md.tpr -o rdf_OW_OW.xvg -ref "name OW" -sel "name OW"

If selection syntax gives problem, I will make index file:
gmx make_ndx -f md.tpr -o index.ndx
Then select water oxygen group and run:
gmx rdf -f md.xtc -s md.tpr -n index.ndx -o rdf_OW_OW.xvg

Expected output:
rdf_OW_OW.xvg

Validation:
The first O-O RDF peak for liquid water should appear near 0.27–0.28 nm. The peak height should be reasonable for liquid water. I will plot rdf_OW_OW.xvg and check that g(r) approaches 1 at large distance.
