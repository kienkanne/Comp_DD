from compdd.docking_utils._ligands_common import (
    _expand_path,
    _parse_ligands_csv,
    _prepared_path,
)
from compdd.executors.base import base
from compdd.executors.gnu_parallel import gnu_parallel


def _prepare_ligand_with_meeko(smiles, output_pdbqt_path):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from meeko import MoleculePreparation, PDBQTWriterLegacy

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles}")

    mol_with_h = Chem.AddHs(mol)

    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    embed_status = AllChem.EmbedMolecule(mol_with_h, params)
    if embed_status == -1:
        raise RuntimeError(f"3D embedding failed for SMILES: {smiles}")

    props = AllChem.MMFFGetMoleculeProperties(mol_with_h)
    if props is not None:
        force_field = AllChem.MMFFGetMoleculeForceField(mol_with_h, props)
    else:
        force_field = AllChem.UFFGetMoleculeForceField(mol_with_h)

    if force_field is None:
        raise RuntimeError(f"Force field setup failed for SMILES: {smiles}")

    force_field.Initialize()
    force_field.Minimize(maxIts=500)

    preparator = MoleculePreparation()
    mol_setups = preparator.prepare(mol_with_h)
    setup = mol_setups[0]

    pdbqt_string, is_valid, error_msg = PDBQTWriterLegacy.write_string(setup)
    if not is_valid:
        raise RuntimeError(f"Meeko failed to generate PDBQT: {error_msg}")

    with open(output_pdbqt_path, "w") as handle:
        handle.write(pdbqt_string)


def _meeko_ligands_prep(docking_cfg, ligands_cfg):
    ligands = _parse_ligands_csv(ligands_cfg.smiles_csv)
    output_dir = _expand_path(ligands_cfg.results_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = ligands_cfg.prepared_suffix

    pdbqt_files = [
        _prepared_path(output_dir, lig_name, suffix, ".pdbqt")
        for _, lig_name in ligands
    ]

    @base(docking_cfg, "prepare_ligands_meeko()")
    def prepare_ligs_meeko():
        for (smiles, _), pdbqt_file in zip(ligands, pdbqt_files):
            _prepare_ligand_with_meeko(smiles, pdbqt_file)

    prepare_ligs_meeko()

    if ligands_cfg.program == "vina":
        return pdbqt_files

    mol2_files = [
        _prepared_path(output_dir, lig_name, suffix, ".mol2")
        for _, lig_name in ligands
    ]

    @gnu_parallel(docking_cfg, "convert_ligands_pdbqt_to_mol2()")
    def convert_ligs_obabel():
        obabel = docking_cfg.libs.obabel

        cmds = []
        for pdbqt_file, mol2_file in zip(pdbqt_files, mol2_files):
            cmds.append([obabel, pdbqt_file, "-O", mol2_file])

        return cmds

    convert_ligs_obabel()
    return mol2_files
