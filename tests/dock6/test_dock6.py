from nexus.dock.ligands._ligands_common import _prepared_path


def test_prepared_filename_adds_separator_before_suffix():
    p = _prepared_path("/tmp", "mol16", "ready", ".mol2")
    assert p.name == "mol16_ready.mol2"
