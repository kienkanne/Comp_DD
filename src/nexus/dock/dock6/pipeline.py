from dataclasses import dataclass

from nexus.dock.dock_config import DockConfig
from nexus.dock.ligands.ligands_prep import ligands_prep
from nexus.dock.dock6._prep_rec import dock6_prep_rec
from nexus.dock.dock6._docking import dock6_docking
from nexus.dock.utils.matchmixer import matchmixer
from nexus.dock.utils.write_summary_csv import write_summary_csv
from nexus.dock.utils.final_copy import final_copy

@dataclass(frozen=True)
class DOCK6Pipeline():
    dcfg: DockConfig

    def run(self):
        self.dcfg.common.program = "dock6"

        lig_files = ligands_prep(self.dcfg)
        prepped_recs = dock6_prep_rec(self.dcfg)
        pairs = matchmixer(prepped_recs, lig_files, 
                           self.dcfg.common.prepared_suffix, self.dcfg.common.mode)

        out_files = dock6_docking(self.dcfg, pairs)
        docking_summary = write_summary_csv(self.dcfg, out_files, prepped_recs)

        final_copy(self.dcfg, prepped_recs, docking_summary, out_files)
