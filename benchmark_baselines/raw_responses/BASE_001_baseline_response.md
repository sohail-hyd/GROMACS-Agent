Here is a complete, reproducible GROMACS workflow to calculate the O–O radial distribution function (RDF) of pure SPC/E water at 300 K. All files, commands, and expected outputs are included.

---

## 1. Directory and Initial Structure

First, create a clean working directory:

```bash
mkdir -p ~/water_rdf_calc
cd ~/water_rdf_calc
```

We will use the `spc216.gro` generic SPC/E water box provided by GROMACS.  
The topology will be generated from `oplsaa.ff` or `spce.ff`; here we use the built-in SPC/E force field.

---

## 2. Required Input Files

### 2.1 Prepare topology and coordinate file from GROMACS data

```bash
# Copy the generic SPC/E water box (216 molecules) as a starting point
cp /usr/local/gromacs/share/gromacs/top/spc216.gro ./water_start.gro

# Generate a topology file using pdb2gmx (interactive/non-interactive)
# Since spc216.gro already contains SPC/E water, we create a minimal pdb first.
# Extract one water from spc216.gro to get atom names right.
gmx solvate -cs spc216.gro -o water_start.pdb -box 1.86206 1.86206 1.86206
# This creates a box with exactly 216 SPC/E waters; the -box dimensions equal
# the original spc216.gro box size: 1.86206 nm side length (density ~997 kg/m³).
```

**Alternative interactive preparation (if desired):**
```bash
# Remove any previous topology files
rm -f topol.top posre.itp

# pdb2gmx requires a .pdb input; create from existing .gro
gmx editconf -f water_start.gro -o water_start.pdb
# Now run pdb2gmx
gmx pdb2gmx -f water_start.pdb -o water_processed.gro -water spce -ff oplsaa -ignh
```

*Output:* `topol.top`, `posre.itp`, `water_processed.gro`.

We will use a simpler route: directly use the `spc216.gro` and manually write a correct topology file for SPC/E water.

### 2.2 Manual Topology File (`topol.top`)

Create `topol.top`:

```bash
cat > topol.top << 'EOF'
; Include force field parameters (SPC/E is a built-in model)
#include "spce.ff/forcefield.itp"

; Include water topology
#include "spce.ff/spce.itp"

; System definition
[ system ]
Pure SPC/E Water

[ molecules ]
; molecule name   count
SOL               216
EOF
```

*Note:* SPC/E water is rigid. The `spce.itp` defines bonds, angles, and the O–H distance with constraints.

### 2.3 Starting Coordinate File

If you used `solvate` above, you already have `water_start.gro`. Otherwise, create a 3×3×3 nm box of SPC/E water:

```bash
gmx solvate -cs spc216 -o water_box.gro -box 3.0 3.0 3.0 -maxsol 900
```

We will use the 216-molecule box for speed, but you can scale up for better statistics.  
Copy the final coordinates to `conf.gro`:

```bash
cp water_box.gro conf.gro
```

---

## 3. Parameter Files for MDP Runs

### 3.1 Energy Minimization: `em.mdp`

```bash
cat > em.mdp << 'EOF'
; Energy minimization
integrator       = steep
nsteps           = 5000
emtol            = 100.0
emstep           = 0.01

; Neighbour searching
cutoff-scheme    = Verlet
nstlist          = 10
ns-type          = grid
pbc              = xyz
rlist            = 1.0

; Electrostatics and VdW
coulombtype      = PME
rcoulomb         = 1.0
vdwtype          = Cut-off
rvdw             = 1.0

; Constraints
constraints      = none
EOF
```

### 3.2 NVT Equilibration: `nvt.mdp`

```bash
cat > nvt.mdp << 'EOF'
; NVT equilibration at 300 K
integrator        = md
nsteps            = 50000          ; 100 ps with 2 fs timestep
dt                = 0.002
comm-mode         = Linear
nstcomm           = 100

; Output control
nstxout           = 5000
nstvout           = 5000
nstenergy         = 1000
nstlog            = 1000

; Neighbour searching
cutoff-scheme     = Verlet
nstlist           = 10
ns-type           = grid
pbc               = xyz
rlist             = 1.0

; Electrostatics and VdW
coulombtype       = PME
rcoulomb          = 1.0
vdwtype           = Cut-off
rvdw              = 1.0

; Temperature coupling
tcoupl            = V-rescale
tc-grps           = System
tau_t             = 0.1
ref_t             = 300

; Pressure coupling is off for NVT
pcoupl            = no

; Constraints (SETTLE for rigid water)
constraints       = h-bonds
constraint-algorithm = LINCS
lincs-order       = 4
lincs-iter        = 1

; Generate velocities
gen_vel           = yes
gen_temp          = 300.0
gen_seed          = 12345
EOF
```

### 3.3 NPT Equilibration: `npt.mdp`

```bash
cat > npt.mdp << 'EOF'
; NPT equilibration
integrator        = md
nsteps            = 50000          ; 100 ps
dt                = 0.002

; Output control
nstxout           = 5000
nstvout           = 5000
nstenergy         = 1000
nstlog            = 1000

; Neighbour searching
cutoff-scheme     = Verlet
nstlist           = 10
ns-type           = grid
pbc               = xyz
rlist             = 1.0

; Electrostatics and VdW
coulombtype       = PME
rcoulomb          = 1.0
vdwtype           = Cut-off
rvdw              = 1.0

; Temperature coupling
tcoupl            = V-rescale
tc-grps           = System
tau_t             = 0.1
ref_t             = 300

; Pressure coupling
pcoupl            = Parrinello-Rahman
pcoupltype        = isotropic
tau_p             = 2.0
ref_p             = 1.0
compressibility   = 4.5e-5

; Constraints (SETTLE for rigid water)
constraints       = h-bonds
constraint-algorithm = LINCS
lincs-order       = 4
lincs-iter        = 1

; Continue from previous simulation
gen_vel           = no
EOF
```

### 3.4 Production MD: `md.mdp`

```bash
cat > md.mdp << 'EOF'
; Production MD for RDF calculation
integrator        = md
nsteps            = 500000         ; 1 ns (increase to 5–10 ns for good statistics)
dt                = 0.002

; Output control (frequent trajectory saving for RDF)
nstxout           = 1000           ; save coordinates every 2 ps
nstvout           = 5000
nstenergy         = 1000
nstlog            = 1000
nstxout-compressed = 1000
compressed-x-grps  = System

; Neighbour searching
cutoff-scheme     = Verlet
nstlist           = 10
ns-type           = grid
pbc               = xyz
rlist             = 1.0

; Electrostatics and VdW
coulombtype       = PME
rcoulomb          = 1.0
vdwtype           = Cut-off
rvdw              = 1.0

; Temperature coupling
tcoupl            = V-rescale
tc-grps           = System
tau_t             = 0.1
ref_t             = 300

; Pressure coupling
pcoupl            = Parrinello-Rahman
pcoupltype        = isotropic
tau_p             = 2.0
ref_p             = 1.0
compressibility   = 4.5e-5

; Constraints
constraints       = h-bonds
constraint-algorithm = LINCS
lincs-order       = 4
lincs-iter        = 1

; No velocity generation (restart from NPT)
gen_vel           = no
EOF
```

---

## 4. Command Sequence (Step-by-Step)

### Step 1: Prepare topology and coordinates

```bash
# Use the generic SPC/E water box (216 molecules, 1.86206 nm box)
gmx solvate -cs spc216.gro -o conf.gro -box 1.86206 1.86206 1.86206
```

(If your GROMACS data files are elsewhere, locate `spc216.gro` first: `find / -name spc216.gro 2>/dev/null`)

### Step 2: Energy Minimization

```bash
gmx grompp -f em.mdp -c conf.gro -p topol.top -o em.tpr -maxwarn 1
gmx mdrun -deffnm em -v
```

Check convergence:
```bash
gmx energy -f em.edr -o potential.xvg
# Select "Potential" (e.g., option 10) when prompted.
```

### Step 3: NVT Equilibration

```bash
gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr -maxwarn 1
gmx mdrun -deffnm nvt -v
```

Monitor temperature:
```bash
gmx energy -f nvt.edr -o temperature.xvg
# Select "Temperature"
```

The temperature should fluctuate around 300 K (± a few K).

### Step 4: NPT Equilibration

```bash
gmx grompp -f npt.mdp -c nvt.gro -p topol.top -o npt.tpr -maxwarn 1
gmx mdrun -deffnm npt -v
```

Monitor density and pressure:
```bash
gmx energy -f npt.edr -o density.xvg
# Select "Density"
# Expect density ~997 kg/m³ for SPC/E at 300 K, 1 bar.
```

### Step 5: Production MD

```bash
gmx grompp -f md.mdp -c npt.gro -p topol.top -o md.tpr -maxwarn 1
gmx mdrun -deffnm md -v
```

### Step 6: Rerun with (optional) higher precision, or directly compute RDF

```bash
# Compute O-O RDF. Selection: atom type OW (or O, depending on force field naming)
gmx rdf -f md.xtc -s md.tpr -n index.ndx -ref "name OW" -sel "name OW" -o oo_rdf.xvg -b 200 -e 1000 -rmax 1.0 -bin 0.002
```

If you don't have an index file, create one:

```bash
gmx make_ndx -f md.tpr -o index.ndx <<< "q"
# Alternatively, type manually:
# gmx make_ndx -f md.tpr -o index.ndx
# > a OW      (atoms named OW)
# > name 18 OW_only
# > q
```

Then:
```bash
gmx rdf -f md.xtc -s md.tpr -n index.ndx -ref OW_only -sel OW_only -o oo_rdf.xvg -b 200 -e 1000
```

---

## 5. Expected Output Files

| File(s)                | Description |
|------------------------|-------------|
| `conf.gro`             | Initial configuration |
| `topol.top`            | System topology |
| `em.tpr`, `em.gro`, `em.edr`, `em.log` | Energy minimization |
| `nvt.tpr`, `nvt.gro`, `nvt.edr`, `nvt.log` | NVT equilibration |
| `npt.tpr`, `npt.gro`, `npt.edr`, `npt.log` | NPT equilibration |
| `md.tpr`, `md.xtc`, `md.edr`, `md.gro`, `md.log`, `md.cpt` | Production run |
| `oo_rdf.xvg`           | **Final O–O radial distribution function** |
| `index.ndx`            | Index file for atom selection |

---

## 6. Analyzing the RDF

```bash
# Plot with GROMACS tool or your favourite plotting program
xmgrace oo_rdf.xvg
# or use Python:
python3 -c "
import numpy as np
import matplotlib.pyplot as plt
r, goo = np.loadtxt('oo_rdf.xvg', comments=('#', '@'))
plt.plot(r, goo)
plt.xlabel('r (nm)')
plt.ylabel('g(r)')
plt.title('O–O Radial Distribution Function of SPC/E Water at 300 K')
plt.grid(True)
plt.savefig('oo_rdf.png')
plt.show()
"
```

**Expected features of the O–O RDF:**
- First peak at ~0.275–0.280 nm (first coordination shell)
- First minimum at ~0.33–0.34 nm
- Second peak at ~0.45 nm
- Long-range limit approaching 1.0
- Coordination number (integral of first peak) ≈ 4.5–5.0 for SPC/E at 300 K

---

## 7. Common Possible Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Atomtype OW not found` | Wrong atom name in selection | Use `gmx dump -s md.tpr \| grep "atomname"` to find correct atom name; use `name OW` or `name O` |
| `No default Angle/Dih. types` | Incomplete force field includes | Ensure `#include "spce.ff/forcefield.itp"` is in `topol.top` |
| `System has non-zero total charge` | Wrong number of molecules | SPC/E water has zero charge per molecule; check molecule count matches coordinates |
| `Water molecule cannot be settled` | Bad initial configuration, overlapping atoms | Rebuild the box with `gmx solvate` or reduce density slightly |
| `Density too low/high` | NPT not converged | Run longer NPT equilibration; check `npt.edr` for density evolution |
| `LINCS warnings` | Too large timestep or initial bad contacts | Ensure 2 fs timestep, SETTLE is used; verify minimization converged |
| `RDF noisy or unphysical` | Insufficient sampling | Use longer production MD (≥5 ns) and discard initial equilibration period (`-b` flag) |
| `Segmentation fault with rdf` | Very large trajectory | Use `gmx trjconv` to extract only OW atoms: `gmx trjconv -f md.xtc -s md.tpr -o ow_only.xtc -n index.ndx` |

---

## 8. Validation Notes

### Expected O–O RDF Parameters for SPC/E Water at 300 K, 1 bar

From the literature (e.g., Mark & Nilsson, *J. Phys. Chem. B* 2001):

- **First peak position (rₘₐₓ₁)**: 0.275 nm (±0.002)
- **First peak height (g(rₘₐₓ₁))**: ~2.8–3.0
- **First minimum (rₘᵢₙ₁)**: 0.33–0.34 nm
- **Coordination number (n(rₘᵢₙ₁))**: ~4.7 (integrated to first minimum)
- **Second peak position**: 0.45–0.47 nm
- **Density**: 997 ± 2 kg/m³

### Validation Steps

1. **Check temperature** during MD:  
   `gmx energy -f md.edr -o temp_prod.xvg` → select `Temperature`  
   Average must be ~300 K, RMSF < 5 K.

2. **Check pressure** (should be ~1 bar, with large fluctuations):  
   `gmx energy -f md.edr -o press_prod.xvg` → select `Pressure`

3. **Check density**:  
   `gmx energy -f npt.edr -o density.xvg` → select `Density`  
   Should converge to 997–1000 kg/m³.

4. **Check energy conservation (NVE test)** – optional:  
   A short NVE run following NPT equilibration should show energy drift < 1% per ns.

5. **Check RDF symmetry and limit**:  
   `g(r) → 1.0` as `r → large`. If not, box size may be too small; use at least a 3 nm box.

### Quick Validation Script

```bash
#!/bin/bash
# validate.sh – quick validation of the results

echo "=== Temperature ==="
gmx energy -f md.edr -o temp.xvg <<< "Temperature" 2>&1 | grep -E "Temperature.*[0-9]+\.[0-9]+"

echo "=== Density ==="
gmx energy -f npt.edr -o dens.xvg <<< "Density" 2>&1 | grep -E "Density.*[0-9]+\.[0-9]+"

echo "=== RDF first peak ==="
awk 'NR>24 && $2 > max { max=$2; r=$1 } END { print "First peak at", r, "nm with height", max }' oo_rdf.xvg
```

---

## 9. Full Reproducible Shell Script

Save the following as `run_water_rdf.sh`:

```bash
#!/bin/bash
set -e

# ============================
# SPC/E Water O–O RDF Workflow
# ============================

# Step 1: Setup
echo "Setting up SPC/E water box..."
gmx solvate -cs spc216.gro -o conf.gro -box 1.86206 1.86206 1.86206

cat > topol.top << 'EOF'
#include "spce.ff/forcefield.itp"
#include "spce.ff/spce.itp"

[ system ]
Pure SPC/E Water

[ molecules ]
SOL  216
EOF

# Create mdp files (em, nvt, npt, md) – omitted here, assume present.

# Step 2: EM
echo "Energy minimization..."
gmx grompp -f em.mdp -c conf.gro -p topol.top -o em.tpr -maxwarn 1
gmx mdrun -deffnm em -v

# Step 3: NVT
echo "NVT equilibration..."
gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr -maxwarn 1
gmx mdrun -deffnm nvt -v

# Step 4: NPT
echo "NPT equilibration..."
gmx grompp -f npt.mdp -c nvt.gro -p topol.top -o npt.tpr -maxwarn 1
gmx mdrun -deffnm npt -v

# Step 5: Production
echo "Production MD..."
gmx grompp -f md.mdp -c npt.gro -p topol.top -o md.tpr -maxwarn 1
gmx mdrun -deffnm md -v

# Step 6: RDF
echo "Calculating O–O RDF..."
gmx make_ndx -f md.tpr -o index.ndx <<< "a OW\nname 18 OW_only\nq"
gmx rdf -f md.xtc -s md.tpr -n index.ndx -ref OW_only -sel OW_only -o oo_rdf.xvg -b 200 -e 1000

echo "Workflow complete. RDF saved to oo_rdf.xvg"
```


