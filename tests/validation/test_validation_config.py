from pathlib import Path

from compdd.validation_coreset.validation_config import load_validation_config
from compdd.docking_configs.root_config import RootConfig


def test_load_validation_config_sets_match_mode_and_uses_data(tmp_path):
    # Create a minimal validation tree
    entry = tmp_path / "1abc"
    entry.mkdir()
    (entry / "1abc_protein.pdb").write_text("protein")
    (entry / "1abc_pocket.pdb").write_text("pocket")
    (entry / "1abc_ligand.sdf").write_text("ligand")

    config_path = tmp_path / "validation.yaml"
    config_path.write_text(
        "libs:\n"
        "  chimerax: chimerax\n"
        "  chimera: chimera\n"
        "  dock_home: dock6\n"
        "  obabel: obabel\n"
        "  parallel: parallel\n"
        "  vina: vina\n"
        "common:\n"
        "  project_name: validation\n"
        f"  working_dir: {tmp_path / 'work'}\n"
        f"  results_dir: {tmp_path / 'results'}\n"
        "receptors:\n"
        "  source: pdb\n"
        "ligands:\n"
        "  source: sdf\n"
        f"validation:\n"
        f"  data: {tmp_path}\n"
        "vina: {}\n"
        "dock6: {}\n"
    )

    cfg = load_validation_config(config_path)

    assert cfg.common.mode == "match"
    assert cfg.receptors.source == "pdb"
    assert cfg.receptors.pdbs == [entry / "1abc_protein.pdb"]
    assert cfg.receptors.reference == [entry / "1abc_pocket.pdb"]
    assert cfg.ligands.source == "sdf"
    assert cfg.ligands.sdfs == [entry / "1abc_ligand.sdf"]
    assert cfg.common.working_dir == Path(tmp_path / "work" / "validation")
