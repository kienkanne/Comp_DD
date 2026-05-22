from pydantic import BaseModel
from typing import Optional, List, Literal, Dict
from pathlib import Path


class FetchConfig(BaseModel):
    chimerax: Optional[Path] = None

    format: Literal["cif", "pdb"] = "cif"

    raw_assembly_suffix: Optional[str] = "raw_assembly"
    stripped_suffix: Optional[str] = "stripped"
    fixed_suffix: Optional[str] = "fixed"
    ligand_suffix: Optional[str] = None

    # Disabled for now
    remove_waters: Optional[bool] = True
    kept_residues: Optional[List] = []
    #

    output_dir: Optional[Path] = None
    remove_raw_assembly: Optional[bool] = False

    id_list: Optional[List] = None
    
    # Experimental
    mutations_csv: Optional[Path] = None

def load_fetch_config(path):
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f)
    rcfg = FetchConfig.model_validate(data)
    ### Experimental
    #rcfg.mutations_csv = parse_mutation_csv(rcfg.mutations_csv)

    return rcfg


import csv
def parse_mutation_csv(csv_path: Path) -> dict:
    mapping = {}
    with open(csv_path, newline='') as fh:
        reader = csv.reader(fh)
        for row in reader:
            if not row:
                continue
            if len(row) < 2:
                raise ValueError(f"Invalid selection CSV row: {row}")
            sel = row[0].strip()
            new_name = row[1].strip()
            mapping[sel] = new_name
    return mapping