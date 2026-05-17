import pytest

from compdd.docking_utils._ligands_prep import _parse_ligands_csv


def test_parse_ligands_csv_preserves_smiles_name_pairs(tmp_path):
    csv_path = tmp_path / "ligands.csv"
    csv_path.write_text(
        "smiles,name\n"
        "Cc1ccc(C(C)C)cc1O,mol1\n"
        "C#CCOc1cc(C(C)C)ccc1C,mol2\n"
        "CC(=O)OC1=CC=CC=C1C(=O)O,aspirin\n"
    )

    assert _parse_ligands_csv(csv_path) == [
        ("Cc1ccc(C(C)C)cc1O", "mol1"),
        ("C#CCOc1cc(C(C)C)ccc1C", "mol2"),
        ("CC(=O)OC1=CC=CC=C1C(=O)O", "aspirin"),
    ]


def test_parse_ligands_csv_rejects_duplicate_sanitized_names(tmp_path):
    csv_path = tmp_path / "ligands.csv"
    csv_path.write_text("smiles,name\nCC,lig 1\nCCC,lig_1\n")

    with pytest.raises(ValueError, match="Duplicate ligand name"):
        _parse_ligands_csv(csv_path)
