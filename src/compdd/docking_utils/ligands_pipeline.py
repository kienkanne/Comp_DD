from dataclasses import dataclass

from compdd.configs.docking_config import RootConfig
from compdd.configs.ligands_config import LigandsConfig
from compdd.docking_utils._ligands_prep import _ligands_prep


@dataclass(frozen=True)
class LigandsPipeline:
    docking_cfg: RootConfig
    cfg: LigandsConfig

    def run(self):
        return _ligands_prep(self.docking_cfg, self.cfg)
