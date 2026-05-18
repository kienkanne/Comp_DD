from compdd.docking_utils._ligands_common import _strip_prepared_suffix
from compdd.executors.gnu_parallel import gnu_parallel
from compdd.utils.main_tracker import main_tracker


def _vina_docking(cfg, lig_files, prepped_rec, vina_config):

    out_files = []

    @main_tracker(cfg, "Batch docking with Vina")
    @gnu_parallel(cfg, "vina_docking()")
    def _run():
        vina = cfg.libs.vina
        suffix = cfg.common.prepared_suffix

        cmds = []
        for prepped_lig in lig_files:
            ligand_name = _strip_prepared_suffix(prepped_lig, suffix)
            output_name = f"{ligand_name}_scored.pdbqt" # "_scored" stays fixed.

            out_files.append(output_name)

            cmds.append([vina, 
                              "--receptor", prepped_rec, 
                              "--ligand", prepped_lig, 
                              "--config", vina_config,
                              "--out", output_name])

        return cmds
    _run()

    return out_files
