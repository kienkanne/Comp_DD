import pytest

from nexus.dock.dock_config import match_references_to_receptors, parse_selection_csv


def test_match_references_to_receptors_by_base_name(tmp_path):
    rec1 = tmp_path / "6W63_protein.pdb"
    rec2 = tmp_path / "1abc_protein.pdb"
    ref1 = tmp_path / "6W63_pocket.pdb"
    ref2 = tmp_path / "1abc_pocket.pdb"
    for path in [rec1, rec2, ref1, ref2]:
        path.write_text("")

    mapping = match_references_to_receptors([rec1, rec2], [ref1, ref2], "_pocket.pdb")

    assert mapping == {rec1: ref1, rec2: ref2}


def test_match_references_to_receptors_raises_for_missing_reference(tmp_path):
    rec = tmp_path / "6W63_protein.pdb"
    ref = tmp_path / "other_pocket.pdb"
    rec.write_text("")
    ref.write_text("")

    with pytest.raises(FileNotFoundError, match="expected name 6W63_pocket.pdb"):
        match_references_to_receptors([rec], [ref], "_pocket.pdb")


def test_parse_selection_csv_uses_first_two_columns(tmp_path):
    csv_path = tmp_path / "selection.csv"
    csv_path.write_text("6W63,/A:41,ignored\n1ABC,/B:100\n\n")

    assert parse_selection_csv(csv_path) == {"6W63": "/A:41", "1ABC": "/B:100"}
