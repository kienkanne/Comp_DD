import pytest

from nexus.validate.validate_config import load_validate_config


def test_load_validate_config_current_path_is_disabled_and_stale(tmp_path):
    entry = tmp_path / "1abc"
    entry.mkdir()
    (entry / "1abc_protein.pdb").write_text("protein")
    (entry / "1abc_pocket.pdb").write_text("pocket")
    (entry / "1abc_ligand.sdf").write_text("ligand")
    config_path = tmp_path / "validation.yaml"
    config_path.write_text(
        "common:\n"
        "  project_name: validation\n"
        f"  working_dir: {tmp_path / 'work'}\n"
        f"  results_dir: {tmp_path / 'results'}\n"
        "validation:\n"
        f"  data: {tmp_path}\n"
    )

    with pytest.raises((AttributeError, ValueError)):
        load_validate_config(config_path)
