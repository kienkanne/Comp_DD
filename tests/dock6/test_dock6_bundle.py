from pathlib import Path
from types import SimpleNamespace

from nexus.dock.dock6._docking import _build_dock6_docking_commands
from nexus.dock.dock6._prep_rec import Dock6ReceptorBundle


def test_dock6_docking_builds_commands_with_receptor_bundle(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    required = [
        "rec1_grid.in",
        "rec1_grid.bmp",
        "rec1_grid.nrg",
        "rec1_grid.out",
    ]
    for name in required:
        (tmp_path / name).write_text("")

    cfg = SimpleNamespace(
        libs=SimpleNamespace(dock_home=Path("/usr/local/dock6")),
        dock6=SimpleNamespace(max_orientations=100),
        common=SimpleNamespace(prepared_suffix="prepped", working_dir=tmp_path),
    )
    receptor = Dock6ReceptorBundle(
        receptor=Path("rec1_prepped.mol2"),
        selected_spheres=Path("rec1_selected_spheres.sph"),
        grid_prefix=tmp_path / "rec1_grid",
        pocket=Path("rec1_pocket.mol2"),
        name="rec1",
    )
    ligand = Path("ligA_prepped.mol2")

    out_files, cmds = _build_dock6_docking_commands(cfg, [(receptor, ligand)])

    assert out_files == [tmp_path / "rec1_ligA_prepped_scored.mol2"]
    assert str(cfg.libs.dock_home / "bin" / "dock6") == str(cmds[0][0])
    assert tmp_path / "flex_rec1_ligA_prepped.in" in cmds[0]
    assert tmp_path / "rec1_ligA_prepped.dock6.out" in cmds[0]

    flex_text = (tmp_path / "flex_rec1_ligA_prepped.in").read_text()
    assert f"ligand_outfile_prefix                                        {tmp_path / 'rec1_ligA_prepped'}" in flex_text
