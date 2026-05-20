from pathlib import Path

from compdd.retrieval.retrieval_config import load_retrieval_config, RetrievalConfig


def test_load_retrieval_config_defaults(tmp_path):
    config_path = tmp_path / "retrieve.yaml"
    config_path.write_text(
        "raw_assembly_suffix: raw_assembly\n"
        "cleaned_suffix: cleaned\n"
        "ligand_suffix: ligand\n"
        "remove_waters: false\n"
        "kept_residues: [Zn]\n"
        f"output_dir: {tmp_path / 'out'}\n"
        "remove_raw_assembly: true\n"
        "id_list: [P123, Q456]\n"
    )

    cfg = load_retrieval_config(config_path)

    assert isinstance(cfg, RetrievalConfig)
    assert cfg.raw_assembly_suffix == "raw_assembly"
    assert cfg.cleaned_suffix == "cleaned"
    assert cfg.ligand_suffix == "ligand"
    assert cfg.remove_waters is False
    assert cfg.kept_residues == ["Zn"]
    assert cfg.output_dir == Path(tmp_path / "out")
    assert cfg.remove_raw_assembly is True
    assert cfg.id_list == ["P123", "Q456"]
