from types import SimpleNamespace

from nexus.validate.rmsd import compute_validation_rmsds


def test_compute_validation_rmsds_writes_csv_for_vina_outputs(tmp_path, monkeypatch):
    cfg = SimpleNamespace(
        common=SimpleNamespace(
            max_poses=2,
            working_dir=tmp_path,
            results_dir=tmp_path,
            project_name="validation",
            prepared_suffix="prepared",
            program="vina",
        ),
        receptors=SimpleNamespace(bundles=[SimpleNamespace(name="1abc")]),
    )
    (tmp_path / "1abc_prepared.pdbqt").write_text("prepared")
    (tmp_path / "1abc_ligand_scored.pdbqt").write_text("scored")

    monkeypatch.setattr(
        "nexus.validate.rmsd.parse_vina_pose_rmsds",
        lambda prep_path, scored_path, max_poses: ["0.100", "0.200"],
    )

    assert compute_validation_rmsds(cfg) is True
    assert (tmp_path / "validation_1abc_rmsd.csv").read_text().splitlines() == [
        "name,rmsd1,rmsd2",
        "1abc_ligand,0.100,0.200",
    ]


def test_compute_validation_rmsds_writes_csv_for_dock6_outputs(tmp_path, monkeypatch):
    cfg = SimpleNamespace(
        common=SimpleNamespace(
            max_poses=1,
            working_dir=tmp_path,
            results_dir=tmp_path,
            project_name="validation",
            prepared_suffix="prepared",
            program="dock6",
        ),
        receptors=SimpleNamespace(bundles=[SimpleNamespace(name="1abc")]),
    )
    (tmp_path / "1abc_prepared.mol2").write_text("prepared")
    (tmp_path / "1abc_ligand_scored.mol2").write_text("scored")

    monkeypatch.setattr(
        "nexus.validate.rmsd.parse_dock6_pose_rmsds",
        lambda prep_path, scored_path, max_poses: ["1.234"],
    )

    assert compute_validation_rmsds(cfg) is True
    assert (tmp_path / "validation_1abc_rmsd.csv").read_text().splitlines() == [
        "name,rmsd1",
        "1abc_ligand,1.234",
    ]
