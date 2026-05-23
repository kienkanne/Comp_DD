from dataclasses import dataclass
from nexus.fetch.fetch_config import FetchConfig
from nexus.fetch.rcsb_fetch import rcsb_fetch


@dataclass(frozen=True)
class FetchPipeline:
    fcfg: FetchConfig

    def run(self):
        for id in self.fcfg.id_list:
            raw_path = rcsb_fetch(self.fcfg, id)
