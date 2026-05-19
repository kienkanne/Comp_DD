from functools import partial

from compdd.executors.python_parallel import python_parallel
from compdd.executors.gnu_parallel import gnu_parallel
from compdd.utils.main_tracker import main_tracker

from compdd.docking_utils._ligands_common import _parse_ligands_csv, _discover_prepared_ligands


def _meeko_charge(mol_with_h, name, output_dir, prepared_suffix):
    from meeko import MoleculePreparation, PDBQTWriterLegacy

    preparator = MoleculePreparation()
    mol_setups = preparator.prepare(mol_with_h)
    setup = mol_setups[0]

    pdbqt_string, is_valid, error_msg = PDBQTWriterLegacy.write_string(setup)
    if not is_valid:
        raise RuntimeError(f"Meeko failed to generate PDBQT: {error_msg}")

    output_pdbqt_path = output_dir / f"{name}_{prepared_suffix}.pdbqt"
    with open(output_pdbqt_path, "w") as handle:
        handle.write(pdbqt_string)
    return output_pdbqt_path


def ligands_prep(cfg):
    @main_tracker(cfg, "Prepare ligands")
    def _run():
        if cfg.ligands.source == "existing":
            return _discover_prepared_ligands(cfg)
        
        if cfg.ligands.source == "sdf":
            from compdd.docking_utils._load_sdf import _load_sdf
            mol_with_h_list, names = _load_sdf(cfg.ligands.sdf_dir)
            
        if cfg.ligands.source == "smiles":
            smiles_list, names = _parse_ligands_csv(cfg.ligands.smiles_csv)

            @python_parallel(cfg, "rdkit_gen3d_parallel()")
            def _rdkit_gen3d_parallel(smiles_list):
                from compdd.docking_utils._rdkit_gen3d import _rdkit_gen3d
                tasks = []
                for smiles in smiles_list:
                    tasks.append(partial(_rdkit_gen3d, smiles))
                return tasks
            mol_with_h_list = _rdkit_gen3d_parallel(smiles_list)


        @python_parallel(cfg, "meeko_charge_parallel()")
        def _meeko_charge_parallel(mol_with_h_list, names):
            tasks = []
            for mol_with_h, name in zip(mol_with_h_list, names):
                tasks.append(partial(
                    _meeko_charge,
                    mol_with_h,
                    name,
                    cfg.ligands.output_dir,
                    cfg.common.prepared_suffix,
                ))
            return tasks

        if cfg.common.program == "vina":
            prepared_ligs = _meeko_charge_parallel(mol_with_h_list, names)
        
        @gnu_parallel(cfg, "obabel_charge_parallel()")
        def _obabel_charge_parallel(mol_with_h_list, names):
            from rdkit import Chem
            obabel = cfg.libs.obabel
            cmds = []
            for mol_with_h, name in zip(mol_with_h_list, names):
                    output_nocharge_sdf_path = cfg.common.working_dir / f"{name}_nocharge.sdf"
                    writer = Chem.SDWriter(output_nocharge_sdf_path)
                    writer.write(mol_with_h)

                    output_mol2_path = cfg.ligands.output_dir / f"{name}_{cfg.prepared_suffix}.mol2"
                    cmds.append([
                        obabel,
                        output_nocharge_sdf_path,
                        "-O", output_mol2_path,
                        "--ff", "mmff94",
                    ])

            return cmds

        if cfg.common.program == "dock6":
            prepared_ligs = _obabel_charge_parallel(mol_with_h_list, names)

        return prepared_ligs
    return _run()