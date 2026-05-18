from compdd.docking_utils._ligands_common import (
    _expand_path,
    _parse_ligands_csv,
    _prepared_path,
)
from compdd.executors.gnu_parallel import gnu_parallel


def _obabel_ligands_prep(docking_cfg, ligands_cfg):
    ligands = _parse_ligands_csv(ligands_cfg.smiles_csv)
    output_dir = _expand_path(ligands_cfg.results_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = ligands_cfg.prepared_suffix

    mol2_files = [
        _prepared_path(output_dir, lig_name, suffix, ".mol2")
        for _, lig_name in ligands
    ]

    @gnu_parallel(docking_cfg, "prepare_ligands_obabel()")
    def charge_ligs_obabel():
        obabel = docking_cfg.libs.obabel

        cmds = []
        for (smiles, _), mol2_file in zip(ligands, mol2_files):
            cmds.append([
                obabel,
                f"-:'{smiles}'",
                "-O", mol2_file,
                "--gen3d", "-p", "7.4", "--minimize", "--steps", "5000", "--ff", "GAFF",
            ])

        return cmds

    charge_ligs_obabel()

    if ligands_cfg.program == "dock6":
        return mol2_files

    pdbqt_files = [
        _prepared_path(output_dir, lig_name, suffix, ".pdbqt")
        for _, lig_name in ligands
    ]

    @gnu_parallel(docking_cfg, "prepare_ligands_mgltools()")
    def charge_ligs_mgltools():
        mgltools = docking_cfg.libs.mgltools

        cmds = []
        for mol2_file, pdbqt_file in zip(mol2_files, pdbqt_files):
            cmds.append([
                mgltools / "bin" / "pythonsh",
                mgltools / "MGLToolsPckgs" / "AutoDockTools" / "Utilities24" / "prepare_ligand4.py",
                "-l", mol2_file,
                "-o", pdbqt_file,
            ])

        return cmds

    charge_ligs_mgltools()
    return pdbqt_files
