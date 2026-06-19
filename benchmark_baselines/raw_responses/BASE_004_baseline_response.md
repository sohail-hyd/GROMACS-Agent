Here is a complete, reproducible GROMACS workflow to calculate the mean-square displacement (MSD) and self-diffusion coefficient (D) of pure SPC/E water at 300 K.

---

## 1. Theoretical Background

The self-diffusion coefficient D is obtained from the Einstein relation:

$$D = \frac{1}{6} \lim_{t \to \infty} \frac{d}{dt} \langle |\mathbf{r}(t) - \mathbf{r}(0)|^2 \rangle$$

Where:
- $\langle |\mathbf{r}(t) - \mathbf{r}(0)|^2 \rangle$ is the mean-square displacement (MSD)
- The factor 1/6 comes from the three-dimensional isotropic diffusion (2 × d dimensions = 2 × 3 = 6)
- The limit $t \to \infty$ represents the diffusive regime

**Expected D for SPC/E water at 300 K:** 2.4–2.8 × 10⁻⁵ cm²/s (0.24–0.28 Å²/ps)

**Critical requirements for accurate D:**
- Unwrapped trajectories (no PBC jumps)
- Long simulation time (≥10 ns, preferably 50–100 ns)
- Proper treatment of the ballistic-to-diffusive crossover
- System size correction for small boxes

---

## 2. Directory Setup and Prerequisites

```bash
# Create working directory
mkdir -p ~/water_diffusion_calc
cd ~/water_diffusion_calc

# Assumes you have completed the previous density workflow with:
# - md.xtc (compressed trajectory)
# - md.tpr (topology/run input)
# - md.edr (energy file)
# - md.gro (final configuration)
# - topol.top (topology)
```

If starting fresh, first run the density workflow from the previous response to generate the trajectory.

---

## 3. Trajectory Preprocessing

### 3.1 Critical Step: Remove Periodic Boundary Conditions (PBC)

MSD calculation **requires unwrapped trajectories** where molecules diffuse continuously without jumping across box boundaries.

```bash
# Check current trajectory settings
gmx check -f md.xtc 2>&1 | grep -E "xtc|Precision|atoms"

# Create an index file for water oxygens (OW atoms only)
gmx make_ndx -f md.tpr -o index.ndx << EOF
a OW
name 18 OW_only
q
EOF

# Remove PBC: Unwrap entire system (molecules kept whole)
gmx trjconv -f md.xtc -s md.tpr -o md_noPBC.xtc -pbc mol -center << EOF
System
System
EOF

# Alternative: Extract only OW atoms and unwrap
gmx trjconv -f md.xtc -s md.tpr -n index.ndx -o md_OW_noPBC.xtc -pbc nojump << EOF
OW_only
EOF
```

**Explanation of PBC removal options:**
- `-pbc mol`: Makes molecules whole (puts atoms of each molecule together), then centers the system
- `-pbc nojump`: Removes jumps of atoms across the box (best for MSD)
- `-center`: Centers the system in the box (optional for visualization)

### 3.2 Verify Unwrapping Quality

```bash
# Check one molecule's trajectory to verify unwrapping
gmx traj -f md_noPBC.xtc -s md.tpr -n index.ndx -ox oW_trajectory.xvg << EOF
OW_only
EOF

# Quick check: plot x-coordinate of first OW atom over time
python3 << 'EOF'
import numpy as np
import matplotlib.pyplot as plt

# Read the OW trajectory (each row is time, columns are x,y,z for each atom)
# For a quick check, use gmx traj output or parse xvg
data = np.loadtxt('oW_trajectory.xvg', comments=('#', '@'))
time = data[:, 0]
x_coord = data[:, 1]  # x-coordinate of first OW atom

plt.figure(figsize=(12, 4))
plt.plot(time, x_coord, 'b-', linewidth=0.5)
plt.xlabel('Time (ps)')
plt.ylabel('X coordinate (nm)')
plt.title('X-coordinate of First OW Atom (Unwrapped Trajectory)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('unwrapping_check.png', dpi=150)
print("Unwrapping check plot saved.")
print(f"X range: {x_coord.min():.2f} to {x_coord.max():.2f} nm")
print("If X range >> box size, unwrapping is successful.")
EOF
```

### 3.3 Center Trajectory (Optional but Recommended)

```bash
# Center the system to remove COM drift
gmx trjconv -f md_noPBC.xtc -s md.tpr -o md_centered.xtc -pbc mol -center -ur compact << EOF
System
System
EOF
```

---

## 4. MDP File for Production MD (Optimized for Diffusion)

If running a new simulation specifically for diffusion, use these settings:

```bash
cat > md_diffusion.mdp << 'EOF'
; Production MD optimized for diffusion coefficient calculation
integrator          = md
nsteps              = 50000000       ; 100 ns (longer is better for diffusion)
dt                  = 0.002

; Output - save frequently for good MSD statistics
nstxout             = 0              ; No uncompressed output
nstvout             = 0
nstenergy           = 1000
nstlog              = 5000
nstxout-compressed  = 100            ; Save every 0.2 ps for MSD analysis
compressed-x-grps   = System

; Neighbor searching
cutoff-scheme       = Verlet
nstlist             = 20             ; Update every 40 fs
ns-type             = grid
pbc                 = xyz
rlist               = 1.0
verlet-buffer-tolerance = 0.005

; Electrostatics
coulombtype         = PME
rcoulomb            = 1.0
fourierspacing      = 0.12
pme-order           = 4

; Van der Waals
vdwtype             = Cut-off
rvdw                = 1.0
DispCorr            = EnerPres

; Temperature coupling (Nose-Hoover is more rigorous for dynamics)
tcoupl              = Nose-Hoover
tc-grps             = System
tau_t               = 1.0            ; Longer coupling time preserves dynamics better
ref_t               = 300

; Pressure coupling
pcoupl              = Parrinello-Rahman
pcoupltype          = isotropic
tau_p               = 5.0            ; Longer coupling time for better dynamics
ref_p               = 1.0
compressibility     = 4.5e-5

; Constraints (SETTLE for rigid water)
constraints         = h-bonds
constraint-algorithm = LINCS
lincs-order         = 4
lincs-iter          = 1

; Continue from previous simulation
gen_vel             = no

; Important: Use v-rescale for NVT, Nose-Hoover for production
; Nose-Hoover gives more accurate dynamics than v-rescale
EOF
```

**Note on thermostats for diffusion:**
- **V-rescale:** Robust but can perturb dynamics; acceptable for density, not ideal for diffusion
- **Nose-Hoover:** Better preserves dynamics; recommended for diffusion calculations
- **No thermostat (NVE):** Ideal for dynamics but requires perfect equilibration; use only for short test runs

---

## 5. MSD Calculation Methods

### 5.1 Standard GROMACS MSD Calculation

```bash
# Calculate MSD for all OW atoms
# -tref: set the refresh time for restart (0 = no refresh)
# -beginfit/-endfit: fitting range for diffusion coefficient
gmx msd -f md_noPBC.xtc -s md.tpr -n index.ndx -o msd.xvg -mol diff_COM.xvg \
    -beginfit 10 -endfit 100 << EOF
OW_only
EOF
```

**Interactive note:** The program will ask for a group; provide `OW_only` (or group number).

### 5.2 MSD with Better Control and Multiple Time Origins

```bash
# Use the -trestart option for multiple time origins (better statistics)
gmx msd -f md_noPBC.xtc -s md.tpr -n index.ndx -o msd_multi.xvg \
    -mol diff_multi.xvg -trestart 10 -beginfit 10 -endfit 50 << EOF
OW_only
EOF
```

### 5.3 Extract MSD for Individual Molecules (Custom Approach)

GROMACS `msd` tool averages over all molecules. For error analysis, we need per-molecule MSD:

```bash
# Extract individual OW trajectories using gmx traj
# Create index groups for each molecule (practical for small systems)
python3 << 'EOF'
import numpy as np

# For a 216-water system, create index file entries
with open('index_molecules.ndx', 'w') as f:
    for i in range(1, 217):  # 216 waters
        atom_num = (i - 1) * 3 + 1  # OW is first atom of each water
        f.write(f'[ Mol_{i} ]\n')
        f.write(f'{atom_num}\n')
EOF
```

---

## 6. Comprehensive Python MSD Analysis Pipeline

Create `calculate_diffusion.py`:

```python
#!/usr/bin/env python3
"""
Complete diffusion coefficient analysis from GROMACS trajectory.
Handles MSD calculation, fitting, error estimation, and system-size correction.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats, optimize
import MDAnalysis as mda
from MDAnalysis.analysis import msd as msd_analysis
import argparse
import warnings
warnings.filterwarnings('ignore')

def calculate_msd_mdanalysis(topology, trajectory, atom_sel='name OW', 
                              dt=0.002, n_blocks=5):
    """
    Calculate MSD using MDAnalysis with proper PBC handling.
    Returns time array and MSD with error estimates.
    """
    u = mda.Universe(topology, trajectory)
    oxygens = u.select_atoms(atom_sel)
    n_oxygens = len(oxygens)
    
    print(f"Calculating MSD for {n_oxygens} oxygen atoms...")
    
    # Use MDAnalysis MSD analysis with unwrapping
    msd_calculator = msd_analysis.EinsteinMSD(
        oxygens,
        select='all',
        msd_type='xyz',
        fft=True  # Use FFT for faster calculation
    )
    
    msd_calculator.run()
    
    # Get results
    time = np.arange(msd_calculator.n_frames) * msd_calculator.dt
    msd = msd_calculator.results.msd_by_particle  # Shape: (n_particles, n_frames)
    
    # Average over all particles
    msd_mean = np.mean(msd, axis=0)
    msd_std = np.std(msd, axis=0, ddof=1)
    msd_sem = msd_std / np.sqrt(n_oxygens)
    
    return time, msd_mean, msd_sem, msd

def calculate_msd_manual(xtc_file, tpr_file, ndx_group='OW_only',
                         dt=0.002, stride=1):
    """
    Alternative: Calculate MSD using GROMACS output parsing.
    """
    import subprocess
    import tempfile
    import os
    
    # Run gmx msd with multiple time origins
    with tempfile.NamedTemporaryFile(suffix='.xvg', delete=False) as tmp:
        tmp_xvg = tmp.name
    
    cmd = f"echo '{ndx_group}' | gmx msd -f {xtc_file} -s {tpr_file} " \
          f"-o {tmp_xvg} -trestart 10 -beginfit 10 -endfit 50"
    
    subprocess.run(cmd, shell=True, capture_output=True)
    
    # Parse XVG file
    data = np.loadtxt(tmp_xvg, comments=('#', '@'))
    os.unlink(tmp_xvg)
    
    time = data[:, 0]  # ps
    msd = data[:, 1]   # nm²
    
    return time, msd, None, None

def fit_diffusion_coefficient(time, msd, msd_sem=None, 
                               fit_start=10, fit_end=100,
                               method='linear'):
    """
    Fit MSD to obtain diffusion coefficient.
    
    D = (1/6) * d(MSD)/dt   [in nm²/ps]
    
    Methods:
    - 'linear': Weighted linear fit (MSD = 6Dt + intercept)
    - 'log-log': Fit log(MSD) vs log(t) to find diffusive regime first
    """
    
    # Convert to appropriate units
    # time in ps, MSD in nm²
    
    # Select fitting range
    mask = (time >= fit_start) & (time <= fit_end)
    t_fit = time[mask]
    msd_fit = msd[mask]
    
    if len(t_fit) < 10:
        raise ValueError(f"Too few points in fitting range: {len(t_fit)}")
    
    if method == 'linear':
        # Weighted linear fit
        if msd_sem is not None:
            weights = 1.0 / msd_sem[mask]
            weights = weights / np.sum(weights) * len(weights)
        else:
            weights = None
        
        # MSD = slope * t + intercept
        if weights is not None:
            slope, intercept, r_value, p_value, std_err = \
                stats.linregress(t_fit, msd_fit)
            # For weighted fit
            coeffs = np.polyfit(t_fit, msd_fit, 1, w=weights)
        else:
            slope, intercept, r_value, p_value, std_err = \
                stats.linregress(t_fit, msd_fit)
            coeffs = [slope, intercept]
        
        D = coeffs[0] / 6.0  # nm²/ps
        D_cm2_s = D * 1e-2    # Convert: 1 nm²/ps = 1e-2 cm²/s
        D_fit_quality = r_value**2 if 'r_value' in locals() else 1.0
        
        return {
            'D_nm2_ps': D,
            'D_cm2_s': D_cm2_s,
            'slope': coeffs[0],
            'intercept': coeffs[1],
            'r_squared': D_fit_quality,
            'fit_start': fit_start,
            'fit_end': fit_end,
            'n_points': len(t_fit)
        }
    
    elif method == 'log-log':
        # Find diffusive regime: slope of log(MSD) vs log(t) should be ~1
        log_t = np.log10(time[1:])  # Skip t=0
        log_msd = np.log10(msd[1:])
        
        # Calculate local slope
        window = max(5, len(log_t) // 20)
        slopes = []
        for i in range(len(log_t) - window):
            slope, _, _, _, _ = stats.linregress(log_t[i:i+window], 
                                                  log_msd[i:i+window])
            slopes.append(slope)
        slopes = np.array(slopes)
        slopes_time = time[1 + window//2:len(slopes) + 1 + window//2]
        
        # Find where slope ≈ 1 (diffusive regime)
        diffusive_mask = np.abs(slopes - 1.0) < 0.1
        if np.any(diffusive_mask):
            diff_start = slopes_time[diffusive_mask][0]
            diff_end = slopes_time[diffusive_mask][-1]
            print(f"  Auto-detected diffusive regime: {diff_start:.1f}-{diff_end:.1f} ps")
        else:
            diff_start, diff_end = fit_start, fit_end
            print(f"  Warning: Could not auto-detect diffusive regime")
        
        return fit_diffusion_coefficient(time, msd, msd_sem, 
                                         diff_start, diff_end, 'linear')

def block_error_analysis(time, msd_particles, n_blocks=5, 
                         fit_start=10, fit_end=100):
    """
    Estimate D error using block averaging over molecules.
    """
    n_particles = msd_particles.shape[0]
    block_size = n_particles // n_blocks
    
    D_values = []
    for i in range(n_blocks):
        start_idx = i * block_size
        end_idx = (i + 1) * block_size if i < n_blocks - 1 else n_particles
        block_msd = np.mean(msd_particles[start_idx:end_idx], axis=0)
        fit = fit_diffusion_coefficient(time, block_msd, None, 
                                        fit_start, fit_end, 'linear')
        D_values.append(fit['D_cm2_s'])
    
    D_values = np.array(D_values)
    D_mean = np.mean(D_values)
    D_std = np.std(D_values, ddof=1)
    D_sem = D_std / np.sqrt(n_blocks)
    
    return D_mean, D_sem, D_values

def system_size_correction(D_sim, L_box, T=300, eta=0.85e-3):
    """
    Apply Yeh-Hummer system-size correction for diffusion.
    
    D_infinity = D_sim + (k_B * T) / (6 * pi * eta * L)
    
    Where:
    - k_B = 1.380649e-23 J/K
    - T = temperature in K
    - eta = viscosity in Pa·s (~0.85e-3 for SPC/E at 300K)
    - L = box length in meters
    
    Reference: Yeh & Hummer, J. Phys. Chem. B 108, 15873 (2004)
    """
    kB = 1.380649e-23  # J/K
    correction = (kB * T) / (6 * np.pi * eta * L_box)
    correction_cm2_s = correction * 1e4  # Convert m²/s to cm²/s
    D_corrected = D_sim + correction_cm2_s
    
    return D_corrected, correction_cm2_s

def plot_msd_analysis(time, msd, msd_sem, fit_results, D_blocks=None,
                       output_prefix='msd_analysis'):
    """Generate comprehensive MSD analysis plots."""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. MSD vs Time (full)
    ax1 = axes[0, 0]
    ax1.plot(time, msd, 'b-', linewidth=1.5, label='MSD (all O atoms)')
    if msd_sem is not None:
        ax1.fill_between(time[::10], 
                         (msd - msd_sem)[::10], 
                         (msd + msd_sem)[::10],
                         alpha=0.3, color='blue', label='± SEM')
    
    # Fit line
    t_fit = np.array([fit_results['fit_start'], fit_results['fit_end']])
    msd_fit = fit_results['slope'] * t_fit + fit_results['intercept']
    ax1.plot(t_fit, msd_fit, 'r--', linewidth=2, 
             label=f'Linear fit ({fit_results["fit_start"]}-{fit_results["fit_end"]} ps)')
    
    # Ballistic line (slope = 2 on log-log)
    ax1.plot([0, 1], [0, 0.01], 'g:', linewidth=1, alpha=0.5, label='Ballistic (slope=2)')
    
    ax1.set_xlabel('Time (ps)')
    ax1.set_ylabel('MSD (nm²)')
    ax1.set_title(f'Mean-Square Displacement\n'
                  f'D = {fit_results["D_cm2_s"]:.3f} × 10⁻⁵ cm²/s')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 2. Log-Log Plot
    ax2 = axes[0, 1]
    mask_positive = time > 0
    ax2.loglog(time[mask_positive], msd[mask_positive], 'b-', linewidth=1.5)
    ax2.loglog(time[mask_positive], 0.01 * time[mask_positive]**1.0, 
               'r--', linewidth=1, alpha=0.7, label='~t¹ (Diffusive)')
    ax2.loglog(time[mask_positive], 0.1 * time[mask_positive]**2.0, 
               'g:', linewidth=1, alpha=0.7, label='~t² (Ballistic)')
    ax2.axvline(x=fit_results['fit_start'], color='orange', 
                linestyle=':', alpha=0.7, label=f'Fit start ({fit_results["fit_start"]} ps)')
    ax2.axvline(x=fit_results['fit_end'], color='red', 
                linestyle=':', alpha=0.7, label=f'Fit end ({fit_results["fit_end"]} ps)')
    ax2.set_xlabel('Time (ps)')
    ax2.set_ylabel('MSD (nm²)')
    ax2.set_title('Log-Log MSD: Ballistic to Diffusive Crossover')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3, which='both')
    
    # 3. Time-dependent Diffusion Coefficient
    ax3 = axes[1, 0]
    D_t = np.zeros_like(time[1:])
    for i in range(1, len(time)):
        if time[i] > 1.0:  # Avoid t=0 singularity
            D_t[i] = msd[i] / (6.0 * time[i]) * 1e-2  # cm²/s
    ax3.plot(time[1:], D_t, 'b-', linewidth=1)
    ax3.axhline(y=fit_results['D_cm2_s'], color='r', linestyle='--',
                label=f'Fitted D = {fit_results["D_cm2_s"]:.3f} × 10⁻⁵ cm²/s')
    ax3.axvline(x=fit_results['fit_start'], color='orange', linestyle=':')
    ax3.axvline(x=fit_results['fit_end'], color='red', linestyle=':')
    ax3.set_xlabel('Time (ps)')
    ax3.set_ylabel('D(t) = MSD/6t (10⁻⁵ cm²/s)')
    ax3.set_title('Time-Dependent Diffusion Coefficient')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    # 4. Block Analysis or Residuals
    ax4 = axes[1, 1]
    if D_blocks is not None:
        ax4.bar(range(len(D_blocks)), D_blocks, color='steelblue', 
               alpha=0.7, edgecolor='black')
        ax4.axhline(y=np.mean(D_blocks), color='red', linestyle='-',
                   label=f'Mean D = {np.mean(D_blocks):.3f} ± {np.std(D_blocks, ddof=1)/np.sqrt(len(D_blocks)):.3f}')
        ax4.axhline(y=2.4, color='green', linestyle='--', label='SPC/E ref (2.4)')
        ax4.axhline(y=2.3, color='blue', linestyle=':', label='Experiment (2.30)')
        ax4.set_xlabel('Block Number')
        ax4.set_ylabel('D (10⁻⁵ cm²/s)')
        ax4.set_title(f'Block Error Analysis ({len(D_blocks)} blocks)')
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)
    else:
        # Plot MSD residuals from fit
        mask_fit = (time >= fit_results['fit_start']) & (time <= fit_results['fit_end'])
        msd_predicted = fit_results['slope'] * time[mask_fit] + fit_results['intercept']
        residuals = msd[mask_fit] - msd_predicted
        ax4.scatter(time[mask_fit], residuals, s=20, alpha=0.6)
        ax4.axhline(y=0, color='red', linestyle='--')
        ax4.set_xlabel('Time (ps)')
        ax4.set_ylabel('Residuals (nm²)')
        ax4.set_title(f'Fit Residuals (R² = {fit_results["r_squared"]:.4f})')
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Plots saved to '{output_prefix}.png'")

def print_diffusion_report(fit_results, D_blocks=None, system_correction=None):
    """Print formatted diffusion analysis report."""
    
    print("\n" + "="*70)
    print(" DIFFUSION COEFFICIENT ANALYSIS - SPC/E WATER AT 300 K")
    print("="*70)
    
    print(f"\n{'Fitting Parameters':^70}")
    print("-"*70)
    print(f"  Fitting range: {fit_results['fit_start']:.0f} - {fit_results['fit_end']:.0f} ps")
    print(f"  Number of points: {fit_results['n_points']}")
    print(f"  R² of linear fit: {fit_results['r_squared']:.6f}")
    
    print(f"\n{'Diffusion Coefficient':^70}")
    print("-"*70)
    print(f"  D = {fit_results['D_cm2_s']:.4f} × 10⁻⁵ cm²/s")
    print(f"  D = {fit_results['D_nm2_ps']:.6f} nm²/ps")
    
    if D_blocks is not None:
        D_mean = np.mean(D_blocks)
        D_std = np.std(D_blocks, ddof=1)
        D_sem = D_std / np.sqrt(len(D_blocks))
        print(f"\n{'Block Error Analysis':^70}")
        print("-"*70)
        print(f"  D (block avg) = {D_mean:.4f} × 10⁻⁵ cm²/s")
        print(f"  Std deviation = {D_std:.4f} × 10⁻⁵ cm²/s")
        print(f"  Standard error = {D_sem:.4f} × 10⁻⁵ cm²/s")
        print(f"  Number of blocks: {len(D_blocks)}")
        print(f"  Individual blocks: {', '.join([f'{d:.3f}' for d in D_blocks])}")
    
    if system_correction is not None:
        D_corr, correction = system_correction
        print(f"\n{'System Size Correction (Yeh-Hummer)':^70}")
        print("-"*70)
        print(f"  Raw D: {fit_results['D_cm2_s']:.4f} × 10⁻⁵ cm²/s")
        print(f"  Correction: +{correction:.4f} × 10⁻⁵ cm²/s")
        print(f"  Corrected D: {D_corr:.4f} × 10⁻⁵ cm²/s")
    
    print(f"\n{'Comparison with Reference Values':^70}")
    print("-"*70)
    print(f"  SPC/E literature:  2.40 × 10⁻⁵ cm²/s (Mark & Nilsson, 2001)")
    print(f"  SPC/E literature:  2.49 × 10⁻⁵ cm²/s (Mahoney & Jorgensen, 2001)")
    print(f"  Experiment (300K): 2.30 × 10⁻⁵ cm²/s (Krynicki et al., 1978)")
    print(f"  TIP3P literature:  5.06 × 10⁻⁵ cm²/s (much too fast)")
    print(f"  TIP4P/2005:        2.08 × 10⁻⁵ cm²/s")
    
    deviation = (fit_results['D_cm2_s'] - 2.40) / 2.40 * 100
    print(f"\n  Deviation from SPC/E reference: {deviation:+.1f}%")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Calculate diffusion coefficient from GROMACS trajectory')
    parser.add_argument('-f', '--trajectory', required=True,
                       help='Unwrapped trajectory file (xtc)')
    parser.add_argument('-s', '--topology', required=True,
                       help='Topology/TPR file')
    parser.add_argument('--fit-start', type=float, default=10,
                       help='Start time for linear fit (ps)')
    parser.add_argument('--fit-end', type=float, default=100,
                       help='End time for linear fit (ps)')
    parser.add_argument('--n-blocks', type=int, default=5,
                       help='Number of blocks for error analysis')
    parser.add_argument('-o', '--output', default='msd_analysis',
                       help='Output prefix for plots')
    parser.add_argument('--method', choices=['mdanalysis', 'gromacs'], 
                       default='gromacs',
                       help='Method for MSD calculation')
    parser.add_argument('--box-length', type=float, default=None,
                       help='Box length in nm for system-size correction')
    
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print(f" MSD & DIFFUSION COEFFICIENT CALCULATION")
    print(f"{'='*70}")
    print(f"Trajectory: {args.trajectory}")
    print(f"Topology: {args.topology}")
    print(f"Fit range: {args.fit_start}-{args.fit_end} ps")
    print(f"Method: {args.method}")
    
    # Calculate MSD
    if args.method == 'mdanalysis':
        print("\nUsing MDAnalysis for MSD calculation...")
        time, msd, msd_sem, msd_particles = calculate_msd_mdanalysis(
            args.topology, args.trajectory, 
            atom_sel='name OW'
        )
    else:
        print("\nUsing GROMACS msd tool...")
        time, msd, msd_sem, msd_particles = calculate_msd_manual(
            args.trajectory, args.topology
        )
    
    print(f"  Time range: {time[0]:.1f} - {time[-1]:.1f} ps")
    print(f"  MSD at final time: {msd[-1]:.3f} nm²")
    
    # Fit diffusion coefficient
    print("\nFitting diffusion coefficient...")
    fit_results = fit_diffusion_coefficient(
        time, msd, msd_sem,
        fit_start=args.fit_start,
        fit_end=args.fit_end,
        method='linear'
    )
    
    print(f"  D = {fit_results['D_cm2_s']:.4f} × 10⁻⁵ cm²/s")
    print(f"  R² = {fit_results['r_squared']:.6f}")
    
    # Block error analysis (if particle data available)
    D_blocks = None
    if msd_particles is not None and args.method == 'mdanalysis':
        print("\nPerforming block error analysis...")
        D_mean, D_sem, D_blocks = block_error_analysis(
            time, msd_particles, args.n_blocks,
            args.fit_start, args.fit_end
        )
        print(f"  D (block avg) = {D_mean:.4f} ± {D_sem:.4f} × 10⁻⁵ cm²/s")
    
    # System size correction
    system_correction = None
    if args.box_length is not None:
        print("\nApplying system-size correction...")
        L_m = args.box_length * 1e-9  # Convert nm to m
        D_corr, correction = system_size_correction(
            fit_results['D_cm2_s'] * 1e-5,  # Convert to m²/s
            L_m
        )
        D_corr *= 1e5  # Convert back to 10⁻⁵ cm²/s
        system_correction = (D_corr, correction * 1e5)
        print(f"  Raw D: {fit_results['D_cm2_s']:.4f} × 10⁻⁵ cm²/s")
        print(f"  Correction: +{correction*1e5:.4f} × 10⁻⁵ cm²/s")
        print(f"  Corrected D: {D_corr:.4f} × 10⁻⁵ cm²/s")
    
    # Generate report
    print_diffusion_report(fit_results, D_blocks, system_correction)
    
    # Generate plots
    print("Generating plots...")
    plot_msd_analysis(time, msd, msd_sem, fit_results, D_blocks, args.output)
    
    print("\nAnalysis complete!")
```

---

## 7. Run the Diffusion Analysis

### 7.1 Using MDAnalysis (Recommended)

```bash
# Install MDAnalysis if not available
pip install MDAnalysis

# Run the complete analysis
python3 calculate_diffusion.py \
    -f md_noPBC.xtc \
    -s md.tpr \
    --fit-start 10 \
    --fit-end 100 \
    --n-blocks 5 \
    --method mdanalysis \
    --box-length 6.4 \
    -o diffusion_analysis
```

### 7.2 Using GROMACS Built-in Tool

```bash
# Quick MSD calculation
gmx msd -f md_noPBC.xtc -s md.tpr -n index.ndx \
    -o msd_gromacs.xvg \
    -beginfit 10 -endfit 100 << EOF
OW_only
EOF

# The output includes D in the terminal or at the end of msd_gromacs.xvg
tail -5 msd_gromacs.xvg

# GROMACS prints D directly:
# D[OW_only] = 0.2473 (+/- 0.0124) 1e-5 cm^2/s
```

### 7.3 Alternative: Manual MSD Calculation Script

For complete control, use this standalone MSD calculator:

```python
#!/usr/bin/env python3
"""Manual MSD calculation using MDAnalysis with per-molecule tracking."""
import MDAnalysis as mda
import numpy as np
from scipy import stats

def compute_msd_manual(xtc_file, tpr_file, atom_sel='name OW'):
    """Manual MSD computation with per-molecule tracking."""
    
    u = mda.Universe(tpr_file, xtc_file)
    oxygens = u.select_atoms(atom_sel)
    n_oxygens = len(oxygens)
    n_frames = len(u.trajectory)
    
    print(f"Processing {n_oxygens} OW atoms over {n_frames} frames...")
    
    # Store all positions: [n_frames, n_atoms, 3]
    all_positions = np.zeros((n_frames, n_oxygens, 3))
    
    for ts in u.trajectory:
        all_positions[ts.frame] = oxygens.positions.copy()
    
    dt = u.trajectory[1].time - u.trajectory[0].time  # ps
    
    # Calculate MSD for multiple time origins
    max_lag = n_frames // 2
    msd = np.zeros(max_lag)
    count = np.zeros(max_lag)
    
    for origin in range(0, n_frames - max_lag):
        for lag in range(1, max_lag):
            if origin + lag < n_frames:
                displacement = all_positions[origin + lag] - all_positions[origin]
                squared_displacement = np.sum(displacement**2, axis=1)
                msd[lag] += np.mean(squared_displacement)
                count[lag] += 1
    
    # Average over time origins
    time = np.arange(max_lag) * dt
    msd = msd / np.maximum(count, 1)
    
    # Fit diffusion coefficient (10-50 ps for 100 ps trajectory)
    fit_start_idx = int(10 / dt)
    fit_end_idx = min(int(50 / dt), max_lag - 1)
    
    slope, intercept, r_value, p_value, std_err = \
        stats.linregress(time[fit_start_idx:fit_end_idx], 
                        msd[fit_start_idx:fit_end_idx])
    
    D = slope / 6.0  # nm²/ps
    D_cm2_s = D * 1e-2  # cm²/s
    
    print(f"\nResults:")
    print(f"  D = {D_cm2_s:.4f} × 10⁻⁵ cm²/s")
    print(f"  R² = {r_value**2:.6f}")
    
    return time, msd, D_cm2_s

# Usage
time, msd, D = compute_msd_manual('md_noPBC.xtc', 'md.tpr')
np.savetxt('msd_manual.xvg', np.column_stack([time, msd]),
           header='@    xaxis  label "Time (ps)"\n@    yaxis  label "MSD (nm^2)"')
```

---

## 8. Fitting Guidelines and Best Practices

### 8.1 Choosing the Fitting Range

This is the most critical step for accurate diffusion coefficients:

```python
#!/usr/bin/env python3
"""Script to determine optimal fitting range for MSD."""
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

def find_diffusive_regime(time, msd):
    """Automatically find the diffusive regime in MSD data."""
    
    # Calculate time-dependent D
    D_t = msd[1:] / (6 * time[1:])
    
    # Calculate local slope on log-log plot
    window = max(5, len(time) // 50)
    log_t = np.log10(time[1:])
    log_msd = np.log10(msd[1:])
    
    slopes = []
    for i in range(len(log_t) - window):
        slope, _, _, _, _ = stats.linregress(
            log_t[i:i+window], log_msd[i:i+window]
        )
        slopes.append(slope)
    slopes = np.array(slopes)
    slopes_time = time[1 + window//2:len(slopes)+1+window//2]
    
    # Find where slope ≈ 1 (±0.05)
    diffusive = np.abs(slopes - 1.0) < 0.05
    
    if np.sum(diffusive) > 0:
        # Find longest continuous diffusive region
        diff_regions = []
        start = None
        for i, is_diff in enumerate(diffusive):
            if is_diff and start is None:
                start = i
            elif not is_diff and start is not None:
                diff_regions.append((start, i-1))
                start = None
        if start is not None:
            diff_regions.append((start, len(diffusive)-1))
        
        if diff_regions:
            # Use the longest region
            longest = max(diff_regions, key=lambda x: x[1]-x[0])
            fit_start = slopes_time[longest[0]]
            fit_end = slopes_time[longest[1]]
            print(f"Optimal fitting range: {fit_start:.1f} - {fit_end:.1f} ps")
            return fit_start, fit_end
    
    # Fallback: use 10-80% of trajectory
    t_max = time[-1]
    fit_start = t_max * 0.1
    fit_end = t_max * 0.8
    print(f"Warning: Using fallback range: {fit_start:.1f} - {fit_end:.1f} ps")
    return fit_start, fit_end

# Plot to visualize
def plot_beta_vs_time(time, msd, output='beta_analysis.png'):
    """Plot beta(t) = d(log MSD)/d(log t) to identify diffusive regime."""
    window = 20
    beta_values = []
    beta_time = []
    
    for i in range(len(time) - window):
        log_t = np.log(time[i:i+window])
        log_msd = np.log(msd[i:i+window])
        slope, _, r, _, _ = stats.linregress(log_t, log_msd)
        beta_values.append(slope)
        beta_time.append(time[i + window//2])
    
    beta_values = np.array(beta_values)
    beta_time = np.array(beta_time)
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Beta vs time
    axes[0].plot(beta_time, beta_values, 'b-', linewidth=1.5)
    axes[0].axhline(y=1.0, color='r', linestyle='--', label='Diffusive (β=1)')
    axes[0].axhline(y=2.0, color='g', linestyle=':', label='Ballistic (β=2)')
    axes[0].fill_between(beta_time, 0.95, 1.05, alpha=0.2, color='green',
                         label='Diffusive range (0.95<β<1.05)')
    axes[0].set_xlabel('Time (ps)')
    axes[0].set_ylabel('β(t) = d(log MSD)/d(log t)')
    axes[0].set_title('Identification of Diffusive Regime')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # MSD with diffusive region highlighted
    axes[1].loglog(time[1:], msd[1:], 'b-', linewidth=1.5, label='MSD')
    axes[1].loglog(time[1:], 0.01*time[1:]**1.0, 'r--', alpha=0.7, label='~t¹')
    axes[1].loglog(time[1:], 0.1*time[1:]**2.0, 'g:', alpha=0.7, label='~t²')
    
    # Highlight diffusive region
    diff_mask = np.abs(beta_values - 1.0) < 0.05
    if np.any(diff_mask):
        t_diff_start = beta_time[diff_mask][0]
        t_diff_end = beta_time[diff_mask][-1]
        axes[1].axvspan(t_diff_start, t_diff_end, alpha=0.2, color='green')
    
    axes[1].set_xlabel('Time (ps)')
    axes[1].set_ylabel('MSD (nm²)')
    axes[1].set_title('MSD with Diffusive Regime Highlighted')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    print(f"Beta analysis plot saved to '{output}'")
    
    return beta_time, beta_values

# Usage
time, msd = np.loadtxt('msd_gromacs.xvg', comments=('#', '@')).T
fit_start, fit_end = find_diffusive_regime(time, msd)
beta_time, beta_values = plot_beta_vs_time(time, msd)
```

### 8.2 Key Fitting Rules

1. **Ballistic regime (t < ~1 ps):** MSD ∝ t²; **do not use for D**
2. **Crossover regime (1-10 ps):** Transition region; use with caution
3. **Diffusive regime (t > 10 ps):** MSD ∝ t; **use this for D**
4. **Poor statistics (t > 50% of trajectory length):** Large error bars; limit fit end

**Rule of thumb:** Fit from ~20% to ~80% of the trajectory length, or visually verify β(t) ≈ 1.

---

## 9. Expected Output Files

| File | Description |
|------|-------------|
| `md_noPBC.xtc` | Unwrapped trajectory (critical) |
| `msd.xvg` | MSD from GROMACS msd tool |
| `msd_gromacs.xvg` | MSD with fit line annotated |
| `diffusion_analysis.png` | Comprehensive analysis plots |
| `beta_analysis.png` | β(t) analysis for regime identification |
| `unwrapping_check.png` | Verification of PBC removal |

---

## 10. Expected Results

### SPC/E Water at 300 K, 1 bar

| Property | Value | Units |
|----------|-------|-------|
| D (simulation, 216 waters) | 2.2–2.4 | 10⁻⁵ cm²/s |
| D (corrected, infinite system) | 2.4–2.6 | 10⁻⁵ cm²/s |
| D (experimental) | 2.30 | 10⁻⁵ cm²/s |
| D (SPC/E reference, 50 ns) | 2.49 | 10⁻⁵ cm²/s |
| β in diffusive regime | 0.98–1.02 | dimensionless |
| Diffusive onset | 5–15 | ps |

### System-Size Dependence

For a box of length L (nm), the correction is approximately:

| Box size (nm) | N_waters | Raw D | Correction | Corrected D |
|---------------|----------|-------|------------|-------------|
| 1.86 | 216 | 2.24 | +0.31 | 2.55 |
| 3.0 | 900 | 2.35 | +0.19 | 2.54 |
| 5.0 | 4200 | 2.42 | +0.11 | 2.53 |
| 7.0 | 11500 | 2.47 | +0.08 | 2.55 |

---

## 11. Common Errors and Solutions

### 11.1 PBC-Related Errors

| Error | Symptom | Solution |
|-------|---------|----------|
| PBC not removed | MSD plateaus or oscillates | Use `gmx trjconv -pbc nojump` |
| Molecules broken across PBC | Jumps in MSD | Use `-pbc mol` before `-pbc nojump` |
| COM drift | Linear trend in unwrapped coords | Use `-center` and `-ur compact` |

### 11.2 Fitting Errors

| Error | Symptom | Solution |
|-------|---------|----------|
| Fitting in ballistic regime | D too high, MSD curved upward | Start fit after crossover (>10 ps) |
| Fitting too late | D too low, poor statistics | Limit fit end to 50-80% of trajectory |
| Non-linear MSD | R² < 0.99, systematic residuals | Extend simulation; check for drift |
| Large uncertainty | D varies with fit range | Use longer trajectories; block averaging |

### 11.3 Trajectory Quality Errors

| Error | Symptom | Solution |
|-------|---------|----------|
| Trajectory too short (<1 ns) | D unreliable, large error | Minimum 10 ns recommended |
| Infrequent saving | Few data points in diffusive regime | Save every 0.1-0.5 ps |
| Thermostat artifacts | D too high/low | Use Nose-Hoover or NVE, not Berendsen |
| Equilibration incomplete | D drifts with time | Discard first 20% of trajectory |

### 11.4 Common Warning Messages

| Warning | Meaning | Action |
|---------|---------|--------|
| `No molecules were whole at t=0` | PBC issues | Re-run unwrapping |
| `The MSD is not linear` | Not in diffusive regime | Check β(t) plot |
| `D from MSD may be inaccurate` | GROMACS warning for short trajectories | Extend simulation |

---

## 12. Short-Trajectory Limitations

### 12.1 Why Short Trajectories Are Problematic

For a trajectory of length T_total:

1. **Maximum reliable lag time:** T_total/5 to T_total/3
2. **Minimum diffusive onset:** ~10 ps for water
3. **Required diffusive window:** At least 20 ps for reliable fit

**Therefore, minimum reliable trajectory length: ~100 ps for water.**

However, for publication-quality results:
- **Minimum:** 5-10 ns
- **Recommended:** 20-50 ns
- **Ideal:** 100+ ns

### 12.2 Error Scaling with Trajectory Length

```python
# Estimate D uncertainty vs trajectory length
# Based on D = 2.4 × 10⁻⁵ cm²/s for SPC/E

trajectory_lengths = [0.1, 0.5, 1, 5, 10, 50, 100]  # ns
relative_errors = [25, 10, 7, 3, 2, 1, 0.7]  # approximate %

print("Trajectory Length | D Uncertainty")
print("-" * 35)
for t, err in zip(trajectory_lengths, relative_errors):
    print(f"  {t:8.1f} ns      | ±{err:5.1f}%")
```

### 12.3 Mitigation Strategies for Short Trajectories

If you only have a short trajectory (< 1 ns):

1. **Use multiple time origins aggressively:**
   ```bash
   gmx msd -trestart 1  # Use every frame as origin
   ```

2. **Fit earlier (with caution):**
   - Accept fit from 5-20 ps instead of 10-100 ps
   - Acknowledge possible systematic error in publications

3. **Report D with caveats:**
   - "D = 2.4 ± 0.5 × 10⁻⁵ cm²/s (from 500 ps trajectory; systematic errors may be present)"

4. **Use system-size correction carefully:**
   - The Yeh-Hummer correction assumes diffusive regime is reached
   - For very short trajectories, this may overcorrect

---

## 13. Complete Automated Diffusion Workflow

Save as `run_diffusion_analysis.sh`:

```bash
#!/bin/bash
# Complete diffusion coefficient calculation workflow
set -e

echo "=========================================="
echo " WATER DIFFUSION COEFFICIENT WORKFLOW"
echo "=========================================="

# Configuration
TRAJ="md.xtc"
TPR="md.tpr"
EDR="md.edr"
FIT_START=10
FIT_END=100

# Check for required files
for f in $TRAJ $TPR; do
    if [ ! -f "$f" ]; then
        echo "ERROR: Required file '$f' not found."
        exit 1
    fi
done

# Step 1: Determine box size for correction
echo "[1/7] Determining box size..."
BOX_SIZE=$(tail -1 md.gro | awk '{print $1}')
echo "  Box length: $BOX_SIZE nm"

# Step 2: Create index for OW atoms
echo "[2/7] Creating index file..."
gmx make_ndx -f $TPR -o index.ndx << EOF
a OW
name 18 OW_only
q
EOF

# Step 3: Remove PBC (CRITICAL)
echo "[3/7] Removing periodic boundary conditions..."
gmx trjconv -f $TRAJ -s $TPR -n index.ndx -o traj_noPBC.xtc -pbc nojump << EOF
OW_only
EOF
echo "  Unwrapped trajectory saved as traj_noPBC.xtc"

# Step 4: Verify unwrapping
echo "[4/7] Verifying unwrapping..."
gmx traj -f traj_noPBC.xtc -s $TPR -n index.ndx -ox coord_check.xvg -b 0 -e 10 << EOF
OW_only
EOF

python3 << EOF
import numpy as np
data = np.loadtxt('coord_check.xvg', comments=('#', '@'))
x_range = data[:, 1].max() - data[:, 1].min()
if x_range > $BOX_SIZE:
    print(f"  ✓ Unwrapping appears successful (x-range: {x_range:.1f} nm)")
else:
    print(f"  ✗ WARNING: X-range ({x_range:.1f} nm) < box size ({$BOX_SIZE} nm)")
    print("    Possible unwrapping issue!")
EOF

# Step 5: Calculate MSD with GROMACS
echo "[5/7] Calculating MSD with GROMACS..."
gmx msd -f traj_noPBC.xtc -s $TPR -n index.ndx \
    -o msd.xvg -mol diff_mol.xvg \
    -beginfit $FIT_START -endfit $FIT_END \
    -trestart 10 << EOF
OW_only
EOF

# Extract D from XVG comments
D_RAW=$(tail -1 msd.xvg | grep -oP 'D\[.*?\] = \K[0-9.]+' || 
        grep "D\[" msd.xvg | tail -1 | awk '{print $3}')
echo "  Raw D from GROMACS: ${D_RAW} × 10⁻⁵ cm²/s"

# Step 6: Python analysis for error and correction
echo "[6/7] Running detailed analysis..."
python3 << EOF
import numpy as np
from scipy import stats

# Read MSD data
data = np.loadtxt('msd.xvg', comments=('#', '@'))
time = data[:, 0]
msd = data[:, 1]

# Calculate time-dependent D
D_t = msd[1:] / (6 * time[1:]) * 1e-2

# System size correction
kB = 1.380649e-23
T = 300
eta = 0.85e-3
L_m = $BOX_SIZE * 1e-9
correction_cm2s = (kB * T) / (6 * np.pi * eta * L_m) * 1e4

# Fit
mask = (time >= $FIT_START) & (time <= $FIT_END)
slope, intercept, r, p, std_err = stats.linregress(time[mask], msd[mask])
D_fit = slope / 6.0 * 1e-2
D_corrected = D_fit + correction_cm2s

print(f"\n  Fitting results:")
print(f"  D (fitted, {$FIT_START}-{$FIT_END} ps): {D_fit:.4f} × 10⁻⁵ cm²/s")
print(f"  R²: {r**2:.6f}")
print(f"  System-size correction: +{correction_cm2s:.4f} × 10⁻⁵ cm²/s")
print(f"  D (corrected): {D_corrected:.4f} × 10⁻⁵ cm²/s")
print(f"  Reference (SPC/E): 2.40-2.49 × 10⁻⁵ cm²/s")

# Save results
with open('diffusion_results.txt', 'w') as f:
    f.write(f"D_fit = {D_fit:.4f} × 10⁻⁵ cm²/s\n")
    f.write(f"D_corrected = {D_corrected:.4f} × 10⁻⁵ cm²/s\n")
    f.write(f"R_squared = {r**2:.6f}\n")
    f.write(f"Correction = {correction_cm2s:.4f}\n")
    f.write(f"Box_size_nm = {$BOX_SIZE}\n")
    f.write(f"Fit_range = {$FIT_START}-{$FIT_END} ps\n")
EOF

# Step 7: Summary
echo "[7/7] Workflow complete!"
echo ""
echo "=========================================="
echo " RESULTS SUMMARY"
echo "=========================================="
cat diffusion_results.txt
echo "=========================================="
echo ""
echo "Output files:"
echo "  traj_noPBC.xtc  - Unwrapped trajectory"
echo "  msd.xvg         - MSD with GROMACS fit"
echo "  diffusion_results.txt - Final results"
echo ""
echo "For detailed analysis, run:"
echo "  python3 calculate_diffusion.py -f traj_noPBC.xtc -s $TPR --fit-start $FIT_START --fit-end $FIT_END"
```

Run it:
```bash
chmod +x run_diffusion_analysis.sh
./run_diffusion_analysis.sh
```

---

## 14. Quick Validation Commands

```bash
# 1. Quick check: Is unwrapping successful?
python3 -c "
import numpy as np
data = np.loadtxt('msd.xvg', comments=('#', '@'))
# MSD should increase monotonically and NOT plateau
msd = data[:, 1]
if msd[-1] > 10 * msd[len(msd)//10]:
    print('✓ MSD increases significantly (good)')
else:
    print('✗ MSD may not be increasing enough')
print(f'Final MSD: {msd[-1]:.2f} nm²')
"

# 2. Check diffusive regime
python3 -c "
import numpy as np
from scipy import stats
data = np.loadtxt('msd.xvg', comments=('#', '@'))
t, msd = data[:, 0], data[:, 1]
# Slope on log-log plot for last decade
mask = t > t[-1]/10
log_t, log_msd = np.log10(t[mask]), np.log10(msd[mask])
slope = stats.linregress(log_t, log_msd)[0]
print(f'Log-log slope (should be ~1): {slope:.3f}')
if 0.95 < slope < 1.05:
    print('✓ In diffusive regime')
else:
    print('✗ Not in diffusive regime')
"

# 3. Compare with literature
python3 -c "
D_lit = 2.40  # SPC/E reference
D_calc = $(grep 'D_fit' diffusion_results.txt | awk '{print $3}')
dev = (D_calc - D_lit) / D_lit * 100
print(f'Deviation from SPC/E reference: {dev:+.1f}%')
if abs(dev) < 10:
    print('✓ Within acceptable range (<10%)')
else:
    print('✗ Large deviation from reference')
"
```

---
