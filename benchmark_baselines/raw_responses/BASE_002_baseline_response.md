Here is a complete GROMACS post-processing workflow to extract and validate the temperature time series from an energy file (`.edr`) for a pure water simulation at 300 K.

---

## 1. Required Input Files

The workflow assumes you have completed a molecular dynamics simulation and have the following files:

| File          | Description                                          | Required |
|---------------|------------------------------------------------------|----------|
| `md.edr`      | Energy file from production MD (binary, portable)    | **Yes**  |
| `nvt.edr`     | Energy file from NVT equilibration (optional)        | No       |
| `npt.edr`     | Energy file from NPT equilibration (optional)        | No       |
| `md.log`      | Log file from production MD (optional, for cross-check) | No   |
| `md.tpr`      | Topology/run input file (optional, for metadata)     | No       |

If you followed the previous workflow, these files are already in your working directory:
```bash
ls -lh *.edr *.log
# Expected: em.edr  nvt.edr  npt.edr  md.edr  md.log
```

---

## 2. Basic Extraction: Single Temperature Time Series

### 2.1 Extract Temperature from EDR File

```bash
# Extract temperature from production MD energy file
gmx energy -f md.edr -o temperature_prod.xvg
```

**Interactive selection:**
When prompted with a list of energy terms, you will see something like:
```
Select the terms you want from the following list
End your selection with an empty line or a zero
-------------------------------------------------------------------
  1  Bond             2  Angle            3  Proper-Dih.      
  4  Ryckaert-Bell.   5  LJ-14            6  Coulomb-14       
  7  LJ-(SR)          8  Disper.-corr.    9  Coulomb-(SR)     
 10  Coul.-recip.    11  Potential       12  Kinetic-En.      
 13  Total-Energy    14  Temperature     15  Pressure-(bar)   
 16  Box-X           17  Box-Y           18  Box-Z            
 19  Volume          20  Density         21  pV               
 22  Enthalpy        23  Vir-XX          24  Vir-XY           
 ...
```

**Type:** `14` (or `Temperature`) and press Enter twice.

**Non-interactive extraction:**
```bash
# Direct extraction without prompts
gmx energy -f md.edr -o temperature_prod.xvg <<< "Temperature"
# or by number:
gmx energy -f md.edr -o temperature_prod.xvg <<< "14"
```

### 2.2 What the XVG File Contains

Inspect the first 30 lines of the output:

```bash
head -30 temperature_prod.xvg
```

Expected output structure:
```
# This file was created Thu Jun 20 10:15:30 2026
# by the following command:
# gmx energy -f md.edr -o temperature_prod.xvg 
#
@    title "GROMACS Energies"
@    xaxis  label "Time (ps)"
@    yaxis  label "Temperature"
@TYPE xy
@ view 0.15, 0.15, 0.75, 0.85
@ legend on
@ legend box on
@ legend loctype view
@ legend 0.78, 0.8
@ legend length 2
@ s0 legend "Temperature"
   0.000000  300.125000
   2.000000  299.876000
   4.000000  300.342000
   6.000000  299.987000
   8.000000  300.456000
  10.000000  299.654000
  ...
```

---

## 3. Comprehensive Post-Processing Workflow

### 3.1 Extract Temperature from Multiple Run Phases

```bash
# Extract temperatures from all equilibration phases and production
gmx energy -f em.edr  -o temperature_em.xvg  <<< "Temperature" 2>/dev/null || echo "No T in EM (expected)"
gmx energy -f nvt.edr -o temperature_nvt.xvg <<< "Temperature"
gmx energy -f npt.edr -o temperature_npt.xvg <<< "Temperature"
gmx energy -f md.edr  -o temperature_md.xvg  <<< "Temperature"
```

### 3.2 Concatenate All Phases for a Complete Time Series

```bash
# Create a combined temperature history
# First, extract time and temperature from each phase, stripping headers

for phase in nvt npt md; do
    # Remove header lines (those starting with # or @)
    grep -v "^[#@]" temperature_${phase}.xvg > temp_${phase}_clean.dat
done

# Concatenate, adjusting time offsets
# NVT: 0–100 ps, NPT: 100–200 ps, MD: 200–1200 ps
awk '{print $1, $2}' temp_nvt_clean.dat > temp_combined.dat
awk -v offset=100 '{print $1+offset, $2}' temp_npt_clean.dat >> temp_combined.dat
awk -v offset=200 '{print $1+offset, $2}' temp_md_clean.dat >> temp_combined.dat

# Add XVG headers back
echo "@    title \"Combined Temperature Profile\"" > temperature_combined.xvg
echo "@    xaxis  label \"Time (ps)\"" >> temperature_combined.xvg
echo "@    yaxis  label \"Temperature (K)\"" >> temperature_combined.xvg
echo "@TYPE xy" >> temperature_combined.xvg
cat temp_combined.dat >> temperature_combined.xvg

# Clean up temporary files
rm temp_*_clean.dat temp_combined.dat
```

### 3.3 Extract Temperature from Log File for Cross-Validation

```bash
# GROMACS log files also contain temperature information
grep "Temperature" md.log | awk '{print NR, $3}' > temperature_from_log.dat
```

---

## 4. Statistical Analysis and Validation

### 4.1 Basic Statistics Using GROMACS Tools

```bash
# Analyze the energy file to get statistics directly
gmx energy -f md.edr -o temperature_stats.xvg <<< "Temperature" 2>&1 | tee energy_stats.txt

# The output includes statistics. Alternatively, use the `-fee` flag:
gmx energy -f md.edr -fee temperature_stats.xvg <<< "Temperature" 2>&1 | grep -A 20 "Energy Average"
```

### 4.2 Compute Statistics with GROMACS `analyze` Tool

```bash
# Extract just the temperature column from XVG (skip header)
grep -v "^[#@]" temperature_md.xvg | awk '{print $2}' > temp_values.dat

# Use gmx analyze for detailed statistics
gmx analyze -f temp_values.dat -av -ee -ac temp_acf.xvg 2>&1 | tee temperature_analysis.txt
```

**Expected output:**
```
Reading data from temp_values.dat...
Read 501 points
Average:    300.023
Std. Dev.:    1.245
Error est.:   0.056
Variance:     1.550
```

### 4.3 Python-Based Statistical Analysis Script

Create `analyze_temperature.py`:

```python
#!/usr/bin/env python3
"""
Comprehensive temperature time series analysis for GROMACS water simulation.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import argparse
import sys

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

def compute_statistics(time, temp, target_temp=300.0):
    """Compute comprehensive temperature statistics."""
    
    # Basic statistics
    mean_temp = np.mean(temp)
    std_temp = np.std(temp, ddof=1)
    min_temp = np.min(temp)
    max_temp = np.max(temp)
    
    # Error estimate (standard error of the mean)
    # Accounting for autocorrelation: use block averaging
    n_blocks = 10
    block_size = len(temp) // n_blocks
    block_means = [np.mean(temp[i*block_size:(i+1)*block_size]) for i in range(n_blocks)]
    sem_blocks = np.std(block_means, ddof=1) / np.sqrt(n_blocks)
    
    # Drift analysis: linear fit
    slope, intercept, r_value, p_value, std_err = stats.linregress(time, temp)
    drift_per_ns = slope * 1000  # Convert from K/ps to K/ns
    
    # Temperature distribution test (normality)
    _, normality_p = stats.normaltest(temp)
    is_normal = normality_p > 0.05
    
    # Autocorrelation analysis
    temp_centered = temp - mean_temp
    autocorr = np.correlate(temp_centered, temp_centered, mode='full')
    autocorr = autocorr[len(autocorr)//2:] / autocorr[len(autocorr)//2]
    
    # Find decorrelation time (when autocorrelation drops below 1/e)
    threshold = 1.0 / np.e
    decorr_idx = np.where(autocorr < threshold)[0]
    decorr_time = time[decorr_idx[0]] if len(decorr_idx) > 0 else time[-1]
    
    # RMS deviation from target
    rmsd_target = np.sqrt(np.mean((temp - target_temp)**2))
    
    return {
        'mean': mean_temp,
        'std': std_temp,
        'min': min_temp,
        'max': max_temp,
        'sem_blocks': sem_blocks,
        'drift_per_ns': drift_per_ns,
        'r_squared': r_value**2,
        'normality_p': normality_p,
        'is_normal': is_normal,
        'decorr_time': decorr_time,
        'rmsd_target': rmsd_target,
        'target': target_temp
    }

def plot_temperature_analysis(time, temp, stats, output_prefix='temperature_analysis'):
    """Generate comprehensive temperature analysis plots."""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Temperature vs Time
    ax1 = axes[0, 0]
    ax1.plot(time, temp, 'b-', linewidth=0.5, alpha=0.7, label='Temperature')
    ax1.axhline(y=stats['target'], color='r', linestyle='--', 
                label=f"Target: {stats['target']} K")
    ax1.axhline(y=stats['mean'], color='g', linestyle='-', 
                label=f"Mean: {stats['mean']:.2f} K")
    ax1.axhspan(stats['mean']-stats['std'], stats['mean']+stats['std'], 
                alpha=0.2, color='green', label=f"±1σ: {stats['std']:.2f} K")
    ax1.set_xlabel('Time (ps)')
    ax1.set_ylabel('Temperature (K)')
    ax1.set_title('Temperature Time Series')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # 2. Temperature Distribution
    ax2 = axes[0, 1]
    n, bins, patches = ax2.hist(temp, bins=50, density=True, alpha=0.7, 
                                 color='blue', edgecolor='black')
    # Fit normal distribution
    x_fit = np.linspace(temp.min(), temp.max(), 200)
    y_fit = stats.norm.pdf(x_fit, stats['mean'], stats['std'])
    ax2.plot(x_fit, y_fit, 'r-', linewidth=2, label='Normal fit')
    ax2.axvline(x=stats['target'], color='red', linestyle='--', 
                label=f"Target: {stats['target']} K")
    ax2.set_xlabel('Temperature (K)')
    ax2.set_ylabel('Probability Density')
    ax2.set_title(f'Temperature Distribution\n' + 
                  (f'Normal: {"✓" if stats["is_normal"] else "✗"} ' 
                   f'(p={stats["normality_p"]:.3f})'))
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # 3. Running Average
    ax3 = axes[1, 0]
    window = len(temp) // 50  # 2% of data
    if window > 1:
        running_avg = np.convolve(temp, np.ones(window)/window, mode='valid')
        running_time = time[window-1:]
        ax3.plot(running_time, running_avg, 'r-', linewidth=1.5, label=f'Running Avg (window={window})')
    ax3.axhline(y=stats['target'], color='red', linestyle='--', label=f'Target: {stats["target"]} K')
    ax3.fill_between(time, stats['target']-2, stats['target']+2, alpha=0.1, color='red',
                     label='±2 K tolerance')
    ax3.set_xlabel('Time (ps)')
    ax3.set_ylabel('Temperature (K)')
    ax3.set_title(f'Running Average\nDrift: {stats["drift_per_ns"]:.2f} K/ns (R²={stats["r_squared"]:.4f})')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # 4. Autocorrelation Function
    ax4 = axes[1, 1]
    temp_centered = temp - stats['mean']
    autocorr = np.correlate(temp_centered, temp_centered, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    autocorr = autocorr / autocorr[0]
    max_lag = min(len(autocorr), 1000)  # Show first 1000 frames or less
    ax4.plot(time[:max_lag], autocorr[:max_lag], 'b-', linewidth=1)
    ax4.axhline(y=1/np.e, color='red', linestyle='--', 
                label=f'1/e = {1/np.e:.3f}')
    if stats['decorr_time'] < time[-1]:
        ax4.axvline(x=stats['decorr_time'], color='green', linestyle='--',
                    label=f'Decorr. time: {stats["decorr_time"]:.1f} ps')
    ax4.set_xlabel('Lag Time (ps)')
    ax4.set_ylabel('Autocorrelation')
    ax4.set_title('Temperature Autocorrelation Function')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_prefix}.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Plots saved to '{output_prefix}.png'")

def print_report(stats):
    """Print a formatted validation report."""
    print("\n" + "="*70)
    print(" TEMPERATURE TIME SERIES VALIDATION REPORT")
    print("="*70)
    print(f"\n{'Parameter':<40} {'Value':<25} {'Status'}")
    print("-"*70)
    
    checks = []
    
    # Mean temperature
    mean_diff = abs(stats['mean'] - stats['target'])
    mean_ok = mean_diff < 2.0
    checks.append(mean_ok)
    print(f"{'Mean temperature':<40} {stats['mean']:>8.2f} K {'✓' if mean_ok else '✗':>15}")
    
    # Standard deviation
    std_ok = stats['std'] < 10.0
    checks.append(std_ok)
    print(f"{'Standard deviation':<40} {stats['std']:>8.2f} K {'✓' if std_ok else '✗':>15}")
    
    # Standard error
    print(f"{'Standard error (block avg)':<40} {stats['sem_blocks']:>8.3f} K")
    
    # Temperature range
    range_temp = stats['max'] - stats['min']
    range_ok = range_temp < 20.0
    checks.append(range_ok)
    print(f"{'Temperature range':<40} {range_temp:>8.2f} K {'✓' if range_ok else '✗':>15}")
    
    # Drift
    drift_ok = abs(stats['drift_per_ns']) < 2.0
    checks.append(drift_ok)
    print(f"{'Drift per ns':<40} {stats['drift_per_ns']:>8.3f} K/ns {'✓' if drift_ok else '✗':>15}")
    print(f"{'  R-squared of fit':<40} {stats['r_squared']:>8.4f}")
    
    # RMS deviation from target
    rmsd_ok = stats['rmsd_target'] < 5.0
    checks.append(rmsd_ok)
    print(f"{'RMSD from target':<40} {stats['rmsd_target']:>8.2f} K {'✓' if rmsd_ok else '✗':>15}")
    
    # Normality
    print(f"{'Normal distribution':<40} {'Yes' if stats['is_normal'] else 'No':>8} "
          f"{'✓' if stats['is_normal'] else '✗':>15}")
    print(f"{'  D\'Agostino p-value':<40} {stats['normality_p']:>8.4f}")
    
    # Decorrelation
    print(f"{'Decorrelation time':<40} {stats['decorr_time']:>8.1f} ps")
    
    # Effective sample size estimate
    if stats['decorr_time'] > 0:
        eff_samples = (time[-1] - time[0]) / stats['decorr_time']
        print(f"{'Effective samples (est.)':<40} {eff_samples:>8.0f}")
    
    print("-"*70)
    all_ok = all(checks)
    print(f"\n{'OVERALL STATUS:':<40} {'PASS' if all_ok else 'FAIL':>8} "
          f"{'✓' if all_ok else '✗':>15}")
    print(f"  {sum(checks)}/{len(checks)} checks passed")
    print("="*70 + "\n")
    
    return all_ok

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze GROMACS temperature time series')
    parser.add_argument('-f', '--file', required=True, help='Input XVG file')
    parser.add_argument('-t', '--target', type=float, default=300.0, 
                       help='Target temperature in K (default: 300.0)')
    parser.add_argument('-o', '--output', default='temperature_analysis', 
                       help='Output prefix for plots (default: temperature_analysis)')
    args = parser.parse_args()
    
    print(f"\nReading temperature data from: {args.file}")
    time, temp = read_xvg(args.file)
    print(f"Loaded {len(temp)} data points")
    print(f"Time range: {time[0]:.1f} to {time[-1]:.1f} ps")
    
    print("\nComputing statistics...")
    stats = compute_statistics(time, temp, args.target)
    
    print_report(stats)
    
    print("Generating plots...")
    plot_temperature_analysis(time, temp, stats, args.output)
```

### 4.4 Run the Python Analysis

```bash
# Make the script executable
chmod +x analyze_temperature.py

# Run on production temperature file
python3 analyze_temperature.py -f temperature_md.xvg -t 300.0 -o temp_analysis_md

# Run on combined file
python3 analyze_temperature.py -f temperature_combined.xvg -t 300.0 -o temp_analysis_combined
```

---

## 5. Block Averaging for Reliable Error Estimates

Create `block_average.py`:

```python
#!/usr/bin/env python3
"""
Block averaging analysis for temperature time series.
Determines when standard error converges with block size.
"""
import numpy as np
import matplotlib.pyplot as plt
import sys

def read_xvg(filename):
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

def block_average(data, max_blocks=50):
    n = len(data)
    block_sizes = []
    means = []
    sems = []
    
    for n_blocks in range(1, max_blocks + 1):
        block_size = n // n_blocks
        if block_size < 2:
            break
        
        block_means = []
        for i in range(n_blocks):
            block = data[i*block_size:(i+1)*block_size]
            block_means.append(np.mean(block))
        
        block_sizes.append(block_size)
        means.append(np.mean(block_means))
        sems.append(np.std(block_means, ddof=1) / np.sqrt(n_blocks))
    
    return np.array(block_sizes), np.array(means), np.array(sems)

if __name__ == "__main__":
    file = sys.argv[1] if len(sys.argv) > 1 else 'temperature_md.xvg'
    
    time, temp = read_xvg(file)
    block_sizes, means, sems = block_average(temp)
    
    # Find converged SEM (where SEM plateaus)
    # Look for where SEM changes by less than 5%
    converged_idx = None
    for i in range(1, len(sems)):
        if abs(sems[i] - sems[i-1]) / sems[i-1] < 0.05:
            converged_idx = i
            break
    
    if converged_idx:
        print(f"SEM converged at block size: {block_sizes[converged_idx]}")
        print(f"Converged SEM: {sems[converged_idx]:.4f} K")
        print(f"Mean temperature: {means[converged_idx]:.3f} K")
    else:
        print("Warning: SEM did not converge within the given blocks.")
        print(f"Final SEM: {sems[-1]:.4f} K (block size: {block_sizes[-1]})")
    
    # Plot block averaging analysis
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.plot(block_sizes, means, 'b.-')
    ax1.set_xlabel('Block Size')
    ax1.set_ylabel('Mean Temperature (K)')
    ax1.set_title('Block Average Convergence')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(block_sizes, sems, 'r.-')
    ax2.set_xlabel('Block Size')
    ax2.set_ylabel('SEM (K)')
    ax2.set_title('Standard Error of the Mean Convergence')
    if converged_idx:
        ax2.axvline(x=block_sizes[converged_idx], color='g', linestyle='--',
                    label=f'Converged at {block_sizes[converged_idx]}')
        ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('block_averaging.png', dpi=150, bbox_inches='tight')
    print("Block averaging plot saved to 'block_averaging.png'")
```

Run it:
```bash
python3 block_average.py temperature_md.xvg
```

---

## 6. Expected Outputs Summary

| Output File | Description |
|-------------|-------------|
| `temperature_em.xvg` | Temperature during EM (may be empty; no thermostat) |
| `temperature_nvt.xvg` | Temperature during NVT equilibration |
| `temperature_npt.xvg` | Temperature during NPT equilibration |
| `temperature_md.xvg` | Temperature during production MD |
| `temperature_combined.xvg` | Concatenated temperature history |
| `temperature_analysis.txt` | Statistics from `gmx analyze` |
| `temp_analysis_md.png` | Comprehensive analysis plots |
| `block_averaging.png` | Block averaging convergence plot |
| `temperature_from_log.dat` | Temperature extracted from log file |

---

## 7. Quick One-Line Validation Commands

```bash
# 1. Quick mean and standard deviation
grep -v "^[#@]" temperature_md.xvg | awk '{sum+=$2; sumsq+=$2*$2; n++} END {
    mean=sum/n; std=sqrt(sumsq/n - mean*mean); 
    printf "Mean: %.2f K, Std: %.2f K\n", mean, std}'

# 2. Check if temperature is within ±3 K of target
grep -v "^[#@]" temperature_md.xvg | awk '{
    if($2 < 297 || $2 > 303) count++} END {
    printf "%.1f%% of points outside 300±3 K\n", count/NR*100}'

# 3. Find min and max temperature
grep -v "^[#@]" temperature_md.xvg | awk 'NR==1{min=$2; max=$2}
    {if($2<min) min=$2; if($2>max) max=$2} 
    END{printf "Min: %.2f K, Max: %.2f K, Range: %.2f K\n", min, max, max-min}'

# 4. Compute drift using linear regression on first and last 10%
grep -v "^[#@]" temperature_md.xvg | awk '{
    lines[NR]=$0; temp[NR]=$2}
    END{
    n=NR; n10=int(n/10);
    for(i=1;i<=n10;i++){sum1+=temp[i]; sumt1+=i}
    for(i=n-n10;i<=n;i++){sum2+=temp[i]; sumt2+=i}
    mean1=sum1/n10; mean2=sum2/n10;
    drift=(mean2-mean1)/(n*2/1000);  # in K/ns
    printf "Start mean: %.2f K, End mean: %.2f K, Drift: %.3f K/ns\n", mean1, mean2, drift}'
```

---

## 8. Validation Criteria and Acceptance Thresholds

| Parameter | Expected Value | Acceptable Range | Flag if |
|-----------|---------------|------------------|---------|
| Mean temperature | 300.0 K | 299.0–301.0 K | Deviates >2 K |
| Standard deviation | 1–3 K | <10 K | >10 K |
| Temperature range | 5–15 K | <20 K | >20 K |
| Drift | ~0 K/ns | <2 K/ns | >2 K/ns |
| RMSD from target | ~1–3 K | <5 K | >5 K |
| Distribution normality | Normal | p > 0.01 | p < 0.01 |
| Decorrelation time | 0.5–5 ps | <50 ps | >100 ps |
| SEM (block averaged) | <0.1 K | <0.5 K | >0.5 K |

---

## 9. Common Possible Errors and Solutions

| Error/Symptom | Cause | Solution |
|---------------|-------|----------|
| `Temperature` not found in energy file | No thermostat was used (e.g., NVE ensemble) | Check `.mdp` file; use `tcoupl = yes` for temperature coupling |
| Temperature extracted is constant | Wrong energy term selected, or EM file used | Ensure you select `Temperature` (not `Total-Energy`); use production `.edr` file |
| `gmx energy` produces empty output | Pipe/interactive selection failed | Use explicit here-doc: `<<< "Temperature"` or `echo "14" \| gmx energy ...` |
| Huge temperature fluctuations | Simulation unstable, water "exploding" | Check if constraints were applied (`constraints = h-bonds`); reduce timestep; verify force field |
| Mean temperature off by 5+ K | Incorrect coupling parameters | Check `ref_t` and `tau_t` in `.mdp`; ensure `tc-grps = System` |
| Temperature drift > 5 K/ns | Equilibration incomplete or thermostat issues | Extend NVT/NPT equilibration; check for energy leaks |
| Python script fails with `ImportError` | Missing scipy or matplotlib | `pip install numpy scipy matplotlib` or `conda install numpy scipy matplotlib` |
| Block averaging SEM doesn't converge | Simulation too short | Run longer production MD (at least 1–5 ns) |
| Decorrelation time extremely long | Thermostat too weak (large `tau_t`) | Reduce `tau_t` to 0.1 ps for faster equilibration |

---

## 10. Full Automated Validation Script

Save as `validate_temperature.sh`:

```bash
#!/bin/bash
# Complete temperature validation pipeline
set -e

EDR_FILE="${1:-md.edr}"
TARGET_TEMP="${2:-300.0}"
OUTPUT_PREFIX="${3:-temperature_validation}"

echo "=========================================="
echo " Temperature Validation Pipeline"
echo "=========================================="
echo "EDR file: $EDR_FILE"
echo "Target T: $TARGET_TEMP K"
echo ""

# Step 1: Extract temperature
echo "[1/5] Extracting temperature from $EDR_FILE..."
gmx energy -f "$EDR_FILE" -o "${OUTPUT_PREFIX}.xvg" <<< "Temperature"
echo "✓ Temperature extracted to ${OUTPUT_PREFIX}.xvg"

# Step 2: Basic statistics with gmx analyze
echo "[2/5] Computing basic statistics..."
grep -v "^[#@]" "${OUTPUT_PREFIX}.xvg" | awk '{print $2}' > temp_values.dat
gmx analyze -f temp_values.dat -av -ee 2>&1 | tee "${OUTPUT_PREFIX}_stats.txt"
echo "✓ Statistics saved to ${OUTPUT_PREFIX}_stats.txt"

# Step 3: Python detailed analysis
echo "[3/5] Running detailed analysis..."
if command -v python3 &> /dev/null; then
    python3 analyze_temperature.py -f "${OUTPUT_PREFIX}.xvg" -t "$TARGET_TEMP" -o "${OUTPUT_PREFIX}"
    echo "✓ Detailed analysis complete"
else
    echo "⚠ Python3 not found; skipping detailed analysis"
fi

# Step 4: Quick validation checks
echo "[4/5] Running quick validation checks..."

# Extract mean from gmx analyze output
MEAN_TEMP=$(grep "Average" "${OUTPUT_PREFIX}_stats.txt" | awk '{print $2}')
STD_TEMP=$(grep "Std. Dev." "${OUTPUT_PREFIX}_stats.txt" | awk '{print $3}')

echo "  Mean temperature: $MEAN_TEMP K"
echo "  Standard deviation: $STD_TEMP K"

# Check against criteria
PASS=true

if (( $(echo "$MEAN_TEMP < 298 || $MEAN_TEMP > 302" | bc -l 2>/dev/null || echo 0) )); then
    echo "  ✗ FAIL: Mean temperature outside 300±2 K range"
    PASS=false
else
    echo "  ✓ PASS: Mean temperature within 300±2 K"
fi

if (( $(echo "$STD_TEMP > 10" | bc -l 2>/dev/null || echo 0) )); then
    echo "  ✗ FAIL: Standard deviation exceeds 10 K"
    PASS=false
else
    echo "  ✓ PASS: Standard deviation acceptable"
fi

# Check drift from linear fit
DRIFT=$(grep "Drift" "${OUTPUT_PREFIX}_stats.txt" 2>/dev/null | awk '{print $2}' || echo "0")
if (( $(echo "${DRIFT#-} > 2" | bc -l 2>/dev/null || echo 0) )); then
    echo "  ✗ FAIL: Temperature drift exceeds 2 K/ns"
    PASS=false
else
    echo "  ✓ PASS: Temperature drift acceptable"
fi

# Step 5: Summary
echo "[5/5] Validation summary"
echo "------------------------------------------"
if $PASS; then
    echo "✓ ALL CHECKS PASSED"
    echo "Temperature control is working correctly."
else
    echo "✗ SOME CHECKS FAILED"
    echo "Review the output files for details."
fi
echo "------------------------------------------"
echo "Output files:"
ls -lh "${OUTPUT_PREFIX}"* 2>/dev/null
echo ""
echo "Validation complete."

# Cleanup temporary files
rm -f temp_values.dat

exit 0
```

Run the complete validation:
```bash
chmod +x validate_temperature.sh
./validate_temperature.sh md.edr 300.0 temp_validation
```

---


