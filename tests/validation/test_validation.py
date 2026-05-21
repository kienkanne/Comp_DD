from pathlib import Path
from types import SimpleNamespace

from nexus.validate.rmsd import compute_validation_rmsds
from nexus.validate.validate_config import load_validate_config


def test_load_validate_config_sets_match_mode_and_uses_data(tmp_path):
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

    cfg = load_validate_config(config_path)

    assert cfg.common.mode == "match"
    assert cfg.receptors.source == "pdb"
    assert cfg.receptors.reference_suffix == "_pocket.pdb"
    assert cfg.receptors.reference == [entry / "1abc_pocket.pdb"]
    assert cfg.ligands.source == "sdf"
    assert cfg.ligands.sdfs == [entry / "1abc_ligand.sdf"]
    assert cfg.common.working_dir == Path(tmp_path / "work" / "validation")


def test_compute_validation_rmsds_writes_csv(tmp_path, monkeypatch):
    cfg = SimpleNamespace(
        common=SimpleNamespace(
            max_poses=2,
            working_dir=tmp_path,
            results_dir=tmp_path,
            project_name="validation",
            prepared_suffix="prepped",
            program="vina",
        ),
        receptors=SimpleNamespace(
            bundles=[SimpleNamespace(name="1abc")],
        ),
    )

    (tmp_path / "1abc_prepped.pdbqt").write_text("dummy")
    (tmp_path / "1abc_ligand_scored.pdbqt").write_text("dummy")

    monkeypatch.setattr(
        "nexus.validate.rmsd._parse_pose_rmsds",
        lambda prep_path, scored_path, max_poses: ["0.123", ""],
    )

    assert compute_validation_rmsds(cfg) is True
    out_csv = tmp_path / "validation_1abc_rmsd.csv"
    assert out_csv.exists()
    assert out_csv.read_text().startswith("name,rmsd1,rmsd2")
