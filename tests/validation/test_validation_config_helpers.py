from pathlib import Path
import tempfile

from nexus.dock.dock_config import match_references_to_receptors, parse_selection_csv


def test_match_references_to_receptors(tmp_path):
    # receptors named like '6W63_protein.pdb' and references like '6W63_pocket.pdb'
    rec1 = tmp_path / "6W63_protein.pdb"
    rec2 = tmp_path / "1abc_protein.pdb"
    rec1.write_text("")
    rec2.write_text("")

    ref1 = tmp_path / "6W63_pocket.pdb"
    ref2 = tmp_path / "1abc_pocket.pdb"
    ref1.write_text("")
    ref2.write_text("")

    mapping = match_references_to_receptors([rec1, rec2], [ref1, ref2], "_pocket.pdb")
    assert mapping[rec1] == ref1
    assert mapping[rec2] == ref2


def test_parse_selection_csv(tmp_path):
    csvf = tmp_path / "sel.csv"
    csvf.write_text("6W63,chain A and resi 50\n1ABC,chain B and resi 40\n")
    mapping = parse_selection_csv(csvf)
    assert mapping["6W63"] == "chain A and resi 50"
    assert mapping["1ABC"] == "chain B and resi 40"
