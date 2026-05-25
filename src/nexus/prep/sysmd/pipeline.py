from pydantic import BaseModel
from nexus.prep.prep_config import PrepConfig
from nexus.prep.sysmd._pdb4amber import _run_pdb4amber
from nexus.prep.sysmd._antechamber_parmchk2 import _run_antechamber_parmchk2
from nexus.prep.sysmd._tleap import run_tleap


class SysmdPipeline(BaseModel):
    pcfg: PrepConfig

    def _run(self):
        receptor_named = _run_pdb4amber(self.pcfg)
        ligand_charged, ligand_frcmod = _run_antechamber_parmchk2(self.pcfg)
        run_tleap(self.pcfg, receptor_named, ligand_charged, ligand_frcmod)

### TODO:
# Cli for Sysmd
# Cpptraj analysis package
# Validate module -> Run for results
# Write lecture notes

# Literature first:
### Claude
# Select protein structures
# Find Mpro drugs

# Docking and write results
# Ranking pre-analysis
# MD suggestions strats