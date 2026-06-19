import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
GSCF = BASE / "data" / "gscf_dataset"
GEQS = BASE / "data" / "geqs_dataset"
GSCF.mkdir(parents=True, exist_ok=True)
GEQS.mkdir(parents=True, exist_ok=True)

gscf_records = [
    ("GSCF_011", "rmsd_backbone", "Generate a GROMACS workflow to calculate RMSD of a protein backbone trajectory.", "gmx rms -s md.tpr -f md.xtc -o rmsd_backbone.xvg", "rmsd_backbone.xvg"),
    ("GSCF_012", "rmsf_residue", "Generate a GROMACS workflow to calculate residue-wise RMSF from a protein trajectory.", "gmx rmsf -s md.tpr -f md.xtc -o rmsf_residue.xvg -res", "rmsf_residue.xvg"),
    ("GSCF_013", "radius_of_gyration", "Generate a GROMACS workflow to calculate radius of gyration of a protein.", "gmx gyrate -s md.tpr -f md.xtc -o gyrate.xvg", "gyrate.xvg"),
    ("GSCF_014", "sasa_protein", "Generate a GROMACS workflow to calculate solvent accessible surface area of a protein.", "gmx sasa -s md.tpr -f md.xtc -o sasa.xvg", "sasa.xvg"),
    ("GSCF_015", "mindist_protein_ligand", "Generate a GROMACS workflow to calculate minimum distance between protein and ligand.", "gmx mindist -s md.tpr -f md.xtc -od mindist.xvg", "mindist.xvg"),
    ("GSCF_016", "cluster_analysis", "Generate a GROMACS workflow for cluster analysis of trajectory conformations.", "gmx cluster -s md.tpr -f md.xtc -o clusters.xpm -g cluster.log", "clusters.xpm; cluster.log"),
    ("GSCF_017", "distance_between_groups", "Generate a GROMACS workflow to calculate distance between two selected groups.", "gmx distance -s md.tpr -f md.xtc -oall distance.xvg", "distance.xvg"),
    ("GSCF_018", "angle_analysis", "Generate a GROMACS workflow to calculate angle distribution from selected atom groups.", "gmx angle -f md.xtc -n index.ndx -ov angle.xvg", "angle.xvg"),
    ("GSCF_019", "dihedral_analysis", "Generate a GROMACS workflow to calculate dihedral angle distribution.", "gmx angle -type dihedral -f md.xtc -n index.ndx -ov dihedral.xvg", "dihedral.xvg"),
    ("GSCF_020", "principal_components", "Generate a GROMACS workflow for covariance and principal component analysis.", "gmx covar -s md.tpr -f md.xtc -o eigenval.xvg -v eigenvec.trr", "eigenval.xvg; eigenvec.trr"),
    ("GSCF_021", "free_volume_box", "Generate a GROMACS workflow to extract box volume time series from an energy file.", "echo Volume | gmx energy -f md.edr -o volume.xvg", "volume.xvg"),
    ("GSCF_022", "pressure_time_series", "Generate a GROMACS workflow to extract pressure time series from an energy file.", "echo Pressure | gmx energy -f md.edr -o pressure.xvg", "pressure.xvg"),
    ("GSCF_023", "potential_energy", "Generate a GROMACS workflow to extract potential energy time series.", "echo Potential | gmx energy -f md.edr -o potential.xvg", "potential.xvg"),
    ("GSCF_024", "kinetic_energy", "Generate a GROMACS workflow to extract kinetic energy time series.", "echo Kinetic-En. | gmx energy -f md.edr -o kinetic_energy.xvg", "kinetic_energy.xvg"),
    ("GSCF_025", "total_energy", "Generate a GROMACS workflow to extract total energy time series.", "echo Total-Energy | gmx energy -f md.edr -o total_energy.xvg", "total_energy.xvg"),
    ("GSCF_026", "enthalpy", "Generate a GROMACS workflow to extract enthalpy time series.", "echo Enthalpy | gmx energy -f md.edr -o enthalpy.xvg", "enthalpy.xvg"),
    ("GSCF_027", "box_dimensions", "Generate a GROMACS workflow to extract box dimensions from an energy file.", "echo Box-X Box-Y Box-Z | gmx energy -f md.edr -o box_dimensions.xvg", "box_dimensions.xvg"),
    ("GSCF_028", "density_profile_x", "Generate a GROMACS workflow to calculate density profile along x direction.", "echo System | gmx density -f md.xtc -s md.tpr -o density_profile_x.xvg -d X -sl 100", "density_profile_x.xvg"),
    ("GSCF_029", "density_profile_y", "Generate a GROMACS workflow to calculate density profile along y direction.", "echo System | gmx density -f md.xtc -s md.tpr -o density_profile_y.xvg -d Y -sl 100", "density_profile_y.xvg"),
    ("GSCF_030", "number_density_profile", "Generate a GROMACS workflow to calculate number density profile along z direction.", "echo System | gmx density -f md.xtc -s md.tpr -o number_density_z.xvg -d Z -sl 100 -dens number", "number_density_z.xvg"),
    ("GSCF_031", "rdf_li_oxygen", "Generate a GROMACS workflow to calculate Li-O radial distribution function.", 'gmx rdf -f md.xtc -s md.tpr -o rdf_Li_OW.xvg -ref "name LI" -sel "name OW"', "rdf_Li_OW.xvg"),
    ("GSCF_032", "rdf_br_oxygen", "Generate a GROMACS workflow to calculate Br-O radial distribution function.", 'gmx rdf -f md.xtc -s md.tpr -o rdf_Br_OW.xvg -ref "name BR" -sel "name OW"', "rdf_Br_OW.xvg"),
    ("GSCF_033", "coordination_li_oxygen", "Generate a GROMACS workflow to calculate Li-O coordination number from RDF.", 'gmx rdf -f md.xtc -s md.tpr -o rdf_Li_OW.xvg -cn cn_Li_OW.xvg -ref "name LI" -sel "name OW"', "rdf_Li_OW.xvg; cn_Li_OW.xvg"),
    ("GSCF_034", "coordination_br_oxygen", "Generate a GROMACS workflow to calculate Br-O coordination number from RDF.", 'gmx rdf -f md.xtc -s md.tpr -o rdf_Br_OW.xvg -cn cn_Br_OW.xvg -ref "name BR" -sel "name OW"', "rdf_Br_OW.xvg; cn_Br_OW.xvg"),
    ("GSCF_035", "hydrogen_bond_water", "Generate a GROMACS workflow to calculate hydrogen bonds in water.", "gmx hbond -f md.xtc -s md.tpr -num hbond_water.xvg", "hbond_water.xvg"),
    ("GSCF_036", "hydrogen_bond_protein_water", "Generate a GROMACS workflow to calculate hydrogen bonds between protein and water.", "gmx hbond -f md.xtc -s md.tpr -num hbond_protein_water.xvg", "hbond_protein_water.xvg"),
    ("GSCF_037", "index_generation", "Generate a GROMACS workflow to create an index file for custom groups.", "gmx make_ndx -f md.gro -o index.ndx", "index.ndx"),
    ("GSCF_038", "trajectory_centering", "Generate a GROMACS workflow to center a trajectory in the simulation box.", "echo Protein System | gmx trjconv -s md.tpr -f md.xtc -o md_center.xtc -center -pbc mol", "md_center.xtc"),
    ("GSCF_039", "trajectory_whole_molecules", "Generate a GROMACS workflow to make molecules whole across periodic boundaries.", "echo System | gmx trjconv -s md.tpr -f md.xtc -o md_whole.xtc -pbc mol", "md_whole.xtc"),
    ("GSCF_040", "trajectory_nojump", "Generate a GROMACS workflow to remove jumps across periodic boundaries.", "echo System | gmx trjconv -s md.tpr -f md.xtc -o md_nojump.xtc -pbc nojump", "md_nojump.xtc"),
    ("GSCF_041", "trajectory_fit", "Generate a GROMACS workflow to fit a trajectory to a reference structure.", "echo Backbone System | gmx trjconv -s md.tpr -f md.xtc -o md_fit.xtc -fit rot+trans", "md_fit.xtc"),
    ("GSCF_042", "trajectory_stride", "Generate a GROMACS workflow to reduce trajectory frame frequency.", "gmx trjconv -s md.tpr -f md.xtc -o md_stride.xtc -dt 10", "md_stride.xtc"),
    ("GSCF_043", "energy_minimization_workflow", "Generate a GROMACS workflow for energy minimization.", "gmx grompp -f minim.mdp -c system.gro -p topol.top -o em.tpr\ngmx mdrun -deffnm em", "em.tpr; em.gro; em.edr; em.log"),
    ("GSCF_044", "nvt_equilibration_workflow", "Generate a GROMACS workflow for NVT equilibration.", "gmx grompp -f nvt.mdp -c em.gro -p topol.top -o nvt.tpr\ngmx mdrun -deffnm nvt", "nvt.tpr; nvt.gro; nvt.edr; nvt.log"),
    ("GSCF_045", "npt_equilibration_workflow", "Generate a GROMACS workflow for NPT equilibration using C-rescale barostat.", "gmx grompp -f npt.mdp -c nvt.gro -p topol.top -o npt.tpr\ngmx mdrun -deffnm npt", "npt.tpr; npt.gro; npt.edr; npt.log"),
    ("GSCF_046", "production_md_workflow", "Generate a GROMACS workflow for production MD after equilibration.", "gmx grompp -f md.mdp -c npt.gro -p topol.top -o md.tpr\ngmx mdrun -deffnm md", "md.tpr; md.xtc; md.edr; md.log"),
    ("GSCF_047", "solvation_workflow", "Generate a GROMACS workflow to solvate a system and update topology.", "gmx solvate -cp solute.gro -cs spc216.gro -o solvated.gro -p topol.top", "solvated.gro; updated topol.top"),
    ("GSCF_048", "ion_addition_workflow", "Generate a GROMACS workflow to add ions and neutralize a solvated system.", "gmx grompp -f ions.mdp -c solvated.gro -p topol.top -o ions.tpr\ngmx genion -s ions.tpr -o solv_ions.gro -p topol.top -neutral", "ions.tpr; solv_ions.gro; updated topol.top"),
    ("GSCF_049", "pbc_rdf_ready_workflow", "Generate a GROMACS workflow to prepare a trajectory for RDF analysis.", "echo System | gmx trjconv -s md.tpr -f md.xtc -o md_whole.xtc -pbc mol", "md_whole.xtc"),
    ("GSCF_050", "pbc_msd_ready_workflow", "Generate a GROMACS workflow to prepare a trajectory for MSD analysis.", "echo System | gmx trjconv -s md.tpr -f md.xtc -o md_nojump.xtc -pbc nojump", "md_nojump.xtc"),
]

def write_gscf(record):
    rid, name, task, command, output = record
    path = GSCF / f"{rid.lower()}_{name}.json"
    data = {
        "id": rid,
        "task_name": name,
        "dataset": "GSCF",
        "status": "curated_workflow_template_not_all_executed",
        "user_task": task,
        "required_input_files": [
            "topol.top",
            "coordinate file such as .gro",
            "trajectory file such as .xtc when required",
            "run input file such as .tpr when required",
            "energy file such as .edr when required"
        ],
        "workflow": {
            "topology_check": "Verify that topol.top exists and that the [ molecules ] section matches the coordinate file.",
            "command_sequence": command,
            "expected_outputs": output
        },
        "common_errors": [
            "missing topology file",
            "wrong molecule count after solvation",
            "wrong atom or group selection",
            "invalid GROMACS option",
            "missing validation note",
            "short trajectory used without warning"
        ],
        "validation_note": "Generated outputs must be checked for successful execution and physical meaning. Short trajectories should be treated as workflow-validation tests unless production-scale sampling is used."
    }
    if not path.exists():
        path.write_text(json.dumps(data, indent=2))

for rec in gscf_records:
    write_gscf(rec)

geqs_errors = [
    ("GEQS_011", "missing_validation_note", 8, "Workflow has commands but lacks scientific validation note."),
    ("GEQS_012", "missing_expected_outputs", 8, "Workflow does not list expected output files."),
    ("GEQS_013", "wrong_rdf_group", 6, "RDF uses unclear or wrong atom group selection."),
    ("GEQS_014", "msd_without_nojump", 6, "MSD workflow lacks PBC nojump preprocessing."),
    ("GEQS_015", "density_without_energy_file", 7, "Density extraction does not mention md.edr or energy file requirement."),
    ("GEQS_016", "temperature_without_equilibration_check", 7, "Temperature workflow lacks equilibration/target-temperature validation."),
    ("GEQS_017", "npt_wrong_barostat", 6, "NPT workflow uses weak or outdated barostat without justification."),
    ("GEQS_018", "nvt_missing_thermostat", 6, "NVT workflow does not specify thermostat settings."),
    ("GEQS_019", "production_missing_equilibration", 5, "Production MD starts without EM/NVT/NPT preparation."),
    ("GEQS_020", "topology_not_updated_after_solvation", 5, "Topology molecule count not updated after solvation."),
    ("GEQS_021", "genion_missing_tpr", 5, "Ion addition lacks ions.tpr preparation by grompp."),
    ("GEQS_022", "trajectory_center_wrong_selection", 6, "Centering command uses unclear center/output group selection."),
    ("GEQS_023", "rmsd_without_fit", 7, "RMSD analysis lacks fitting/least-squares alignment discussion."),
    ("GEQS_024", "rmsf_wrong_group", 7, "RMSF group selection is unclear."),
    ("GEQS_025", "sasa_missing_probe_note", 8, "SASA workflow lacks probe/selection validation."),
    ("GEQS_026", "hbond_unclear_donor_acceptor", 7, "Hydrogen-bond workflow does not define donor/acceptor groups."),
    ("GEQS_027", "coordination_no_cn_output", 6, "Coordination-number workflow calculates RDF but omits -cn output."),
    ("GEQS_028", "density_profile_wrong_axis", 6, "Density profile workflow uses wrong or unspecified spatial direction."),
    ("GEQS_029", "energy_terms_unverified", 7, "Energy workflow does not verify available energy terms."),
    ("GEQS_030", "box_volume_missing_term", 7, "Volume workflow does not specify Volume energy term."),
    ("GEQS_031", "cluster_missing_cutoff", 7, "Cluster workflow lacks cutoff/method explanation."),
    ("GEQS_032", "pca_missing_covar", 6, "PCA workflow omits covariance generation."),
    ("GEQS_033", "distance_no_index", 7, "Distance workflow lacks custom index/selection note."),
    ("GEQS_034", "angle_no_index", 7, "Angle workflow lacks index group definition."),
    ("GEQS_035", "dihedral_wrong_type", 6, "Dihedral analysis does not specify dihedral type."),
    ("GEQS_036", "interactive_selection_not_reproducible", 6, "Workflow relies on undocumented manual selections."),
    ("GEQS_037", "missing_common_errors", 8, "Workflow lacks common errors and fixes."),
    ("GEQS_038", "missing_short_trajectory_warning", 7, "Workflow lacks short-trajectory limitation warning."),
    ("GEQS_039", "invalid_file_order", 5, "Workflow uses files before they are generated."),
    ("GEQS_040", "wrong_tpr_for_analysis", 6, "Analysis uses a mismatched .tpr file."),
    ("GEQS_041", "wrong_xtc_for_diffusion", 6, "MSD uses centered trajectory instead of nojump trajectory."),
    ("GEQS_042", "wrong_xtc_for_visualization", 7, "Visualization workflow uses nojump trajectory when centered trajectory is more appropriate."),
    ("GEQS_043", "missing_grompp_step", 5, "Simulation workflow omits grompp before mdrun."),
    ("GEQS_044", "missing_mdp_files", 5, "Simulation workflow omits required MDP settings/files."),
    ("GEQS_045", "missing_topology_include", 6, "Topology preparation lacks force-field/water-model include discussion."),
    ("GEQS_046", "wrong_water_atom_name", 7, "Workflow assumes OW/HW atom names without checking force-field naming."),
    ("GEQS_047", "unsafe_overclaim", 6, "Workflow claims production-quality result from short test trajectory."),
    ("GEQS_048", "no_reproducibility_note", 7, "Workflow lacks reproducibility details such as versions, files, and command order."),
    ("GEQS_049", "no_physical_interpretation", 8, "Workflow produces output but lacks physical interpretation guidance."),
    ("GEQS_050", "mixed_system_wrong_selection", 6, "Workflow uses whole System when a component-specific selection is needed."),
]

def write_geqs(rec):
    rid, name, score, reason = rec
    path = GEQS / f"{rid.lower()}_{name}.json"
    data = {
        "id": rid,
        "task_name": name,
        "dataset": "GEQS",
        "status": "curated_evaluator_template",
        "expert_score": score,
        "error_pattern": name,
        "input": {
            "user_task": f"Evaluate a GROMACS workflow containing the error pattern: {name}.",
            "generated_workflow_issue": reason
        },
        "output": {
            "score": score,
            "decision": "accept" if score >= 8 else "revise",
            "detected_errors": [reason],
            "correction_suggestions": [
                "Add topology and file-preparation checks.",
                "Use correct GROMACS command order.",
                "Use reproducible atom/group selections.",
                "Add expected output files.",
                "Add scientific validation note."
            ]
        }
    }
    if not path.exists():
        path.write_text(json.dumps(data, indent=2))

for rec in geqs_errors:
    write_geqs(rec)

print("GSCF records:", len(list(GSCF.glob('*.json'))))
print("GEQS records:", len(list(GEQS.glob('*.json'))))
