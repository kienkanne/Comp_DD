from nexus.dock.dock_config import load_dock_config


def test_load_docking_config_keeps_ligands_out_of_common(tmp_path):
    receptor = tmp_path / "rec.pdb"
    receptor.write_text("protein")

    config_yaml = tmp_path / "docking.yaml"
    config_yaml.write_text(
        "libs:\n"
        "  chimerax: chimerax\n"
        "  chimera: chimera\n"
        "  mgltools: mgltools\n"
        "  dock_home: dock6\n"
        "  obabel: obabel\n"
        "  parallel: parallel\n"
        "  vina: vina\n"
        "common:\n"
        "  project_name: demo\n"
        f"  working_dir: {tmp_path / 'work'}\n"
        f"  results_dir: {tmp_path / 'results'}\n"
        "  prepared_suffix: ready\n"
        "receptors:\n"
        "  source: pdb\n"
        f"  pdbs: [{receptor}]\n"
        "  pocket_option: selection\n"
        "  selection: all\n"
        "ligands:\n"
        "  source: existing\n"
        "  existing_dir: .\n"
        "  output_dir: .\n"
        "validation: {}\n"
        "vina: {}\n"
        "dock6: {}\n"
    )

    cfg = load_dock_config(config_yaml)

    assert cfg.common.prepared_suffix == "ready"
    assert cfg.common.working_dir == tmp_path / "work" / "demo"
    assert cfg.common.results_dir == tmp_path / "results" / "demo"
    assert not hasattr(cfg.common, "ligands_csv")


def test_load_docking_config_reference_option(tmp_path):
    receptor = tmp_path / "rec.pdb"
    receptor.write_text("protein")
    reference = tmp_path / "pocket.pdb"
    reference.write_text("pocket")

    config_yaml = tmp_path / "docking_reference.yaml"
    config_yaml.write_text(
        "libs:\n"
        "  chimerax: chimerax\n"
        "  chimera: chimera\n"
        "  mgltools: mgltools\n"
        "  dock_home: dock6\n"
        "  obabel: obabel\n"
        "  parallel: parallel\n"
        "  vina: vina\n"
        "common:\n"
        "  project_name: demo\n"
        f"  working_dir: {tmp_path / 'work'}\n"
        f"  results_dir: {tmp_path / 'results'}\n"
        "receptors:\n"
        "  source: pdb\n"
        f"  pdbs: [{receptor}]\n"
        "  pocket_option: reference\n"
        f"  reference: {reference}\n"
        "ligands:\n"
        "  source: existing\n"
        "  existing_dir: .\n"
        "  output_dir: .\n"
        "validation: {}\n"
        "vina: {}\n"
        "dock6: {}\n"
    )

    cfg = load_dock_config(config_yaml)

    assert cfg.receptors.pocket_option == "reference"
    assert cfg.receptors.reference == [reference]
