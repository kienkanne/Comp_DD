from pydantic import BaseModel, model_validator
from typing import Literal, Optional
from pathlib import Path


class LigandsConfig(BaseModel):
    source: Literal["smiles", "files"] = "smiles"
    prepared_suffix: str = "prepped"

    smiles_csv: Optional[Path] = None
    results_dir: Optional[Path] = None
    prepare_tool: Literal["obabel", "meeko"] = "obabel"

    ligands_dir: Optional[Path] = None
    program: Literal["vina", "dock6"]

    @model_validator(mode="after")
    def validate_source_fields(self):
        if self.source == "smiles":
            if self.smiles_csv is None:
                raise ValueError("smiles_csv is required when source is 'smiles'")
            if self.results_dir is None:
                raise ValueError("results_dir is required when source is 'smiles'")
        elif self.ligands_dir is None:
            raise ValueError("ligands_dir is required when source is 'files'")
        return self


def load_ligands_config(path, program):
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f)
    data["program"] = program
    cfg = LigandsConfig.model_validate(data)

    return cfg
