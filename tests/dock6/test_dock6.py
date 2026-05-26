from nexus.dock.utils._strip_prepared_suffix import _strip_prepared_suffix


def test_strip_prepared_suffix_for_dock6_names():
    assert _strip_prepared_suffix("mol16_prepared.mol2", "prepared") == "mol16"
    assert _strip_prepared_suffix("already_plain.mol2", "prepared") == "already_plain"
