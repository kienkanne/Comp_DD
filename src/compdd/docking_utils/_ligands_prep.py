from compdd.docking_utils._ligands_common import (
    _discover_prepared_ligands,
    _parse_ligands_csv,
    _sanitize_name,
)
from compdd.utils.main_tracker import main_tracker


def _ligands_prep(docking_cfg, ligands_cfg):
    @main_tracker(docking_cfg, "Prepare ligands")
    def _run():
        if ligands_cfg.source == "files":
            return _discover_prepared_ligands(ligands_cfg)

        if ligands_cfg.prepare_tool == "obabel":
            from compdd.docking_utils._obabel_ligands_prep import _obabel_ligands_prep

            return _obabel_ligands_prep(docking_cfg, ligands_cfg)

        if ligands_cfg.prepare_tool == "meeko":
            from compdd.docking_utils._meeko_ligands_prep import _meeko_ligands_prep

            return _meeko_ligands_prep(docking_cfg, ligands_cfg)

        raise ValueError(f"Unsupported ligand preparation tool: {ligands_cfg.prepare_tool}")

    return _run()
