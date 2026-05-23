from pydantic import BaseModel
from typing import Optional
from pathlib import Path

class CommonConfig(BaseModel):
    input: Optional[Path] = None
    output: Optional[Path] = None
    suffix: Optional[str] = None

    chimerax: Optional[Path] = "/usr/local/chimerax/bin/ChimeraX"

class RecConfig(BaseModel):
    dry: Optional[bool] = False

class MutateConfig(BaseModel):
    mutations: Optional[str] = None

class LigConfig(BaseModel):
    pass


class PrepConfig(BaseModel):
    common: CommonConfig = CommonConfig()
    rec: RecConfig = RecConfig()
    mutate: MutateConfig = MutateConfig()
    lig: LigConfig = LigConfig()


def load_prep_config(path):
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f)
    pcfg = PrepConfig.model_validate(data)
    
    if pcfg.common.output is None:
        pcfg.common.output = pcfg.common.input.parent

    """if pcfg.common.task == "lig":
        if pcfg.common.input.suffix == "csv":
            from nexus.dock.ligands._ligands_common import _parse_ligands_csv
            pcfg.common.input = _parse_ligands_csv(pcfg.common.input)
        else:
            pcfg.common.input = extract_files(pcfg.common.input, ".sdf")
        
        if pcfg.common.format not in ("vina", "dock6", "amber"):
            raise ValueError("Output ligand format for program must be 'vina', 'dock6' or 'amber'.")"""


    return pcfg
