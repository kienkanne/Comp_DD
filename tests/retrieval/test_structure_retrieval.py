from pathlib import Path
import sys
import types

import pytest

# Provide lightweight stand-ins for optional external dependencies used by the module.
fake_gemmi = types.ModuleType("gemmi")
fake_gemmi.cif = types.ModuleType("gemmi.cif")
fake_gemmi.cif.read_file = lambda path: None
fake_gemmi.make_structure_from_block = lambda block: None
sys.modules["gemmi"] = fake_gemmi
sys.modules["gemmi.cif"] = fake_gemmi.cif

fake_rcsbapi = types.ModuleType("rcsbapi")

fake_rcsbapi_data = types.ModuleType("rcsbapi.data")
fake_rcsbapi_data.DataQuery = object
sys.modules["rcsbapi.data"] = fake_rcsbapi_data

fake_rcsbapi_model = types.ModuleType("rcsbapi.model")
fake_rcsbapi_model.ModelQuery = object
sys.modules["rcsbapi.model"] = fake_rcsbapi_model

sys.modules["rcsbapi"] = fake_rcsbapi

from nexus.fetch.fetch_config import FetchConfig
import nexus.fetch.rcsb_fetch as rcsb_fetch


class FakeDoc:
    def sole_block(self):
        return None


class FakeResidue:
    def __init__(self, name):
        self.name = name


class FakeChain(list):
    pass


class FakeModel(list):
    pass


class FakeStructure(list):
    def remove_waters(self):
        self.removed_waters = True

    def make_mmcif_document(self):
        return self

    def write_file(self, path):
        Path(path).write_text("fake mmcif")


class FakeDataQuery:
    def __init__(self, input_type, input_ids, return_data_list):
        self.input_type = input_type
        self.input_ids = input_ids
        self.return_data_list = return_data_list
        self._response = None

    def exec(self):
        self._response = {
            "data": {
                "entries": [
                    {
                        "nonpolymer_entities": [
                            {"pdbx_entity_nonpoly": {"comp_id": "LIG"}},
                            {"pdbx_entity_nonpoly": {"comp_id": "HOH"}},
                        ]
                    }
                ]
            }
        }

    def get_response(self):
        return self._response


class FakeModelQuery:
    def __init__(self, download, file_directory):
        self.file_directory = Path(file_directory)

    def get_ligand(self, entry_id, label_comp_id, encoding, filename):
        Path(self.file_directory / filename).write_text("dummy sdf")

    def get_assembly(self, entry_id, encoding, filename):
        Path(self.file_directory / filename).write_text("data")


def test_get_ligands_in_structure_filters_ignored_entities(monkeypatch):
    monkeypatch.setattr(rcsb_fetch, "DataQuery", FakeDataQuery)

    ligand_ids = rcsb_fetch.get_ligands_in_structure("1ABC")

    assert ligand_ids == ["LIG"]


def test_retrieve_structure_writes_cleaned_cif_and_removes_raw(tmp_path, monkeypatch):
    cfg = FetchConfig(
        raw_assembly_suffix="raw_assembly",
        cleaned_suffix="cleaned",
        ligand_suffix=None,
        remove_waters=True,
        kept_residues=["ZN"],
        output_dir=tmp_path,
        remove_raw_assembly=True,
        id_list=["1ABC"],
    )

    monkeypatch.setattr(rcsb_fetch, "DataQuery", FakeDataQuery)
    monkeypatch.setattr(rcsb_fetch, "ModelQuery", FakeModelQuery)
    monkeypatch.setattr(rcsb_fetch.gemmi.cif, "read_file", lambda path: FakeDoc())
    monkeypatch.setattr(rcsb_fetch.gemmi, "make_structure_from_block", lambda block: FakeStructure([FakeModel([FakeChain([FakeResidue("HOH"), FakeResidue("ZN"), FakeResidue("ALA")])])]))

    rcsb_fetch.fetch_rcsb(cfg)

    expected_cleaned = tmp_path / "1ABC_cleaned.cif"
    assert expected_cleaned.exists()
    assert expected_cleaned.read_text() == "fake mmcif"
    assert not (tmp_path / "1ABC_raw_assembly.cif").exists()


def test_retrieve_structure_raises_if_id_list_missing(tmp_path):
    cfg = FetchConfig(
        output_dir=tmp_path,
        id_list=None,
    )

    with pytest.raises(TypeError):
        rcsb_fetch.fetch_rcsb(cfg)
