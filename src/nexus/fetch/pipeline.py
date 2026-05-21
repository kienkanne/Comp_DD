from dataclasses import dataclass
from nexus.fetch.fetch_config import FetchConfig
from nexus.fetch.rcsb import fetch_rcsb

@dataclass(frozen=True)
class FetchPipeline:
    fcfg: FetchConfig

    def run(self):
        fetch_rcsb(self.fcfg)