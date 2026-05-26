import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class StubDataQuery:
    response = {"data": {"entries": []}}

    def __init__(self, input_type, input_ids, return_data_list):
        self.input_type = input_type
        self.input_ids = input_ids
        self.return_data_list = return_data_list

    def exec(self):
        return None

    def get_response(self):
        return self.response


class StubModelQuery:
    def __init__(self, download, file_directory):
        self.download = download
        self.file_directory = Path(file_directory)

    def get_ligand(self, entry_id, label_comp_id, encoding, filename):
        (self.file_directory / filename).write_text("stub sdf")

    def get_assembly(self, entry_id, encoding, filename):
        (self.file_directory / filename).write_text("stub cif")


rcsbapi = types.ModuleType("rcsbapi")
rcsbapi_data = types.ModuleType("rcsbapi.data")
rcsbapi_data.DataQuery = StubDataQuery
rcsbapi_model = types.ModuleType("rcsbapi.model")
rcsbapi_model.ModelQuery = StubModelQuery

sys.modules.setdefault("rcsbapi", rcsbapi)
sys.modules.setdefault("rcsbapi.data", rcsbapi_data)
sys.modules.setdefault("rcsbapi.model", rcsbapi_model)
