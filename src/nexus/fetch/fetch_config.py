from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path


class FetchConfig(BaseModel):
    raw_assembly_suffix: Optional[str] = "raw_assembly"
    cleaned_suffix: Optional[str] = "cleaned"
    ligand_suffix: Optional[str] = None

    remove_waters: Optional[bool] = True
    kept_residues: Optional[List] = []

    output_dir: Optional[Path] = None
    remove_raw_assembly: Optional[bool] = False

    id_list: Optional[List] = None

def load_fetch_config(path):
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f)
    rcfg = FetchConfig.model_validate(data)

    return rcfg