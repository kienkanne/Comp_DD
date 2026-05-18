from dataclasses import dataclass

from compdd.configs.docking_config import RootConfig
from compdd.configs.ligands_config import LigandsConfig
from compdd.docking_utils._ligands_prep import _ligands_prep
from compdd.vina._vina_prep_rec import _vina_prep_rec
from compdd.vina._vina_docking import _vina_docking
from compdd.docking_utils._write_summary_csv import _write_summary_csv
from compdd.docking_utils._copy_to_results import _copy_to_results

@dataclass(frozen=True)
class VinaPipeline():
    cfg: RootConfig
    ligands_cfg: LigandsConfig

    def run(self):
        lig_files = _ligands_prep(self.cfg, self.ligands_cfg)
        prepped_rec, vina_config = _vina_prep_rec(self.cfg)
        out_files = _vina_docking(self.cfg, lig_files, prepped_rec, vina_config)
        docking_summary = _write_summary_csv(self.cfg, out_files, program="vina")

        _copy_to_results(self.cfg, prepped_rec, docking_summary, out_files)
