from pathlib import Path
import subprocess
import re

# Converts either pdbqt or mol2 docked poses to individual mol2 files, making it easy for RDKIT to read
def extract_poses(docked_poses_path: Path):
    docked_poses_path = Path(docked_poses_path)
    working_dir = docked_poses_path.parent
    ligand_name = docked_poses_path.stem    
    
    output_prefix = working_dir / f"{ligand_name}_pose_.mol2"

    cmd = ["obabel", str(docked_poses_path), "-O", str(output_prefix), "-m"]

    result = subprocess.run(cmd, text=True, capture_output=True, check=True)

    match = re.search(r'\d+', result.stderr)
    if match:
        num_poses = int(match.group())

    
    poses_path = []
    for i in range(num_poses):
        file_path = output_prefix.with_name(f"{ligand_name}_pose_{i+1}.mol2")
        poses_path.append(file_path)
    return poses_path


def _parse_mol2(file_path: Path):
    text = file_path.read_text()
    parts = text.split("@<TRIPOS>MOLECULE")
    if len(parts) < 2:
        return []

    mols = []
    for part in parts[1:]:
        block = "@<TRIPOS>MOLECULE" + part
        try:
            from rdkit import Chem
            mol = Chem.MolFromMol2Block(block, sanitize=False, removeHs=False)
            if mol:
                try:
                    Chem.SanitizeMol(mol)
                except Exception:
                    mol.SetProp("Sanitization_Failed", "True")
                mols.append(mol)
        except Exception:
            continue

    return mols


def parse_mol2_pose_rmsds(pose1_path: Path, pose2_path: Path):
    try:
        from rdkit.Chem import rdMolAlign
    except Exception as e:
        raise RuntimeError("RDKit is required for DOCK6 RMSD calculation") from e

    if not pose1_path.exists():
        raise FileNotFoundError(f"Prepared crystal not found: {pose1_path}")
    if not pose2_path.exists():
        raise FileNotFoundError(f"Scored file not found: {pose2_path}")

    pose1_mols = _parse_mol2(pose1_path)
    pose1_mol = pose1_mols[0]

    pose2_mols = _parse_mol2(pose2_path)
    pose2_mol = pose2_mols[0]

    try:
        rmsd = rdMolAlign.AlignMol(pose1_mol, pose2_mol, maxIters=0)
        return f"{rmsd:.3f}"
    except Exception:
        raise

"""pose1 = Path("/localscratch/kbui/NexusMol/examples/artifacts/6W63_mol4_solvated/6W63_mol4_prepared_scored_pose_1.mol2")
pose2 = Path("/localscratch/kbui/NexusMol/examples/artifacts/6W63_mol4_solvated/6W63_mol4_prepared_scored_pose_2.mol2")

print(parse_mol2_pose_rmsds(pose1, pose2))

pose1 = Path("/localscratch/kbui/NexusMol/build/extract_pdbqt/6W63_aspirin_pose1.mol2")
pose2 = Path("/localscratch/kbui/NexusMol/build/extract_pdbqt/6W63_aspirin_pose2.mol2")"""


poses = (extract_poses("/localscratch/kbui/NexusMol/build/extract_pdbqt/6W63_aspirin_prepared_scored.pdbqt"))

print(parse_mol2_pose_rmsds(poses[0], poses[7]))