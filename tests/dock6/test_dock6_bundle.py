from pathlib import Path
from types import SimpleNamespace

from nexus.dock.dock6._docking import _build_dock6_docking_commands
from nexus.dock.dock6._prep_rec import Dock6ReceptorBundle


def create_grid_files(prefix):
    for suffix in [".in", ".bmp", ".nrg", ".out"]:
        Path(f"{prefix}{suffix}").write_text("")


def test_dock6_docking_builds_commands_and_flex_input(tmp_path):
    grid_prefix = tmp_path / "rec1_grid"
    create_grid_files(grid_prefix)
    cfg = SimpleNamespace(
        libs=SimpleNamespace(dock_home=Path("/opt/dock6")),
        dock6=SimpleNamespace(max_orientations=100),
        common=SimpleNamespace(working_dir=tmp_path, mode="mix"),
    )
    receptor = Dock6ReceptorBundle(
        receptor=tmp_path / "rec1_prepared.mol2",
        selected_spheres=tmp_path / "rec1_ss.sph",
        grid_prefix=grid_prefix,
        pocket=tmp_path / "rec1_pocket.mol2",
        name="rec1",
    )
    ligand = tmp_path / "ligA_prepared.mol2"

    out_files, cmds = _build_dock6_docking_commands(cfg, [(receptor, ligand)])

    flex = tmp_path / "flex_rec1_ligA_prepared.in"
    assert out_files == [tmp_path / "rec1_ligA_prepared_scored.mol2"]
    assert cmds == [[Path("/opt/dock6/bin/dock6"), "-i", flex]]
    assert "ligA_prepared.mol2" in flex.read_text()
    assert str(tmp_path / "rec1_ligA_prepared") in flex.read_text()
    assert "max_orientations                                             100" in flex.read_text()


def test_dock6_docking_raises_when_grid_files_are_missing(tmp_path):
    cfg = SimpleNamespace(
        libs=SimpleNamespace(dock_home=Path("/opt/dock6")),
        dock6=SimpleNamespace(max_orientations=100),
        common=SimpleNamespace(working_dir=tmp_path, mode="mix"),
    )
    receptor = Dock6ReceptorBundle(
        receptor=tmp_path / "rec1_prepared.mol2",
        selected_spheres=tmp_path / "rec1_ss.sph",
        grid_prefix=tmp_path / "missing_grid",
        pocket=tmp_path / "rec1_pocket.mol2",
        name="rec1",
    )

    try:
        _build_dock6_docking_commands(cfg, [(receptor, tmp_path / "lig.mol2")])
    except FileNotFoundError as exc:
        assert "missing_grid.in" in str(exc)
    else:
        raise AssertionError("Expected missing grid files to raise FileNotFoundError")
