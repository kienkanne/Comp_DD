from pathlib import Path
import csv
import re
from compdd.executors.gnu_parallel import gnu_parallel
from compdd.utils.main_tracker import main_tracker


def _sanitize_name(name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip())
    sanitized = sanitized.strip("._-")
    if not sanitized:
        raise ValueError(f"Invalid ligand name {name!r}")
    return sanitized


def _parse_ligands_csv(csv_path):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Ligand CSV not found: {csv_path}")

    seen_smiles = set()
    seen_names = set()
    ligands = []

    with open(csv_path, newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["smiles", "name"]:
            raise ValueError("Ligand CSV must have exactly this header: smiles,name")

        for row_number, row in enumerate(reader, start=2):
            smiles = (row.get("smiles") or "").strip()
            raw_name = (row.get("name") or "").strip()
            if not smiles or not raw_name:
                raise ValueError(f"Ligand CSV row {row_number} must include smiles and name")

            name = _sanitize_name(raw_name)

            if smiles in seen_smiles:
                raise ValueError(f"Duplicate smiles: {smiles!r}")
            seen_smiles.add(smiles)

            if name in seen_names:
                raise ValueError(f"Duplicate ligand name after sanitization: {raw_name!r}")
            seen_names.add(name)

            ligands.append((smiles, name))

    if not ligands:
        raise ValueError(f"Ligand CSV contains no ligands: {csv_path}")

    return ligands


def _ligands_prep(cfg, program):
    @main_tracker(cfg, "Prepare ligands")
    def _run():
        ligands = _parse_ligands_csv(cfg.common.ligands_csv)
        lig_names = [name for _, name in ligands]

        @gnu_parallel(cfg, "charge_ligs_obabel()")
        def charge_ligs_obabel():
            obabel = cfg.libs.obabel

            cmds = []
            for smiles, lig_name in ligands:
                cmds.append([
                    obabel,
                    f"-:'{smiles}'",
                    "-O", f"{lig_name}_prepped.mol2",
                    "--gen3d", "-p", "7.4", "--minimize", "--steps 5000", "--ff GAFF"
                ])

            return cmds
        charge_ligs_obabel()

        prepped_ligs = []

        @gnu_parallel(cfg, "charge_rec_mgltools()")
        def charge_rec_mgltools():
            mgltools = cfg.libs.mgltools

            cmds = []
            for lig_name in lig_names:
                cmds.append([
                    mgltools/"bin"/"pythonsh",
                    mgltools/"MGLToolsPckgs"/"AutoDockTools"/"Utilities24"/"prepare_ligand4.py",
                    "-l", f"{lig_name}_prepped.mol2",
                    "-o", f"{lig_name}_prepped.pdbqt",
                    ])
                prepped_ligs.append(f"{lig_name}_prepped.pdbqt")

            return cmds

        if program == "vina":
            charge_rec_mgltools()
        else:
            prepped_ligs = [f"{lig_name}_prepped.mol2" for lig_name in lig_names]

        return prepped_ligs

    return _run()
