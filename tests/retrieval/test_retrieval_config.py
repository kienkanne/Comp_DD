import sys
from pathlib import Path

import pytest

if sys.version_info < (3, 10):
    pytest.skip(
        "nexus.fetch.fetch_config uses Python 3.10+ union type syntax",
        allow_module_level=True,
    )

from nexus.fetch.fetch_config import FetchConfig, load_fetch_config


def test_load_fetch_config_current_fields(tmp_path):
    config_path = tmp_path / "fetch.yaml"
    config_path.write_text(
        "input: [6W63, 7K40]\n"
        f"output_dir: {tmp_path / 'out'}\n"
        "ligand_name: ligand\n"
    )

    cfg = load_fetch_config(config_path)

    assert isinstance(cfg, FetchConfig)
    assert cfg.input == ["6W63", "7K40"]
    assert cfg.output_dir == Path(tmp_path / "out")
    assert cfg.ligand_name == "ligand"


def test_fetch_config_accepts_text_file_input_path(tmp_path):
    ids = tmp_path / "ids.txt"
    ids.write_text("6W63\n7K40\n")

    cfg = FetchConfig(input=ids, output_dir=tmp_path)

    assert cfg.input == ids
    assert cfg.output_dir == tmp_path
