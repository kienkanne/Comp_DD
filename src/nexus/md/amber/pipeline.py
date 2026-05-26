import os
from pydantic import BaseModel
from nexus.md.md_config import MDConfig

from nexus.md.amber._minimize import minimize
from nexus.md.amber._heat import heat
from nexus.md.amber._equilibrate import equilibrate
from nexus.md.amber._produce import produce
from nexus.md.amber._final_copy import copy_to_results


class AmberPipeline(BaseModel):
    mcfg: MDConfig

    def _run(self):
        AMBERHOME = os.environ.get("AMBERHOME")
        if not AMBERHOME:
            raise RuntimeError("AMBERHOME environment variable not set")

        prmtop = self.mcfg.common.prmtop
        inpcrd = self.mcfg.common.inpcrd

        if prmtop is None or not prmtop.is_file():
            raise FileNotFoundError(f"Missing prmtop at: {prmtop}")
        if inpcrd is None or not inpcrd.is_file():
            raise FileNotFoundError(f"Missing prmtop at: {inpcrd}")
        
        last_min_ncrst = minimize(self.mcfg, prmtop, inpcrd)
        last_heat_ncrst = heat(self.mcfg, prmtop, last_min_ncrst)
        last_eq_ncrst = equilibrate(self.mcfg, prmtop, last_heat_ncrst)
        
        ### TODO:
        # Returns trajectory file and out file for each seed to be copied to results_dir
        # Add production chunks, then combine at the end
        # Trajectory file should be removed from artifacts as it's very heavy
        outputs = produce(self.mcfg, prmtop, last_eq_ncrst)

        copy_to_results(self.mcfg, outputs)