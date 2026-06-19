Here is a complete, reproducible GROMACS workflow for trajectory preprocessing (PBC correction, molecule making whole, centering, and cleaning) of a pure water simulation trajectory.

---

## 1. Overview of Trajectory Preprocessing

Proper preprocessing is **essential** before any analysis (RDF, MSD, diffusion, clustering, etc.). The workflow addresses:

1. **Making molecules whole** – Atoms of each molecule are kept together across PBC
2. **Removing PBC jumps** – Atoms move continuously without jumping across box boundaries  
3. **Centering** – System is centered in the box for visualization and analysis
4. **Compacting** – Removes unnecessary vacuum from the simulation box
5. **Optional:** Extracting subsets (e.g., only OW atoms), slicing time windows, reducing sampling frequency

---

## 2. Directory Setup and Required Files

```bash
# Create preprocessing directory
mkdir -p ~/water_preprocessing
cd ~/water_preprocessing

# Required input files (copy from your simulation):
# - md.xtc or md.trr    (trajectory)
# - md.tpr              (topology/run input, needed for atom names)
# - md.gro              (final configuration, optional)
# - topol.top           (topology, optional)
# - index.ndx           (index file, optional)

# Check your files
ls -lh md.xtc md.tpr md.gro 2>/dev/null
```

---

## 3. Create Comprehensive Index File

```bash
# Create index file with all needed groups
gmx make_ndx -f md.tpr -o index_full.ndx << EOF
a OW
name 18 OW_only
a HW1 HW2
name 19 HW_only
a OW HW1 HW2
name 20 All_atoms
del 0-17
q
EOF

# Verify index contents
gmx make_ndx -f md.tpr -n index_full.ndx -o index_check.ndx << EOF
q
EOF
cat index_full.ndx
```

**Expected index structure:**
```
[ OW_only ]
  1  4  7 10 ...  (OW atom numbers)
[ HW_only ]
  2  3  5  6  8  9 ... (HW atom numbers)
[ All_atoms ]
  1  2  3  4  5  6 ... (all atom numbers)
```

---

## 4. Complete Preprocessing Command Sequence

### 4.1 Step 1: Inspect Original Trajectory

```bash
# Check trajectory information
gmx check -f md.xtc 2>&1 | tee trajectory_info.txt

# Key things to check:
echo "=== Key Trajectory Properties ==="
gmx check -f md.xtc 2>&1 | grep -E "Precision|atoms|frames|time|box"
```

**Typical output:**
```
Reading frame 0 time 0.000
Precision of xtc file: 1000.000 (nm)
# Atoms: 648  (216 waters × 3 atoms)
Last frame time: 5000.000 ps
Total frames: 50001
```

### 4.2 Step 2: Make Molecules Whole (PBC treatment level 1)

This ensures atoms of each water molecule are in the same periodic image.

```bash
# Make molecules whole - atoms of same molecule stay together
gmx trjconv -f md.xtc -s md.tpr -o step1_whole.xtc -pbc mol -ur compact << EOF
System
EOF

echo "✓ Molecules made whole - saved as step1_whole.xtc"
```

**Explanation:**
- `-pbc mol`: Puts atoms of the same molecule together (no bond broken across PBC)
- `-ur compact`: Centers the system in a compact box
- `System`: Selects the whole system for processing

### 4.3 Step 3: Remove PBC Jumps (PBC treatment level 2)

Removes jumps when molecules cross periodic boundaries.

```bash
# Remove jumps across PBC - creates continuous trajectory
gmx trjconv -f step1_whole.xtc -s md.tpr -o step2_nojump.xtc -pbc nojump -ur compact << EOF
System
EOF

echo "✓ PBC jumps removed - saved as step2_nojump.xtc"
```

**Explanation:**
- `-pbc nojump`: Removes jumps of atoms across the box (essential for MSD/diffusion)
- Atoms coordinates become continuous (not wrapped to 0 to L)

### 4.4 Step 4: Center the System

Center the system on a specific group for visualization and analysis.

```bash
# Center system on the center of mass of all atoms
gmx trjconv -f step2_nojump.xtc -s md.tpr -o step3_centered.xtc \
    -pbc mol -center -ur compact << EOF
System
System
EOF

echo "✓ System centered - saved as step3_centered.xtc"
```

**Options:**
- `-center`: Centers the system on the center of mass of the selected group
- First prompt: Group to center on (System = all atoms)
- Second prompt: Group to output (System = all atoms)

### 4.5 Step 5: Fit to Reference (Optional - Remove Rotation)

For analyses sensitive to overall rotation (e.g., protein domains), fit to a reference.

```bash
# For pure water, this is usually not needed, but included for completeness
# If you had a protein: fit to protein backbone
gmx trjconv -f step3_centered.xtc -s md.tpr -o step4_fitted.xtc \
    -fit rot+trans << EOF
OW_only
System
EOF

echo "✓ Rotation/translation removed (if needed) - saved as step4_fitted.xtc"
```

### 4.6 Step 6: Extract Subset (OW atoms only for RDF/MSD analysis)

```bash
# Extract only OW atoms (reduces file size, speeds up analysis)
gmx trjconv -f step3_centered.xtc -s md.tpr -n index_full.ndx \
    -o step5_OW_only.xtc << EOF
OW_only
EOF

echo "✓ OW-only trajectory extracted - saved as step5_OW_only.xtc"
```

### 4.7 Step 7: Slice Time Window (Optional)

Extract a specific time range, e.g., discard equilibration period.

```bash
# Extract production portion only (e.g., 200-1000 ps)
gmx trjconv -f step5_OW_only.xtc -s md.tpr -n index_full.ndx \
    -o step6_OW_production.xtc -b 200 -e 1000 << EOF
OW_only
EOF

echo "✓ Production time window extracted (200-1000 ps)"
```

### 4.8 Step 8: Reduce Frame Frequency (Optional)

Reduce the number of frames for faster processing.

```bash
# Keep every 5th frame (reduce sampling)
gmx trjconv -f step6_OW_production.xtc -s md.tpr -n index_full.ndx \
    -o step7_OW_reduced.xtc -skip 5 << EOF
OW_only
EOF

echo "✓ Frame frequency reduced (every 5th frame)"
```

### 4.9 Step 9: Generate Final Clean GRO File

```bash
# Extract final frame as reference structure
gmx trjconv -f step6_OW_production.xtc -s md.tpr -n index_full.ndx \
    -o final_reference.gro -dump 1000 << EOF
OW_only
EOF

echo "✓ Reference structure extracted - saved as final_reference.gro"
```

---

## 5. Complete Automated Preprocessing Script

Save as `preprocess_trajectory.sh`:

```bash
#!/bin/bash
# ============================================================
# Complete GROMACS Trajectory Preprocessing Workflow
# For pure water simulation
# ============================================================
set -e

# Input files
TRAJ_IN="md.xtc"
TPR_IN="md.tpr"
GRO_IN="md.gro"

# Output files
TRAJ_FINAL="trajectory_clean.xtc"
GRO_FINAL="system_clean.gro"
INDEX_FILE="index_clean.ndx"
LOG_FILE="preprocessing.log"

# Time range (ps) - set to 0 and -1 to keep whole trajectory
TIME_START=0
TIME_END=-1      # -1 means end of trajectory

# Frame skip (1 = keep all frames)
FRAME_SKIP=1

# Center group
CENTER_GROUP="System"

# Subset extraction (leave empty to keep all atoms)
EXTRACT_GROUP="OW_only"

echo "=========================================="
echo " TRAJECTORY PREPROCESSING WORKFLOW"
echo "=========================================="
echo "Input trajectory: $TRAJ_IN"
echo "Topology: $TPR_IN"
echo ""

# Check for required files
for f in "$TRAJ_IN" "$TPR_IN"; do
    if [ ! -f "$f" ]; then
        echo "ERROR: Required file '$f' not found."
        exit 1
    fi
done

# Initialize log
echo "Preprocessing started: $(date)" > $LOG_FILE

# ============================================
# Step 1: Trajectory Information
# ============================================
echo "[1/9] Inspecting trajectory..."
echo "=== Trajectory Information ===" >> $LOG_FILE
gmx check -f $TRAJ_IN 2>&1 | tee -a $LOG_FILE

# Extract key info
N_ATOMS=$(gmx check -f $TRAJ_IN 2>&1 | grep "atoms:" | awk '{print $2}')
N_FRAMES=$(gmx check -f $TRAJ_IN 2>&1 | grep "frames:" | awk '{print $2}')
echo "  Atoms: $N_ATOMS" | tee -a $LOG_FILE
echo "  Frames: $N_FRAMES" | tee -a $LOG_FILE

# ============================================
# Step 2: Create Index File
# ============================================
echo "[2/9] Creating index file..."
gmx make_ndx -f $TPR_IN -o $INDEX_FILE << EOF 2>> $LOG_FILE
a OW
name 18 OW_only
a HW1 HW2
name 19 HW_only
a OW HW1 HW2
name 20 All_atoms
q
EOF
echo "  ✓ Index created: $INDEX_FILE" | tee -a $LOG_FILE

# ============================================
# Step 3: Make Molecules Whole
# ============================================
echo "[3/9] Making molecules whole..."
gmx trjconv -f $TRAJ_IN -s $TPR_IN \
    -o temp_whole.xtc \
    -pbc mol -ur compact << EOF 2>> $LOG_FILE
System
EOF
echo "  ✓ Molecules made whole" | tee -a $LOG_FILE

# ============================================
# Step 4: Remove PBC Jumps
# ============================================
echo "[4/9] Removing PBC jumps..."
gmx trjconv -f temp_whole.xtc -s $TPR_IN \
    -o temp_nojump.xtc \
    -pbc nojump -ur compact << EOF 2>> $LOG_FILE
System
EOF
echo "  ✓ PBC jumps removed" | tee -a $LOG_FILE

# ============================================
# Step 5: Center System
# ============================================
echo "[5/9] Centering system..."
gmx trjconv -f temp_nojump.xtc -s $TPR_IN \
    -o temp_centered.xtc \
    -pbc mol -center -ur compact << EOF 2>> $LOG_FILE
$CENTER_GROUP
System
EOF
echo "  ✓ System centered on $CENTER_GROUP" | tee -a $LOG_FILE

# ============================================
# Step 6: Extract Time Range (if specified)
# ============================================
if [ "$TIME_START" != "0" ] || [ "$TIME_END" != "-1" ]; then
    echo "[6/9] Extracting time range: $TIME_START to $TIME_END ps..."
    TIME_FLAGS="-b $TIME_START"
    if [ "$TIME_END" != "-1" ]; then
        TIME_FLAGS="$TIME_FLAGS -e $TIME_END"
    fi
    
    gmx trjconv -f temp_centered.xtc -s $TPR_IN -n $INDEX_FILE \
        -o temp_timerange.xtc $TIME_FLAGS << EOF 2>> $LOG_FILE
All_atoms
EOF
    
    # Replace centered with time-ranged version
    mv temp_timerange.xtc temp_centered.xtc
    echo "  ✓ Time range extracted" | tee -a $LOG_FILE
else
    echo "[6/9] Keeping full time range (0 to end)" | tee -a $LOG_FILE
fi

# ============================================
# Step 7: Reduce Frame Frequency (if specified)
# ============================================
if [ "$FRAME_SKIP" -gt 1 ]; then
    echo "[7/9] Reducing frame frequency (keep every ${FRAME_SKIP}th frame)..."
    gmx trjconv -f temp_centered.xtc -s $TPR_IN -n $INDEX_FILE \
        -o temp_reduced.xtc -skip $FRAME_SKIP << EOF 2>> $LOG_FILE
All_atoms
EOF
    mv temp_reduced.xtc temp_centered.xtc
    echo "  ✓ Frame frequency reduced" | tee -a $LOG_FILE
else
    echo "[7/9] Keeping all frames (no reduction)" | tee -a $LOG_FILE
fi

# ============================================
# Step 8: Extract Subset (if specified)
# ============================================
if [ -n "$EXTRACT_GROUP" ]; then
    echo "[8/9] Extracting atom subset: $EXTRACT_GROUP..."
    gmx trjconv -f temp_centered.xtc -s $TPR_IN -n $INDEX_FILE \
        -o $TRAJ_FINAL << EOF 2>> $LOG_FILE
$EXTRACT_GROUP
EOF
    echo "  ✓ Subset extracted: $EXTRACT_GROUP" | tee -a $LOG_FILE
else
    echo "[8/9] Keeping all atoms (no subset)" | tee -a $LOG_FILE
    mv temp_centered.xtc $TRAJ_FINAL
fi

# ============================================
# Step 9: Extract Final Frame as GRO
# ============================================
echo "[9/9] Extracting final reference structure..."
gmx trjconv -f $TRAJ_FINAL -s $TPR_IN -n $INDEX_FILE \
    -o $GRO_FINAL -dump -1 << EOF 2>> $LOG_FILE
${EXTRACT_GROUP:-System}
EOF
echo "  ✓ Reference structure: $GRO_FINAL" | tee -a $LOG_FILE

# ============================================
# Cleanup and Validation
# ============================================
echo ""
echo "=== Cleaning temporary files ==="
rm -f temp_*.xtc

echo ""
echo "=========================================="
echo " PREPROCESSING COMPLETE"
echo "=========================================="
echo "Final trajectory: $TRAJ_FINAL"
echo "Final structure: $GRO_FINAL"
echo "Index file: $INDEX_FILE"
echo "Log file: $LOG_FILE"
echo ""

# Validate final trajectory
echo "=== Final Trajectory Information ===" | tee -a $LOG_FILE
gmx check -f $TRAJ_FINAL 2>&1 | tee -a $LOG_FILE

FINAL_FRAMES=$(gmx check -f $TRAJ_FINAL 2>&1 | grep "frames:" | awk '{print $2}')
echo "  Final frames: $FINAL_FRAMES (input had $N_FRAMES)" | tee -a $LOG_FILE

echo ""
echo "Preprocessing completed successfully at $(date)" | tee -a $LOG_FILE
```

---

## 6. Alternative: Single-Command Preprocessing Chain

For quick preprocessing, you can chain commands with pipes:

```bash
# All-in-one preprocessing (if you don't need intermediate files)
gmx trjconv -f md.xtc -s md.tpr -o trajectory_clean.xtc \
    -pbc nojump -center -ur compact << EOF
System
System
EOF

# For OW-only trajectory in one step
gmx trjconv -f md.xtc -s md.tpr -o trajectory_OW_clean.xtc \
    -pbc nojump -center -ur compact << EOF
OW_only
OW_only
EOF

# With time range and frame skip
gmx trjconv -f md.xtc -s md.tpr -o trajectory_clean_final.xtc \
    -pbc nojump -center -ur compact -b 200 -e 1000 -skip 5 << EOF
OW_only
OW_only
EOF
```

---

## 7. Validation of Preprocessed Trajectory

### 7.1 Automated Validation Script

Save as `validate_preprocessing.py`:

```python
#!/usr/bin/env python3
"""
Validate preprocessed trajectory:
- Check for PBC jumps
- Verify molecules are whole
- Confirm centering quality
- Check for coordinate artifacts
"""
import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis import distances
import argparse
import matplotlib.pyplot as plt

def validate_pbc_removal(universe, max_jump_threshold=0.5):
    """
    Check if any atoms have jumps larger than threshold.
    For unwrapped trajectories, jumps should be continuous (no big jumps).
    """
    print("\n=== PBC Removal Validation ===")
    
    oxygens = universe.select_atoms('name OW')
    n_atoms = len(oxygens)
    
    # Track positions of first 10 atoms
    n_check = min(10, n_atoms)
    positions = np.zeros((len(universe.trajectory), n_check, 3))
    
    for ts in universe.trajectory:
        positions[ts.frame, :, :] = oxygens[:n_check].positions
    
    # Calculate frame-to-frame displacements
    jumps_detected = 0
    max_displacement = 0
    
    for i in range(n_check):
        disp = np.sqrt(np.sum(np.diff(positions[:, i, :], axis=0)**2, axis=1))
        max_disp = np.max(disp)
        max_displacement = max(max_displacement, max_disp)
        
        # Check for suspicious jumps (> half box size)
        box_size = universe.dimensions[0]
        if max_disp > box_size * 0.5:
            jumps_detected += 1
            print(f"  ✗ Atom {i}: Large jump detected ({max_disp:.2f} nm > {box_size*0.5:.2f} nm)")
    
    if jumps_detected == 0:
        print(f"  ✓ No PBC jumps detected")
        print(f"  Maximum frame-to-frame displacement: {max_displacement:.3f} nm")
    else:
        print(f"  ✗ {jumps_detected}/{n_check} atoms show potential PBC jumps")
    
    return jumps_detected == 0

def validate_whole_molecules(universe, bond_tolerance=0.12):
    """
    Check if water molecules are intact (O-H bond ~0.1 nm).
    """
    print("\n=== Whole Molecule Validation ===")
    
    # Select first water molecule
    all_atoms = universe.select_atoms('all')
    n_waters = len(all_atoms) // 3
    
    # Check first 50 molecules
    n_check = min(50, n_waters)
    broken_count = 0
    
    for i in range(n_check):
        ow = all_atoms[i*3]
        hw1 = all_atoms[i*3 + 1]
        hw2 = all_atoms[i*3 + 2]
        
        # Check bonds over first frame
        d1 = np.linalg.norm(ow.position - hw1.position)
        d2 = np.linalg.norm(ow.position - hw2.position)
        
        if abs(d1 - 0.1) > bond_tolerance:
            broken_count += 1
        if abs(d2 - 0.1) > bond_tolerance:
            broken_count += 1
    
    if broken_count == 0:
        print(f"  ✓ All checked molecules are whole (bond lengths correct)")
    else:
        print(f"  ✗ {broken_count} bonds appear broken across PBC")
    
    return broken_count == 0

def validate_centering(universe, tolerance=0.5):
    """
    Check if system is properly centered (COM near box center).
    """
    print("\n=== Centering Validation ===")
    
    box = universe.dimensions
    box_center = box[:3] / 2
    
    com_displacements = []
    
    for ts in universe.trajectory:
        all_atoms = universe.select_atoms('all')
        com = all_atoms.center_of_mass()
        displacement = np.linalg.norm(com - box_center)
        com_displacements.append(displacement)
    
    com_displacements = np.array(com_displacements)
    max_disp = np.max(com_displacements)
    mean_disp = np.mean(com_displacements)
    
    if max_disp < tolerance:
        print(f"  ✓ System properly centered")
        print(f"  Mean COM displacement from box center: {mean_disp:.3f} nm")
        print(f"  Max COM displacement: {max_disp:.3f} nm")
    else:
        print(f"  ⚠ System may not be well-centered")
        print(f"  Max COM displacement: {max_disp:.3f} nm (threshold: {tolerance} nm)")
    
    return max_disp < tolerance

def validate_coordinate_continuity(universe, n_check_atoms=5):
    """
    Check coordinate continuity for unwrapped trajectories.
    Coordinates should change smoothly without large jumps.
    """
    print("\n=== Coordinate Continuity Validation ===")
    
    oxygens = universe.select_atoms('name OW')
    
    fig, axes = plt.subplots(n_check_atoms, 1, figsize=(12, 2*n_check_atoms))
    
    for i in range(n_check_atoms):
        positions = np.zeros((len(universe.trajectory), 3))
        for ts in universe.trajectory:
            positions[ts.frame] = oxygens[i].position
        
        time = np.arange(len(positions)) * universe.trajectory.dt
        
        axes[i].plot(time, positions[:, 0], 'r-', label='X', linewidth=0.5)
        axes[i].plot(time, positions[:, 1], 'g-', label='Y', linewidth=0.5)
        axes[i].plot(time, positions[:, 2], 'b-', label='Z', linewidth=0.5)
        axes[i].set_ylabel(f'OW {i}\nPosition (nm)')
        axes[i].legend(fontsize=6, loc='upper right')
        axes[i].grid(True, alpha=0.3)
        
        # Check for discontinuities
        disp = np.sqrt(np.sum(np.diff(positions, axis=0)**2, axis=1))
        max_jump = np.max(disp)
        
        if max_jump > 1.0:
            axes[i].set_title(f'OW {i}: ⚠ Large jump detected ({max_jump:.2f} nm)', 
                            color='red')
        else:
            axes[i].set_title(f'OW {i}: Smooth trajectory (max step: {max_jump:.3f} nm)')
    
    axes[-1].set_xlabel('Time (ps)')
    
    plt.suptitle('Coordinate Continuity Check', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('coordinate_continuity.png', dpi=150)
    plt.close()
    
    print(f"  ✓ Continuity plot saved as 'coordinate_continuity.png'")
    print(f"  Check the plot: trajectories should be smooth without sharp jumps")

def generate_validation_summary(universe, output='validation_summary.txt'):
    """Generate comprehensive validation report."""
    
    with open(output, 'w') as f:
        f.write("="*60 + "\n")
        f.write(" TRAJECTORY PREPROCESSING VALIDATION REPORT\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Trajectory file: {universe.filename}\n")
        f.write(f"Number of atoms: {len(universe.atoms)}\n")
        f.write(f"Number of frames: {len(universe.trajectory)}\n")
        f.write(f"Time range: {universe.trajectory[0].time:.1f} - "
                f"{universe.trajectory[-1].time:.1f} ps\n")
        f.write(f"Box dimensions: {universe.dimensions[0]:.4f} × "
                f"{universe.dimensions[1]:.4f} × {universe.dimensions[2]:.4f} nm\n\n")
        
        # Run validations
        f.write("VALIDATION RESULTS:\n")
        f.write("-"*60 + "\n")
        
        # PBC check
        f.write("\nPBC Removal: ")
        pbc_ok = validate_pbc_removal(universe)
        f.write("PASS\n" if pbc_ok else "FAIL\n")
        
        # Whole molecules check
        f.write("\nWhole Molecules: ")
        mol_ok = validate_whole_molecules(universe)
        f.write("PASS\n" if mol_ok else "FAIL\n")
        
        # Centering check
        f.write("\nCentering: ")
        cent_ok = validate_centering(universe)
        f.write("PASS\n" if cent_ok else "WARNING\n")
        
        f.write("\n" + "="*60 + "\n")
        all_ok = pbc_ok and mol_ok and cent_ok
        f.write(f"OVERALL: {'PASS' if all_ok else 'ISSUES DETECTED'}\n")
        f.write("="*60 + "\n")
    
    print(f"\n✓ Validation summary saved to '{output}'")
    return all_ok

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Validate preprocessed GROMACS trajectory')
    parser.add_argument('-f', '--trajectory', required=True,
                       help='Preprocessed trajectory file')
    parser.add_argument('-s', '--topology', required=True,
                       help='Topology/TPR file')
    parser.add_argument('-o', '--output', default='validation_summary.txt',
                       help='Output summary file')
    
    args = parser.parse_args()
    
    print(f"\nLoading trajectory: {args.trajectory}")
    u = mda.Universe(args.topology, args.trajectory)
    
    print(f"  Atoms: {len(u.atoms)}")
    print(f"  Frames: {len(u.trajectory)}")
    
    # Run validations
    pbc_ok = validate_pbc_removal(u)
    mol_ok = validate_whole_molecules(u)
    cent_ok = validate_centering(u)
    validate_coordinate_continuity(u)
    
    # Generate report
    all_ok = generate_validation_summary(u, args.output)
    
    print("\n" + "="*60)
    if all_ok:
        print(" ✓ ALL VALIDATION CHECKS PASSED")
        print(" Trajectory is ready for analysis.")
    else:
        print(" ⚠ SOME CHECKS FAILED OR NEED ATTENTION")
        print(" Review the validation summary for details.")
    print("="*60 + "\n")
```

### 7.2 Run Validation

```bash
# Run validation on cleaned trajectory
python3 validate_preprocessing.py \
    -f trajectory_clean.xtc \
    -s md.tpr \
    -o validation_report.txt

# View report
cat validation_report.txt
```

---

## 8. Expected Output Files

| File | Description | Size (typical) |
|------|-------------|----------------|
| `trajectory_clean.xtc` | Final preprocessed trajectory | 10-100 MB |
| `system_clean.gro` | Final frame reference structure | < 1 MB |
| `index_clean.ndx` | Index file with atom groups | < 1 KB |
| `preprocessing.log` | Log of all operations | < 1 MB |
| `validation_report.txt` | Validation results | < 10 KB |
| `coordinate_continuity.png` | Continuity check plot | < 1 MB |

**Intermediate files (can be deleted):**
- `step1_whole.xtc`
- `step2_nojump.xtc`
- `step3_centered.xtc`
- `step5_OW_only.xtc` (etc.)

---

## 9. Quick Validation Commands

```bash
# 1. Check file sizes (should decrease with each step)
ls -lh md.xtc step*_*.xtc trajectory_clean.xtc 2>/dev/null

# 2. Quick check for PBC jumps in cleaned trajectory
python3 -c "
import MDAnalysis as mda
import numpy as np
u = mda.Universe('md.tpr', 'trajectory_clean.xtc')
ow = u.select_atoms('name OW')
pos0 = ow[0].position
max_disp = 0
for ts in u.trajectory:
    disp = np.linalg.norm(ow[0].position - pos0)
    max_disp = max(max_disp, disp)
    pos0 = ow[0].position.copy()
print(f'Max net displacement of OW[0]: {max_disp:.2f} nm')
print(f'If >> box size, unwrapping successful.')
"

# 3. Count frames before and after
echo "Original frames: $(gmx check -f md.xtc 2>&1 | grep frames)"
echo "Cleaned frames:  $(gmx check -f trajectory_clean.xtc 2>&1 | grep frames)"

# 4. Check O-H bond lengths in first frame
python3 -c "
import MDAnalysis as mda
import numpy as np
u = mda.Universe('md.tpr', 'trajectory_clean.xtc')
u.trajectory[0]
all_atoms = u.select_atoms('all')
n_waters = len(all_atoms) // 3
broken = 0
for i in range(n_waters):
    ow = all_atoms[i*3]
    hw1 = all_atoms[i*3+1]
    hw2 = all_atoms[i*3+2]
    d1 = np.linalg.norm(ow.position - hw1.position)
    d2 = np.linalg.norm(ow.position - hw2.position)
    if abs(d1 - 0.1) > 0.02 or abs(d2 - 0.1) > 0.02:
        broken += 1
if broken == 0:
    print('✓ All O-H bonds intact (molecules are whole)')
else:
    print(f'✗ {broken} molecules have broken bonds')
"
```

---

## 10. Common Errors and Solutions

### 10.1 Input File Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `File not found` | Missing trajectory or TPR | Verify file paths; check directory |
| `Cannot open TPR file` | Corrupted TPR or wrong GROMACS version | TPR must match trajectory |
| `Atom index out of range` | Wrong number of atoms | Check if trajectory matches topology |
| `No atoms selected` | Empty group in trjconv | Use correct index group name |

### 10.2 PBC Processing Errors

| Error/Symptom | Cause | Solution |
|---------------|-------|----------|
| Molecules split across box after `-pbc mol` | Some molecules were broken in initial frame | Use `-pbc atom` instead, then `-pbc mol` |
| MSD still shows jumps after `-pbc nojump` | Molecules were not made whole first | Always run `-pbc mol` before `-pbc nojump` |
| System drifts away | COM motion not removed | Use `-center` option |
| Vacuum appears in box after centering | `-ur compact` not used | Add `-ur compact` to compact box |

### 10.3 Centering Errors

| Error | Cause | Solution |
|-------|-------|----------|
| System not centered on desired group | Wrong group selected | Select specific group (e.g., protein, OW_only) |
| Box size changes after centering | `-box` option inadvertently used | Do not use `-box` unless intentional |
| System rotates during trajectory | Normal for isotropic systems | Use `-fit rot+trans` if rotation is problematic |

### 10.4 Extraction Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Extracted group has wrong number of atoms | Wrong selection syntax | Use `name OW` not `atom OW`; check index |
| Time range extraction gives empty trajectory | `-b` time > trajectory length | Check trajectory length with `gmx check` |
| `-skip` removes too many frames | Too large skip value | Frames_after = Frames_before / skip |

### 10.5 Common Warning Messages

| Warning | Meaning | Action |
|---------|---------|--------|
| `WARNING: PBC - Not all atoms are within the box` | Expected for unwrapped trajectories | Ignore if using `-pbc nojump` |
| `The XTC file is corrupted at frame X` | Damaged trajectory file | Check disk space; regenerate trajectory |
| `Velocity scaling factor exceeds 100%` | Normal for PBC removal | Can be safely ignored |
| `Will write an XTC file with reduced precision` | Precision reduction from TRR to XTC | Use `-ndec` option to control precision |

---

## 11. Best Practices Summary

1. **Always inspect the original trajectory** with `gmx check` before preprocessing
2. **Order matters:** Make whole → Remove jumps → Center → Extract
3. **Keep intermediate files** during development; delete for production
4. **Use `-ur compact`** to remove unnecessary vacuum
5. **Validate the final trajectory** before analysis
6. **Document all preprocessing steps** in your methods section
7. **Use index files** for reproducible atom selection
8. **For MSD/diffusion:** Must use `-pbc nojump` on whole molecules
9. **For RDF:** `-pbc mol` is usually sufficient
10. **For visualization:** Always center on the molecule of interest

---

## 12. Processing Decision Tree

```
┌─────────────────────────────────┐
│   What analysis are you doing?  │
└─────────────────────────────────┘
                │
        ┌───────┼───────────┬──────────────┐
        │       │           │              │
     [RDF]   [MSD/D]   [Clustering]  [Visualization]
        │       │           │              │
        ▼       ▼           ▼              ▼
    -pbc mol  -pbc mol   -pbc mol      -pbc mol
    (centered) -pbc nojump -center      -center
               -center    -pbc nojump   -fit (optional)
               (OW only)  -center
                          (subset)
```

---


