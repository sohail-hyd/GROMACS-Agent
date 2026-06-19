# Pure water density calculation at 300 K using GROMACS

# 1. Create water box
gmx solvate -cs spc216.gro -o water_box.gro -box 3 3 3

# 2. Count water molecules
N=$(grep -c " OW" water_box.gro)

# 3. Create topology
cat > topol.top << EOT
#include "oplsaa.ff/forcefield.itp"
#include "oplsaa.ff/spc.itp"

[ system ]
Pure water box

[ molecules ]
SOL $N
EOT

# 4. Energy minimization
gmx grompp -f minim.mdp -c water_box.gro -p topol.top -o em.tpr
gmx mdrun -s em.tpr -deffnm em

# 5. NVT equilibration
gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr
gmx mdrun -s nvt.tpr -deffnm nvt

# 6. NPT equilibration
gmx grompp -f npt.mdp -c nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
gmx mdrun -s npt.tpr -deffnm npt

# 7. Production MD
gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr
gmx mdrun -s md.tpr -deffnm md

# 8. Density extraction
echo "Density" | gmx energy -f md.edr -o density.xvg

# 9. Average density
awk '!/^[@#]/ {sum+=$2; n++} END {print "Average density = ", sum/n, "kg/m^3"}' density.xvg
