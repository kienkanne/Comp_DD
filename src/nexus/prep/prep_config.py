from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional, Literal, List
from pathlib import Path

class CommonConfig(BaseModel):
    input: Optional[Path] = None
    output_dir: Optional[Path] = None
    suffix: Optional[str] = None

    chimerax: Optional[Path] = "/usr/local/chimerax/bin/ChimeraX"

    model_config = ConfigDict(extra='allow')

    @model_validator(mode="after")
    def default_output_dir(self):
        if self.output_dir is None:
            self.output_dir = Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self

class RecConfig(BaseModel):
    dry: Optional[bool] = False

class MutateConfig(BaseModel):
    mutations: Optional[List[str]] = None

class LigdockConfig(BaseModel):
    source: Optional[Literal["smiles", "csv"]] = "smiles"
    n_jobs: Optional[int] = 1
    type: Optional[Literal["GAFF", "AM1-BCC"]] = "GAFF"

class SysmdConfig(BaseModel):
    name: Optional[str] = None
    working_dir: Optional[Path] = Path.cwd()
    ligand: Optional[Path] = None
    # Technically these are literal, but there are a lot of options
    force_field: Optional[str] = "ff19SB"
    water_model: Optional[str] = "opc"

    box_type: Optional[Literal["Box", "Oct"]] = "Oct"
    box_size: Optional[float] = 12.0
    salt_conc: Optional[float] = 0.15    

    @model_validator(mode="after")
    def default_working_dir(self):
        if self.working_dir is None:
            self.working_dir = Path.cwd()
        self.working_dir.mkdir(parents=True, exist_ok=True)
        return self

class PrepConfig(BaseModel):
    common: Optional[CommonConfig] = CommonConfig()
    rec: Optional[RecConfig] = RecConfig()
    mutate: Optional[MutateConfig] = MutateConfig()
    ligdock: Optional[LigdockConfig] = LigdockConfig()
    sysmd: Optional[SysmdConfig] = SysmdConfig()


def load_prep_config(path):
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f)
    pcfg = PrepConfig.model_validate(data)
    
    if pcfg.common.output is None:
        pcfg.common.output = pcfg.common.input.parent

    return pcfg
