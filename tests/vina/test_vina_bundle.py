from pathlib import Path
from types import SimpleNamespace

from nexus.dock.vina._docking import _build_vina_docking_commands
from nexus.dock.vina._prep_rec import VinaReceptorBundle


def test_vina_docking_builds_mix_mode_commands(tmp_path):
    cfg = SimpleNamespace(common=SimpleNamespace(working_dir=tmp_path, mode="mix"))
    receptor = VinaReceptorBundle(
        receptor=tmp_path / "rec1_prepared.pdbqt",
        vina_config=tmp_path / "rec1_vina_config.txt",
        pocket=tmp_path / "rec1_pocket.pdb",
        name="rec1",
    )
    ligand = tmp_path / "ligA_prepared.pdbqt"

    out_files, cmds = _build_vina_docking_commands(cfg, [(receptor, ligand)])

    assert out_files == [tmp_path / "rec1_ligA_prepared_scored.pdbqt"]
    assert cmds == [
        [
            "vina",
            "--receptor",
            str(receptor.receptor),
            "--ligand",
            str(ligand),
            "--config",
            str(receptor.vina_config),
            "--out",
            tmp_path / "rec1_ligA_prepared_scored.pdbqt",
        ]
    ]


def test_vina_docking_builds_match_mode_output_prefix(tmp_path):
    cfg = SimpleNamespace(common=SimpleNamespace(working_dir=tmp_path, mode="match"))
    receptor = VinaReceptorBundle(
        receptor=tmp_path / "rec1_prepared.pdbqt",
        vina_config=tmp_path / "rec1_vina_config.txt",
        pocket=tmp_path / "rec1_pocket.pdb",
        name="rec1",
    )
    ligand = Path("rec1_prepared.pdbqt")

    out_files, _ = _build_vina_docking_commands(cfg, [(receptor, ligand)])

    assert out_files == [tmp_path / "rec1_prepared_scored.pdbqt"]
