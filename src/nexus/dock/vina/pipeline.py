from dataclasses import dataclass

from nexus.dock.dock_config import DockConfig
from nexus.prep.lig.ligands_prep import ligands_prep
from nexus.dock.vina._prep_rec import vina_prep_rec
from nexus.dock.utils.matchmixer import matchmixer
from nexus.dock.vina._docking import vina_docking
from nexus.dock.utils.write_summary_csv import write_summary_csv
from nexus.dock.utils.final_copy import final_copy

@dataclass(frozen=True)
class VinaPipeline():
    dcfg: DockConfig

    def run(self):
        self.dcfg.common.program = "vina"

        prepped_ligs = ligands_prep(self.dcfg)
        prepped_recs = vina_prep_rec(self.dcfg)

        pairs = matchmixer(prepped_recs, prepped_ligs, 
                           self.dcfg.common.prepared_suffix, self.dcfg.common.mode)

        out_files = vina_docking(self.dcfg, pairs)
        docking_summary = write_summary_csv(self.dcfg, out_files, prepped_recs)

        config_files = [bundle.vina_config for bundle in prepped_recs]
        final_copy(self.dcfg, prepped_recs, docking_summary, out_files, config_files)
