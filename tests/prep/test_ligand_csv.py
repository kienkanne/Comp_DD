import pytest

from nexus.prep.ligdock._parse_csv import _parse_ligands_csv


def test_parse_ligands_csv_sanitizes_names(tmp_path):
    csv_path = tmp_path / "ligands.csv"
    csv_path.write_text("smiles,name\nCCO,ethyl alcohol\nCCN,amine#1\n")

    smiles, names = _parse_ligands_csv(csv_path)

    assert smiles == ["CCO", "CCN"]
    assert names == ["ethyl_alcohol", "amine_1"]


def test_parse_ligands_csv_requires_exact_header(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("name,smiles\nethanol,CCO\n")

    with pytest.raises(ValueError, match="exactly this header"):
        _parse_ligands_csv(csv_path)


def test_parse_ligands_csv_rejects_duplicate_sanitized_names(tmp_path):
    csv_path = tmp_path / "dupes.csv"
    csv_path.write_text("smiles,name\nCCO,a b\nCCN,a_b\n")

    with pytest.raises(ValueError, match="Duplicate ligand name"):
        _parse_ligands_csv(csv_path)
