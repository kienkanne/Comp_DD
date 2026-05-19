from dataclasses import dataclass

from compdd.configs.docking_config import RootConfig
from compdd.docking_utils._ligands_prep import ligands_prep
from compdd.vina._vina_prep_rec import _vina_prep_rec
from compdd.vina._vina_docking import _vina_docking
from compdd.docking_utils._write_summary_csv import _write_summary_csv
from compdd.docking_utils._copy_to_results import _copy_to_results

@dataclass(frozen=True)
class VinaPipeline():
    cfg: RootConfig

    def run(self):
        lig_files = ligands_prep(self.cfg)
        prepped_rec, vina_config = _vina_prep_rec(self.cfg)
        out_files = _vina_docking(self.cfg, lig_files, prepped_rec, vina_config)
        docking_summary = _write_summary_csv(self.cfg, out_files)

        _copy_to_results(self.cfg, prepped_rec, docking_summary, out_files, [vina_config])

#test
from compdd.configs.docking_config import load_config

cfg = load_config("/localscratch/kbui/COMPDD/sample_configs/sample_docking.yaml")
cfg.common.program = "vina"
print (cfg.ligands.output_dir)
VinaPipeline(cfg).run()