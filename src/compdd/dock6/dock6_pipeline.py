from dataclasses import dataclass

from compdd.configs.docking_config import RootConfig
from compdd.configs.ligands_config import LigandsConfig
from compdd.docking_utils._ligands_prep import _ligands_prep
from compdd.dock6._dock6_prep_rec import _dock6_prep_rec
from compdd.dock6._dock6_docking import _dock6_docking
from compdd.docking_utils._write_summary_csv import _write_summary_csv
from compdd.docking_utils._copy_to_results import _copy_to_results

@dataclass(frozen=True)
class DOCK6Pipeline():
    cfg: RootConfig
    ligands_cfg: LigandsConfig

    def run(self):
        lig_files = _ligands_prep(self.cfg, self.ligands_cfg)
        prepped_rec, selected_spheres = _dock6_prep_rec(self.cfg)
        out_files = _dock6_docking(self.cfg, lig_files, selected_spheres)
        docking_summary = _write_summary_csv(self.cfg, out_files, program="dock6")

        _copy_to_results(self.cfg, prepped_rec, docking_summary, out_files)
