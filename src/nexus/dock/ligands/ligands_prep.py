from functools import partial

from nexus.core.executors.python_parallel import python_parallel
from nexus.core.executors.gnu_parallel import gnu_parallel
from nexus.core.trackers.main_tracker import main_tracker

from nexus.dock.ligands._ligands_common import _parse_ligands_csv, _discover_prepared_ligands


def ligands_prep(dcfg):
    @main_tracker(dcfg, "Prepare ligands")
    def _run():
        if dcfg.ligands.source == "existing":
            return _discover_prepared_ligands(dcfg)
        
        if dcfg.ligands.source == "sdf":
            @python_parallel(dcfg, "load_sdf_parallel()", skip=True)
            def _load_sdf_parallel(sdfs):
                from nexus.dock.ligands._load_sdf import _load_sdf
                tasks = []
                for sdf in sdfs:
                    tasks.append(partial(_load_sdf, sdf))
                return tasks

            parallel_output = _load_sdf_parallel(dcfg.ligands.sdfs)
            mol_with_h_list, names = map(list, zip(*parallel_output))
            
        if dcfg.ligands.source == "smiles":
            smiles_list, names = _parse_ligands_csv(dcfg.ligands.smiles_csv)

            @python_parallel(dcfg, "rdkit_gen3d_parallel()", skip=True)
            def _rdkit_gen3d_parallel(smiles_list):
                from nexus.dock.ligands._rdkit_gen3d import _rdkit_gen3d
                tasks = []
                for smiles in smiles_list:
                    tasks.append(partial(_rdkit_gen3d, smiles))
                return tasks
            mol_with_h_list = _rdkit_gen3d_parallel(smiles_list)


        if dcfg.common.program == "vina":
            @python_parallel(dcfg, "meeko_charge_parallel()", skip=True)
            def _meeko_charge_parallel(mol_with_h_list, names):
                from nexus.dock.ligands._meeko_charge import _meeko_charge
                tasks = []
                for mol_with_h, name in zip(mol_with_h_list, names):
                    tasks.append(partial(
                        _meeko_charge,
                        mol_with_h,
                        name,
                        dcfg.ligands.output_dir,
                        dcfg.common.prepared_suffix,
                    ))
                return tasks

            prepared_ligs = _meeko_charge_parallel(mol_with_h_list, names)
        
        
        if dcfg.common.program == "dock6":
            prepared_ligs = []

            @gnu_parallel(dcfg, "obabel_charge_parallel()")
            def _obabel_charge_parallel(mol_with_h_list, names):
                from rdkit import Chem
                obabel = dcfg.libs.obabel
                cmds = []
                
                for mol_with_h, name in zip(mol_with_h_list, names):
                        output_nocharge_sdf_path = dcfg.common.working_dir / f"{name}_nocharge.sdf"
                        writer = Chem.SDWriter(output_nocharge_sdf_path)
                        writer.write(mol_with_h)

                        output_mol2_path = dcfg.ligands.output_dir / f"{name}_{dcfg.common.prepared_suffix}.mol2"
                        cmds.append([
                            obabel,
                            output_nocharge_sdf_path,
                            "-O", output_mol2_path,
                            "--ff", "mmff94",
                        ])
                        prepared_ligs.append(output_mol2_path)
                return cmds
            
            _obabel_charge_parallel(mol_with_h_list, names)

        return prepared_ligs
    return _run()