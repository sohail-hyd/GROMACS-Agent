Here is a complete, reproducible GROMACS workflow to calculate the density of pure SPC/E water at 300 K and 1 bar, with comprehensive validation and error analysis.

---

## 1. Overview and Theory

The density (ρ) is calculated from the simulation as:

$$\rho = \frac{N \cdot M}{N_A \cdot V}$$

Where:
- N = number of water molecules
- M = molar mass of water (18.0153 g/mol for SPC/E)
- N_A = Avogadro's number (6.02214076 × 10²³ mol⁻¹)
- V = average volume of the simulation box (nm³)

**Expected density for SPC/E at 300 K, 1 bar:** 997 ± 2 kg/m³

---

## 2. Directory Structure and Initial Setup

```bash
# Create clean working directory
mkdir -p ~/water_density_calc
cd ~/water_density_calc
```

---

## 3. Required Input Files

### 3.1 Topology File (`topol.top`)

Create a topology file for SPC/E water:

```bash
cat > topol.top << 'EOF'
; Include SPC/E force field parameters
#include "spce.ff/forcefield.itp"

; Include SPC/E water topology (rigid, with SETTLE)
#include "spce.ff/spce.itp"

; System definition
[ system ]
Pure SPC/E Water for Density Calculation

[ molecules ]
; molecule name   count
SOL               216
EOF
```

**For a larger system (recommended for better statistics):**

```bash
cat > topol_large.top << 'EOF'
#include "spce.ff/forcefield.itp"
#include "spce.ff/spce.itp"

[ system ]
Pure SPC/E Water - Large Box

[ molecules ]
SOL               8788
EOF
```

### 3.2 Generate Initial Coordinates

**Option A: Small 216-molecule box (quick test)**
```bash
# Exact 216-water box from GROMACS distribution
gmx solvate -cs spc216.gro -o conf.gro -box 1.86206 1.86206 1.86206 -maxsol 216
```

**Option B: Larger box for better density statistics (recommended)**
```bash
# Generate a ~6.4 nm cubic box with ~8788 waters
gmx solvate -cs spc216.gro -o conf_large.gro -box 6.4 6.4 6.4 -maxsol 9000
# Copy to standard name
cp conf_large.gro conf.gro
# Update topology accordingly
cp topol_large.top topol.top
```

**Option C: Custom box size**
```bash
# 5 nm box (~3000 waters)
gmx solvate -cs spc216.gro -o conf.gro -box 5.0 5.0 5.0 -maxsol 4500
# Count actual waters in the box:
WATER_COUNT=$(grep "SOL" conf.gro | wc -l)
echo "Generated box with $WATER_COUNT water molecules"
# Update topology with actual count
sed -i "s/SOL.*[0-9]*/SOL               $WATER_COUNT/" topol.top
```

### 3.3 Find GROMACS Data Directory (if needed)

```bash
# Find where spc216.gro is located
GMX_DATA=$(gmx -h 2>&1 | grep "Data prefix" | awk '{print $3}')
# or
GMX_DATA=$(dirname $(find / -name "spc216.gro" -type f 2>/dev/null | head -1))
echo "GROMACS data directory: $GMX_DATA"
```

---

## 4. MDP Parameter Files

### 4.1 Energy Minimization: `em.mdp`

```bash
cat > em.mdp << 'EOF'
; Energy Minimization
integrator          = steep
nsteps              = 5000
emtol               = 100.0
emstep              = 0.01

; Cutoffs
cutoff-scheme       = Verlet
nstlist             = 10
ns-type             = grid
pbc                 = xyz
rlist               = 1.0

; Electrostatics
coulombtype         = PME
rcoulomb            = 1.0

; Van der Waals
vdwtype             = Cut-off
rvdw                = 1.0

; No constraints during EM (avoids issues with bad contacts)
constraints         = none
EOF
```

### 4.2 NVT Equilibration: `nvt.mdp`

```bash
cat > nvt.mdp << 'EOF'
; NVT Equilibration - stabilize temperature
integrator          = md
nsteps              = 50000          ; 100 ps
dt                  = 0.002          ; 2 fs timestep

; Output control
nstxout             = 5000
nstvout             = 5000
nstenergy           = 1000
nstlog              = 1000

; Neighbor searching
cutoff-scheme       = Verlet
nstlist             = 10
ns-type             = grid
pbc                 = xyz
rlist               = 1.0

; Electrostatics
coulombtype         = PME
rcoulomb            = 1.0
fourierspacing      = 0.12
pme-order           = 4

; Van der Waals
vdwtype             = Cut-off
rvdw                = 1.0
DispCorr            = EnerPres     ; IMPORTANT for accurate pressure/density

; Temperature coupling (velocity rescaling)
tcoupl              = V-rescale
tc-grps             = System
tau_t               = 0.1           ; 0.1 ps coupling time
ref_t               = 300           ; 300 K target

; Pressure coupling (off for NVT)
pcoupl              = no

; Constraints (SETTLE for rigid water)
constraints         = h-bonds
constraint-algorithm = LINCS
lincs-order         = 4
lincs-iter          = 1

; Velocity generation
gen_vel             = yes
gen_temp            = 300.0
gen_seed            = 987654
EOF
```

### 4.3 NPT Equilibration: `npt.mdp`

```bash
cat > npt.mdp << 'EOF'
; NPT Equilibration - stabilize density
integrator          = md
nsteps              = 100000         ; 200 ps (longer for density stabilization)
dt                  = 0.002

; Output control
nstxout             = 5000
nstvout             = 5000
nstenergy           = 1000           ; Save energy every 1 ps for high-res density
nstlog              = 1000

; Neighbor searching
cutoff-scheme       = Verlet
nstlist             = 10
ns-type             = grid
pbc                 = xyz
rlist               = 1.0

; Electrostatics
coulombtype         = PME
rcoulomb            = 1.0
fourierspacing      = 0.12
pme-order           = 4

; Van der Waals
vdwtype             = Cut-off
rvdw                = 1.0
DispCorr            = EnerPres     ; CRITICAL: dispersion correction for accurate density

; Temperature coupling
tcoupl              = V-rescale
tc-grps             = System
tau_t               = 0.1
ref_t               = 300

; Pressure coupling (Parinello-Rahman for NPT)
pcoupl              = Parrinello-Rahman
pcoupltype          = isotropic
tau_p               = 2.0           ; 2 ps pressure coupling time
ref_p               = 1.0           ; 1 bar
compressibility     = 4.5e-5        ; Water compressibility (bar⁻¹)

; Constraints
constraints         = h-bonds
constraint-algorithm = LINCS
lincs-order         = 4
lincs-iter          = 1

; Continue from NVT
gen_vel             = no
EOF
```

### 4.4 Production MD (NPT): `md.mdp`

```bash
cat > md.mdp << 'EOF'
; Production MD for density calculation
integrator          = md
nsteps              = 2500000        ; 5 ns (increase to 20-50 ns for publication)
dt                  = 0.002

; Output control - frequent energy saving for density time series
nstxout             = 5000
nstvout             = 5000
nstenergy           = 100            ; Save every 0.1 ps for detailed density analysis
nstlog              = 1000
nstxout-compressed  = 5000
compressed-x-grps   = System

; Neighbor searching
cutoff-scheme       = Verlet
nstlist             = 10
ns-type             = grid
pbc                 = xyz
rlist               = 1.0

; Electrostatics
coulombtype         = PME
rcoulomb            = 1.0
fourierspacing      = 0.12
pme-order           = 4

; Van der Waals
vdwtype             = Cut-off
rvdw                = 1.0
DispCorr            = EnerPres     ; MUST be on for accurate density

; Temperature coupling
tcoupl              = V-rescale
tc-grps             = System
tau_t               = 0.1
ref_t               = 300

; Pressure coupling
pcoupl              = Parrinello-Rahman
pcoupltype          = isotropic
tau_p               = 2.0
ref_p               = 1.0
compressibility     = 4.5e-5

; Constraints
constraints         = h-bonds
constraint-algorithm = LINCS
lincs-order         = 4
lincs-iter          = 1

; Continue from NPT
gen_vel             = no
EOF
```

### 4.5 Optional: NVE Production for Energy Conservation Check

```bash
cat > nve_check.mdp << 'EOF'
; Short NVE run to check energy conservation
integrator          = md
nsteps              = 50000          ; 100 ps
dt                  = 0.002

nstxout             = 5000
nstvout             = 5000
nstenergy           = 100
nstlog              = 1000

cutoff-scheme       = Verlet
nstlist             = 10
ns-type             = grid
pbc                 = xyz
rlist               = 1.0

coulombtype         = PME
rcoulomb            = 1.0
vdwtype             = Cut-off
rvdw                = 1.0
DispCorr            = EnerPres

; No temperature or pressure coupling for NVE
tcoupl              = no
pcoupl              = no

constraints         = h-bonds
constraint-algorithm = LINCS
lincs-order         = 4
lincs-iter          = 1

gen_vel             = no
EOF
```

---

## 5. Complete Command Sequence

### Step 1: Verify System Setup

```bash
echo "=== System Information ==="
echo "Molecules in topology:"
grep "^SOL" topol.top
echo ""
echo "Atoms in coordinate file:"
grep -c "OW\|HW" conf.gro
echo ""
echo "Box size (from conf.gro):"
tail -1 conf.gro
```

### Step 2: Energy Minimization

```bash
echo "Running energy minimization..."
gmx grompp -f em.mdp -c conf.gro -p topol.top -o em.tpr -maxwarn 1
gmx mdrun -deffnm em -v -ntmpi 1

# Check minimization convergence
echo "Potential energy after minimization:"
gmx energy -f em.edr -o potential_em.xvg <<< "Potential" 2>&1 | grep "Potential"
```

### Step 3: NVT Equilibration

```bash
echo "Running NVT equilibration..."
gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr -maxwarn 1
gmx mdrun -deffnm nvt -v -ntmpi 1

# Quick temperature check
echo "Temperature during NVT:"
gmx energy -f nvt.edr -o temp_nvt.xvg <<< "Temperature" 2>&1 | grep -A 5 "Energy Average"
```

### Step 4: NPT Equilibration

```bash
echo "Running NPT equilibration..."
gmx grompp -f npt.mdp -c nvt.gro -p topol.top -o npt.tpr -maxwarn 1
gmx mdrun -deffnm npt -v -ntmpi 1

# Check density convergence during NPT
gmx energy -f npt.edr -o density_npt.xvg <<< "Density"
echo "Density at end of NPT:"
tail -1 density_npt.xvg
```

### Step 5: Production MD

```bash
echo "Running production MD..."
gmx grompp -f md.mdp -c npt.gro -p topol.top -o md.tpr -maxwarn 1
gmx mdrun -deffnm md -v -ntmpi 1
```

### Step 6: Optional NVE Energy Conservation Check

```bash
echo "Running NVE energy conservation check..."
gmx grompp -f nve_check.mdp -c md.gro -p topol.top -o nve.tpr -maxwarn 1
gmx mdrun -deffnm nve -v -ntmpi 1
```

---

## 6. Density Extraction and Analysis

### 6.1 Extract Density from Production MD

```bash
# Extract density time series from energy file
gmx energy -f md.edr -o density_prod.xvg <<< "Density"

# Extract volume time series (for manual density calculation)
gmx energy -f md.edr -o volume_prod.xvg <<< "Volume"
```

### 6.2 Basic Density Statistics

```bash
# Using GROMACS analyze tool
grep -v "^[#@]" density_prod.xvg | awk '{print $2}' > density_values.dat
gmx analyze -f density_values.dat -av -ee -ac density_acf.xvg 2>&1 | tee density_statistics.txt
```

### 6.3 Comprehensive Python Density Analysis Script

Create `analyze_density.py`:

```python
#!/usr/bin/env python3
"""
Comprehensive density analysis for GROMACS water simulation.
Calculates density from volume, performs block averaging,
and generates publication-quality figures.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import argparse
import os

# Physical constants
NA = 6.02214076e23  # Avogadro's number
MW_SPCE = 18.0153   # SPC/E water molecular weight (g/mol)

def read_xvg(filename):
    """Read GROMACS XVG file, returning time and data arrays."""
    time, data = [], []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith(('#', '@')):
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                time.append(float(parts[0]))
                data.append(float(parts[1]))
    return np.array(time), np.array(data)

def calculate_density_from_volume(volume_nm3, n_molecules, mw=MW_SPCE):
    """Calculate density in kg/m³ from volume in nm³."""
    # Volume in m³
    volume_m3 = volume_nm3 * 1e-27
    # Mass per molecule in kg
    mass_per_molecule = mw / (NA * 1000)  # kg
    # Total mass
    total_mass = n_molecules * mass_per_molecule
    # Density
    density = total_mass / volume_m3
    return density

def block_averaging(data, min_blocks=4, max_blocks=50):
    """Perform block averaging for error estimation."""
    n = len(data)
    block_sizes = []
    block_sems = []
    
    for n_blocks in range(min_blocks, max_blocks + 1):
        block_size = n // n_blocks
        if block_size < 10:
            break
        
        block_means = []
        for i in range(n_blocks):
            block = data[i*block_size:(i+1)*block_size]
            if len(block) > 0:
                block_means.append(np.mean(block))
        
        block_sizes.append(block_size)
        block_sems.append(np.std(block_means, ddof=1) / np.sqrt(n_blocks))
    
    return np.array(block_sizes), np.array(block_sems)

def compute_detailed_statistics(time, density, volume=None, n_molecules=None):
    """Compute comprehensive density statistics."""
    
    # Use only the latter half of the trajectory (equilibrated portion)
    n_points = len(density)
    equilibrated_start = n_points // 2
    density_eq = density[equilibrated_start:]
    time_eq = time[equilibrated_start:]
    
    # Basic statistics
    mean_density = np.mean(density_eq)
    std_density = np.std(density_eq, ddof=1)
    min_density = np.min(density_eq)
    max_density = np.max(density_eq)
    
    # Block averaging for error estimation
    block_sizes, block_sems = block_averaging(density_eq)
    
    # Find converged SEM (smallest SEM from plateau)
    if len(block_sems) > 5:
        # Use the median of last 20% as converged value
        sem_converged = np.median(block_sems[-max(1, len(block_sems)//5):])
    else:
        sem_converged = block_sems[-1] if len(block_sems) > 0 else std_density/np.sqrt(len(density_eq))
    
    # Density drift analysis
    slope, intercept, r_value, p_value, std_err = stats.linregress(time_eq, density_eq)
    drift_per_ns = slope * 1000  # Convert from K/ps to K/ns
    
    # Volume-based density if volume data provided
    vol_density = None
    if volume is not None and n_molecules is not None:
        volume_eq = volume[equilibrated_start:]
        vol_density = calculate_density_from_volume(volume_eq, n_molecules)
        mean_vol_density = np.mean(vol_density)
    else:
        mean_vol_density = None
    
    # Check for normality
    _, normality_p = stats.normaltest(density_eq)
    is_normal = normality_p > 0.01
    
    # Relative standard deviation
    rel_std = (std_density / mean_density) * 100
    
    return {
        'mean': mean_density,
        'std': std_density,
        'sem': sem_converged,
        'min': min_density,
        'max': max_density,
        'rel_std': rel_std,
        'drift_per_ns': drift_per_ns,
        'r_squared': r_value**2,
        'normality_p': normality_p,
        'is_normal': is_normal,
        'vol_density': mean_vol_density,
        'n_equilibrated': len(density_eq)
    }

def plot_density_analysis(time, density, volume, n_molecules, stats, 
                          output_prefix='density_analysis'):
    """Generate comprehensive density analysis plots."""
    
    n_points = len(density)
    equil_start = n_points // 2
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    
    # 1. Density vs Time (full trajectory)
    ax1 = axes[0, 0]
    ax1.plot(time, density, 'b-', linewidth=0.5, alpha=0.7, label='Density')
    ax1.axvline(x=time[equil_start], color='orange', linestyle=':', 
                label=f'Equilibration cutoff ({time[equil_start]:.0f} ps)')
    ax1.axhline(y=stats['mean'], color='red', linestyle='--', 
                label=f"Mean: {stats['mean']:.1f} kg/m³")
    ax1.axhspan(stats['mean']-stats['std'], stats['mean']+stats['std'], 
                alpha=0.2, color='red', label=f"±1σ: {stats['std']:.1f}")
    ax1.set_xlabel('Time (ps)')
    ax1.set_ylabel('Density (kg/m³)')
    ax1.set_title('Density Time Series (Full Trajectory)')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # 2. Density Distribution (equilibrated)
    ax2 = axes[0, 1]
    density_eq = density[equil_start:]
    n, bins, patches = ax2.hist(density_eq, bins=50, density=True, 
                                 alpha=0.7, color='steelblue', edgecolor='black')
    x_fit = np.linspace(density_eq.min(), density_eq.max(), 200)
    y_fit = stats.norm.pdf(x_fit, stats['mean'], stats['std'])
    ax2.plot(x_fit, y_fit, 'r-', linewidth=2, label='Normal fit')
    
    # Add reference lines
    ax2.axvline(x=997, color='green', linestyle='--', 
                label='SPC/E reference (997 kg/m³)')
    ax2.axvline(x=997.047, color='blue', linestyle=':', 
                label='Experiment (997.047 kg/m³)')
    ax2.set_xlabel('Density (kg/m³)')
    ax2.set_ylabel('Probability Density')
    ax2.set_title(f'Density Distribution (Equilibrated)\n'
                  f'Mean: {stats["mean"]:.1f} ± {stats["sem"]:.1f} kg/m³')
    ax2.legend(fontsize=7)
    ax2.grid(True, alpha=0.3)
    
    # 3. Volume-based Density and Box Dimensions
    ax3 = axes[1, 0]
    if volume is not None:
        vol_density = calculate_density_from_volume(volume, n_molecules)
        ax3.plot(time, vol_density, 'b-', linewidth=0.5, alpha=0.7, 
                label='Volume-based density')
        ax3.axvline(x=time[equil_start], color='orange', linestyle=':')
        ax3.axhline(y=np.mean(vol_density[equil_start:]), color='red', 
                   linestyle='--', label=f"Mean: {np.mean(vol_density[equil_start:]):.1f}")
        ax3.set_ylabel('Density (kg/m³)')
    ax3.set_xlabel('Time (ps)')
    ax3.set_title('Density from Box Volume')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # 4. Running Average and Convergence
    ax4 = axes[1, 1]
    window = max(10, len(density_eq) // 100)
    running_avg = np.convolve(density_eq, np.ones(window)/window, mode='valid')
    running_time = time[equil_start + window - 1:]
    ax4.plot(running_time, running_avg, 'b-', linewidth=1, 
            label=f'Running average (window={window})')
    
    # Add cumulative average
    cumulative_avg = np.cumsum(density_eq) / np.arange(1, len(density_eq)+1)
    ax4.plot(time[equil_start:], cumulative_avg, 'r-', linewidth=1, 
            label='Cumulative average', alpha=0.7)
    ax4.axhline(y=stats['mean'], color='black', linestyle=':', 
                label=f'Final mean: {stats["mean"]:.1f}')
    ax4.set_xlabel('Time (ps)')
    ax4.set_ylabel('Density (kg/m³)')
    ax4.set_title('Density Convergence')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Additional: Block averaging plot
    fig2, (ax5, ax6) = plt.subplots(1, 2, figsize=(12, 5))
    
    block_sizes, block_sems = block_averaging(density_eq)
    ax5.plot(block_sizes, block_sems, 'b.-', markersize=8)
    ax5.set_xlabel('Block Size')
    ax5.set_ylabel('Standard Error of Mean (kg/m³)')
    ax5.set_title('Block Averaging Analysis')
    ax5.grid(True, alpha=0.3)
    
    ax6.plot(block_sizes, block_sems * block_sizes, 'r.-', markersize=8)
    ax6.set_xlabel('Block Size')
    ax6.set_ylabel('SEM × Block Size')
    ax6.set_title('Convergence Check (Plateau Indicates Convergence)')
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}_block_averaging.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Plots saved to '{output_prefix}.png' and '{output_prefix}_block_averaging.png'")

def print_density_report(stats, experimental_ref=997.047):
    """Print a formatted density validation report."""
    
    print("\n" + "="*75)
    print(" DENSITY ANALYSIS REPORT - SPC/E WATER AT 300 K, 1 BAR")
    print("="*75)
    
    print(f"\n{'Parameter':<45} {'Value':<25}")
    print("-"*75)
    print(f"{'Mean density':<45} {stats['mean']:>8.2f} kg/m³")
    print(f"{'Standard deviation':<45} {stats['std']:>8.2f} kg/m³")
    print(f"{'Standard error (block averaged)':<45} {stats['sem']:>8.3f} kg/m³")
    print(f"{'Relative standard deviation':<45} {stats['rel_std']:>8.4f} %")
    print(f"{'Minimum density':<45} {stats['min']:>8.2f} kg/m³")
    print(f"{'Maximum density':<45} {stats['max']:>8.2f} kg/m³")
    print(f"{'Density range':<45} {stats['max']-stats['min']:>8.2f} kg/m³")
    print(f"{'Drift per ns':<45} {stats['drift_per_ns']:>8.3f} kg/m³/ns")
    print(f"{'R² of linear fit':<45} {stats['r_squared']:>8.4f}")
    print(f"{'Normal distribution':<45} {'Yes' if stats['is_normal'] else 'No'}")
    print(f"{'D\'Agostino p-value':<45} {stats['normality_p']:>8.4f}")
    
    if stats['vol_density'] is not None:
        print(f"{'Volume-based density':<45} {stats['vol_density']:>8.2f} kg/m³")
    
    print(f"{'Equilibrated data points':<45} {stats['n_equilibrated']:>8d}")
    
    print("-"*75)
    
    # Comparison with references
    print(f"\n{'Comparison with Reference Values':^75}")
    print("-"*75)
    
    deviation_exp = stats['mean'] - experimental_ref
    deviation_pct_exp = (deviation_exp / experimental_ref) * 100
    
    print(f"{'Experimental water at 300K, 1 bar':<45} {experimental_ref:>8.3f} kg/m³")
    print(f"{'Simulation deviation from experiment':<45} {deviation_exp:>+8.2f} kg/m³ "
          f"({deviation_pct_exp:+.2f}%)")
    
    # SPC/E reference from literature
    spce_ref = 997.0
    deviation_spce = stats['mean'] - spce_ref
    deviation_pct_spce = (deviation_spce / spce_ref) * 100
    print(f"{'SPC/E literature reference':<45} {spce_ref:>8.1f} kg/m³")
    print(f"{'Simulation deviation from SPC/E ref':<45} {deviation_spce:>+8.2f} kg/m³ "
          f"({deviation_pct_spce:+.2f}%)")
    
    print("-"*75)
    
    # Validation checks
    print(f"\n{'Validation Checks':^75}")
    print("-"*75)
    
    checks = []
    
    # Check 1: Within 1% of experimental
    check1 = abs(deviation_pct_exp) < 1.0
    checks.append(check1)
    print(f"{'Within 1% of experiment (< 1% error)':<45} "
          f"{'✓ PASS' if check1 else '✗ FAIL'}")
    
    # Check 2: Within 2 kg/m³ of SPC/E reference
    check2 = abs(deviation_spce) < 2.0
    checks.append(check2)
    print(f"{'Within 2 kg/m³ of SPC/E reference':<45} "
          f"{'✓ PASS' if check2 else '✗ FAIL'}")
    
    # Check 3: SEM < 0.5 kg/m³
    check3 = stats['sem'] < 0.5
    checks.append(check3)
    print(f"{'Standard error < 0.5 kg/m³':<45} "
          f"{'✓ PASS' if check3 else '✗ FAIL'}")
    
    # Check 4: Drift < 0.5 kg/m³ per ns
    check4 = abs(stats['drift_per_ns']) < 0.5
    checks.append(check4)
    print(f"{'Density drift < 0.5 kg/m³/ns':<45} "
          f"{'✓ PASS' if check4 else '✗ FAIL'}")
    
    # Check 5: Normal distribution
    check5 = stats['is_normal']
    checks.append(check5)
    print(f"{'Normal distribution of density':<45} "
          f"{'✓ PASS' if check5 else '✗ FAIL'}")
    
    print("-"*75)
    print(f"{'OVERALL STATUS':<45} "
          f"{'✓ PASS' if all(checks) else '✗ FAIL'} "
          f"({sum(checks)}/{len(checks)} checks passed)")
    print("="*75 + "\n")
    
    return all(checks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze density of GROMACS water simulation')
    parser.add_argument('-d', '--density-file', required=True,
                       help='Density XVG file from gmx energy')
    parser.add_argument('-v', '--volume-file', 
                       help='Volume XVG file (optional)')
    parser.add_argument('-n', '--n-molecules', type=int, default=216,
                       help='Number of water molecules')
    parser.add_argument('-o', '--output', default='density_analysis',
                       help='Output prefix for plots')
    
    args = parser.parse_args()
    
    print(f"\nReading density data from: {args.density_file}")
    time, density = read_xvg(args.density_file)
    print(f"Loaded {len(density)} density data points")
    print(f"Time range: {time[0]:.1f} to {time[-1]:.1f} ps")
    
    volume = None
    if args.volume_file and os.path.exists(args.volume_file):
        print(f"Reading volume data from: {args.volume_file}")
        _, volume = read_xvg(args.volume_file)
    
    print(f"Number of water molecules: {args.n_molecules}")
    
    print("\nComputing statistics...")
    stats = compute_detailed_statistics(time, density, volume, args.n_molecules)
    
    print_density_report(stats)
    
    print("Generating plots...")
    plot_density_analysis(time, density, volume, args.n_molecules, 
                          stats, args.output)
```

### 6.4 Run the Density Analysis

```bash
# Make script executable
chmod +x analyze_density.py

# Run analysis with volume-based calculation
python3 analyze_density.py \
    -d density_prod.xvg \
    -v volume_prod.xvg \
    -n 216 \
    -o density_analysis
```

---

## 7. Alternative: Manual Density Calculation from Box Dimensions

```bash
# Extract box dimensions over time
gmx energy -f md.edr -o box.xvg <<< "Box-X Box-Y Box-Z"

# Calculate density manually
python3 << 'EOF'
import numpy as np

# Read box dimensions
data = np.loadtxt('box.xvg', comments=('#', '@'))
time = data[:, 0]
box_x = data[:, 1]  # nm
box_y = data[:, 2]  # nm
box_z = data[:, 3]  # nm

# Constants
NA = 6.02214076e23
MW = 18.0153  # g/mol
N_molecules = 216

# Calculate volume and density
volume = box_x * box_y * box_z  # nm³
mass_per_molecule = MW / (NA * 1000)  # kg
total_mass = N_molecules * mass_per_molecule  # kg
density = total_mass / (volume * 1e-27)  # kg/m³

# Statistics (use second half for equilibration)
n_half = len(density) // 2
density_eq = density[n_half:]
mean_density = np.mean(density_eq)
std_density = np.std(density_eq, ddof=1)
sem_density = std_density / np.sqrt(len(density_eq))

print(f"\nDensity from box dimensions:")
print(f"  Mean: {mean_density:.2f} kg/m³")
print(f"  Std:  {std_density:.2f} kg/m³")
print(f"  SEM:  {sem_density:.3f} kg/m³")
print(f"  Box size (mean): {np.mean(box_x[n_half:]):.4f} nm")
EOF
```

---

## 8. Quick One-Line Density Extraction

```bash
# Extract mean density and error from energy file
gmx energy -f md.edr -o density.xvg <<< "Density" 2>&1 | grep -A 10 "Energy Average"

# Quick statistics from XVG file
grep -v "^[#@]" density_prod.xvg | awk 'NR>250 {
    sum+=$2; sumsq+=$2*$2; n++}
    END {
        mean=sum/n; 
        std=sqrt(sumsq/n - mean*mean);
        printf "Density: %.2f ± %.3f kg/m³ (from %d points)\n", mean, std/n, n
    }'
```

---

## 9. Expected Output Files

| File | Description |
|------|-------------|
| `conf.gro` | Initial configuration |
| `topol.top` | System topology |
| `em.gro`, `em.edr`, `em.log` | Energy minimization |
| `nvt.gro`, `nvt.edr`, `nvt.log` | NVT equilibration |
| `npt.gro`, `npt.edr`, `npt.log` | NPT equilibration |
| `md.gro`, `md.xtc`, `md.edr`, `md.log`, `md.cpt` | Production MD |
| `density_prod.xvg` | Density time series from production |
| `volume_prod.xvg` | Volume time series |
| `density_statistics.txt` | Basic statistics from gmx analyze |
| `density_analysis.png` | Comprehensive analysis plots |
| `density_analysis_block_averaging.png` | Block averaging convergence plots |

---

## 10. Expected Results and Validation

### 10.1 Expected Density Values

| Water Model | Expected Density at 300K, 1bar (kg/m³) | Reference |
|-------------|----------------------------------------|-----------|
| Experiment | 997.047 | NIST |
| SPC/E | 997 ± 2 | Mark & Nilsson (2001) |
| TIP3P | ~985 | Jorgensen et al. (1983) |
| TIP4P/2005 | 997 ± 1 | Abascal & Vega (2005) |
| OPC | 997 ± 1 | Izadi et al. (2014) |

### 10.2 Validation Criteria

| Parameter | Criterion | Importance |
|-----------|-----------|------------|
| Mean density | 995–999 kg/m³ for SPC/E | Critical |
| Standard error | < 0.5 kg/m³ | High |
| Density drift | < 0.5 kg/m³/ns | High |
| Relative std dev | < 0.5% | Medium |
| Normality of distribution | p > 0.01 | Medium |
| Box size isotropy | All dimensions within 0.5% of each other | Medium |

### 10.3 Check NPT Equilibration Quality

```bash
# Plot density evolution during NPT to verify equilibration
python3 << 'EOF'
import numpy as np
import matplotlib.pyplot as plt

# Read NPT density
data_npt = np.loadtxt('density_npt.xvg', comments=('#', '@'))
time_npt = data_npt[:, 0]
density_npt = data_npt[:, 1]

# Read production density
data_prod = np.loadtxt('density_prod.xvg', comments=('#', '@'))
time_prod = data_prod[:, 0] + time_npt[-1]
density_prod = data_prod[:, 1]

# Plot combined
plt.figure(figsize=(10, 5))
plt.plot(time_npt, density_npt, 'b-', alpha=0.5, label='NPT equilibration')
plt.plot(time_prod, density_prod, 'r-', alpha=0.5, label='Production')
plt.axhline(y=997, color='green', linestyle='--', label='Target (997 kg/m³)')
plt.xlabel('Time (ps)')
plt.ylabel('Density (kg/m³)')
plt.title('Density Equilibration Check')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('density_equilibration.png', dpi=150)
print("Density equilibration plot saved.")
EOF
```

---

## 11. Common Possible Errors and Solutions

### 11.1 Setup Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Molecule type 'SOL' not found` | Wrong residue name in topology | Use `SOL` not `SOL`; check `.itp` file |
| `System has non-zero total charge` | Wrong number of waters | SPC/E has zero charge; verify molecule count |
| `Atoms xx and yy in constraint have the same mass` | Wrong water model topology | Use `#include "spce.ff/spce.itp"` |
| `The cut-off length is longer than half the shortest box vector` | Box too small | Use box > 2× rlist (minimum 2.1 nm) |

### 11.2 Density-Specific Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Density too low (< 950 kg/m³) | Missing dispersion correction | Add `DispCorr = EnerPres` to MDP |
| Density too low (~980 kg/m³) | Incorrect water model (TIP3P) | TIP3P naturally gives lower density; use SPC/E or TIP4P |
| Density too high (> 1020 kg/m³) | Pressure coupling too strong | Increase `tau_p` to 2.0–5.0 ps |
| Density fluctuating wildly | Small box, poor statistics | Use at least 500–1000 water molecules |
| Density drifts continuously | NPT equilibration incomplete | Extend NPT to 500 ps–1 ns |
| Density from energy ≠ from volume | PME/constraint energy contribution | Both should agree within 0.1%; use volume-based for accuracy |
| Box becomes non-cubic | Anisotropic pressure coupling | Use `pcoupltype = isotropic` |

### 11.3 Runtime Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Pressure scaling more than 1%` | Large pressure fluctuations | Normal in small systems; ignore if density is stable |
| `Water molecule cannot be settled` | Bad initial geometry | Extend EM; use `gmx solvate` properly |
| `LINCS warnings: rmsd exceeds` | Constraint failures | Reduce timestep to 1.5 fs; verify topology |
| `Segmentation fault in mdrun` | Memory/GPU issue | Use `-ntmpi 1` or fewer threads |

---

## 12. Complete Automated Density Workflow Script

Save as `run_density_calculation.sh`:

```bash
#!/bin/bash
# Complete GROMACS density calculation workflow for SPC/E water
set -e

# Configuration
BOX_SIZE=5.0          # nm
N_STEPS_NPT=100000    # 200 ps equilibration
N_STEPS_MD=2500000    # 5 ns production
TARGET_TEMP=300       # K
TARGET_PRESS=1.0      # bar

echo "=========================================="
echo " SPC/E Water Density Calculation"
echo "=========================================="
echo "Box size: ${BOX_SIZE} nm"
echo "Production: $((N_STEPS_MD * 2 / 1000)) ns"
echo ""

# Step 1: Generate system
echo "[1/7] Generating water box..."
gmx solvate -cs spc216.gro -o conf.gro -box ${BOX_SIZE} ${BOX_SIZE} ${BOX_SIZE} \
    -maxsol 10000

N_WATER=$(grep -c "OW\|HW" conf.gro)
N_WATER=$((N_WATER / 3))
echo "  Generated box with ${N_WATER} water molecules"

# Update topology
cat > topol.top << EOF
#include "spce.ff/forcefield.itp"
#include "spce.ff/spce.itp"

[ system ]
SPC/E Water Density Calculation

[ molecules ]
SOL              ${N_WATER}
EOF

# Step 2: Energy minimization
echo "[2/7] Energy minimization..."
gmx grompp -f em.mdp -c conf.gro -p topol.top -o em.tpr -maxwarn 1
gmx mdrun -deffnm em -v -ntmpi 1

# Step 3: NVT equilibration
echo "[3/7] NVT equilibration..."
gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr -maxwarn 1
gmx mdrun -deffnm nvt -v -ntmpi 1

# Step 4: NPT equilibration
echo "[4/7] NPT equilibration..."
gmx grompp -f npt.mdp -c nvt.gro -p topol.top -o npt.tpr -maxwarn 1
gmx mdrun -deffnm npt -v -ntmpi 1

# Step 5: Production MD
echo "[5/7] Production MD..."
gmx grompp -f md.mdp -c npt.gro -p topol.top -o md.tpr -maxwarn 1
gmx mdrun -deffnm md -v -ntmpi 1

# Step 6: Extract density
echo "[6/7] Extracting density..."
gmx energy -f md.edr -o density_prod.xvg <<< "Density"
gmx energy -f md.edr -o volume_prod.xvg <<< "Volume"

# Step 7: Quick analysis
echo "[7/7] Quick density analysis..."
grep -v "^[#@]" density_prod.xvg | awk 'NR>250 {
    sum+=$2; sumsq+=$2*$2; n++}
    END {
        mean=sum/n;
        std=sqrt(sumsq/n - mean*mean);
        sem=std/sqrt(n);
        printf "\n  Final Density: %.2f ± %.3f kg/m³\n", mean, sem
        printf "  (from %d points after equilibration)\n\n", n
    }'

echo "=========================================="
echo " Workflow complete!"
echo "=========================================="
echo "Output files:"
ls -lh density_*.* md.edr md.log 2>/dev/null
echo ""
echo "For detailed analysis, run:"
echo "  python3 analyze_density.py -d density_prod.xvg -v volume_prod.xvg -n ${N_WATER}"
```

Run the complete workflow:
```bash
chmod +x run_density_calculation.sh
./run_density_calculation.sh
```

---

## 13. Density Comparison Across Water Models

If you want to compare multiple water models, here's a template for TIP3P:

```bash
# For TIP3P water
cat > topol_tip3p.top << 'EOF'
#include "oplsaa.ff/forcefield.itp"
#include "oplsaa.ff/tip3p.itp"

[ system ]
TIP3P Water

[ molecules ]
SOL             216
EOF

# Use the same MDP files but expect density around 985 kg/m³
# Note: TIP3P is known to underestimate water density at 300K
```

---

## 14. Key Validation Notes

1. **Dispersion Correction is Critical:** Without `DispCorr = EnerPres`, SPC/E density is ~15-20 kg/m³ too low. This is the most common cause of density errors.

2. **Equilibration Time:** Density converges slower than temperature. Always check the density time series for drift before analysis. A minimum of 200 ps NPT equilibration is recommended.

3. **System Size Effects:** Small systems (<500 molecules) show larger fluctuations but mean density should be accurate. For publication, use ≥1000 molecules.

4. **Pressure Coupling Algorithm:** Parrinello-Rahman gives better density convergence than Berendsen for production. Use Berendsen only for initial equilibration.

5. **Cutoff Effects:** Using a 0.9 nm cutoff (rather than 1.0 nm) can shift density by 1-2 kg/m³. Be consistent with force field recommendations.

6. **Timestep Sensitivity:** Using 2.5 fs timestep can affect density by 1-2 kg/m³ compared to 2.0 fs due to discretization errors in the barostat.

7. **Box Shape:** For density calculations, use cubic boxes. Anisotropic boxes can develop shape fluctuations that affect density measurements.

8. **Temperature Dependence:** The density of SPC/E water at different temperatures:
   - 280 K: ~1000 kg/m³
   - 300 K: ~997 kg/m³
   - 320 K: ~988 kg/m³
   - Maximum density occurs at ~250 K for SPC/E (actual water: 277 K)


