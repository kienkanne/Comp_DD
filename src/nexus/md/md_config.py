from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from pathlib import Path


class CommonConfig(BaseModel):
    model_config = ConfigDict(extra='allow')

    project_name: Optional[str] = "md"
    working_dir: Optional[Path] = Path.cwd() / "artifacts"
    results_dir: Optional[Path] = Path.cwd() / "results"
    
    temp: Optional[float] = 300.0
    dt: Optional[float] = 0.002
    cut: Optional[float] = 10.0
    mask: Optional[str] = None

    prmtop: Optional[Path] = None
    inpcrd: Optional[Path] = None


class MinConfig(BaseModel):
    n_min_runs: Optional[int] = 7
    ncyc: Optional[int] = 1000
    maxcyc: Optional[int] = 5000
    restraints: Optional[List[float]] = [10.0, 5.0, 2.0, 1.0, 0.5, 0.1, 0.0]


class HeatConfig(BaseModel):
    mid_temp: Optional[float] = 100.0
    time1: Optional[float] = 100.0
    time2: Optional[float] = 500.0
    total_time: Optional[float] = 2000.0
    restraint: Optional[float] = 10.0


class EqConfig(BaseModel):
    n_eq_runs: Optional[int] = 7
    eq_time: Optional[float] = 100.0
    restraints: Optional[List[float]] = [10.0, 5.0, 2.0, 1.0, 0.5, 0.1, 0.0]


class ProdConfig(BaseModel):
    num_seeds: Optional[int] = 1
    rand_time: Optional[float] = 200.0
    prod_time: Optional[float] = 2500.0
    prod_freq: Optional[float] = 10.0


class MDConfig(BaseModel):
    common: Optional[CommonConfig] = CommonConfig()
    min: Optional[MinConfig] = MinConfig()
    heat: Optional[HeatConfig] = HeatConfig()
    eq: Optional[EqConfig] = EqConfig()
    prod: Optional[ProdConfig] = ProdConfig()


def load_md_config(path):
    import yaml
    with open(path) as f:
        mcfg = yaml.safe_load(f)
    mcfg = MDConfig.model_validate(mcfg)
    ### TODO: Simplify setup function and remove dependencies
    mcfg = _setup_dirs(mcfg)

    return mcfg
    

def _setup_dirs(mcfg: MDConfig):
    from nexus.core.trackers.logging_utils import setup_logger
    from nexus.core.trackers.manifest import Manifest
    from nexus.core.trackers.runstate import State

    mcfg.common.working_dir = mcfg.common.working_dir/ mcfg.common.project_name
    mcfg.common.results_dir = mcfg.common.results_dir / mcfg.common.project_name
    
    mcfg.common.working_dir.mkdir(parents=True, exist_ok=True)
    mcfg.common.results_dir.mkdir(parents=True, exist_ok=True)

    setattr(mcfg.common, "logger", setup_logger(mcfg.common.working_dir / "run.log"))
    setattr(mcfg.common, "manifest", Manifest(mcfg.common.working_dir / "manifest.json"))
    setattr(mcfg.common, "runstate", State(mcfg.common.working_dir / "state.json") )

    return mcfg
