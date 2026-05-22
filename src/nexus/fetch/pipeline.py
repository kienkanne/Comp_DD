from dataclasses import dataclass
from pathlib import Path
from nexus.fetch.chimerax_fix import chimerax_fix
from nexus.fetch.fetch_config import FetchConfig
from nexus.fetch.rcsb_fetch import rcsb_fetch
from nexus.fetch.chimerax_fix import chimerax_fix

@dataclass(frozen=True)
class FetchPipeline:
    fcfg: FetchConfig

    def run(self):
        for id in self.fcfg.id_list:
            raw_path = rcsb_fetch(self.fcfg, id)
            chimerax_fix(self.fcfg, raw_path, id)

        if self.fcfg.remove_raw_assembly:
            print (f"❗ Removing {raw_path}")
            Path(raw_path).unlink(missing_ok=True)