from string import Template
from pathlib import Path

from nexus.core.trackers.main_tracker import main_tracker
from nexus.md.amber._run_pmemd import _run_pmemd
from nexus.md.md_config import MDConfig

''' Minimization n runs. 
The first run takes the input coordinates.
Each subsequent run takes the output coordinates of the previous run. 
The output coordinates are saved as min{run}.ncrst'''

def minimize(mcfg: MDConfig, prmtop: Path, inpcrd: Path) -> Path:
    @main_tracker(mcfg, "Minimization")
    def _run():
        working_dir = mcfg.common.working_dir
        working_dir.mkdir(parents=True, exist_ok=True)

        cut = mcfg.common.cut
        n_min_runs = mcfg.min.n_min_runs
        ncyc = mcfg.min.ncyc
        maxcyc = mcfg.min.maxcyc
        restraints = mcfg.min.restraints

        with open(Path(__file__).resolve().parents[0] / "templates" / "min_template.txt") as f:
            min_template = f.read()

        last_ncrst = None
        for run in range(1, n_min_runs + 1):
            min_input = Template(min_template).substitute(
                ncyc=ncyc,
                maxcyc=maxcyc,
                cut=cut,
                restraint=restraints[run - 1],
            )

            if run == 1:
                _run_pmemd(min_input, prmtop, inpcrd, working_dir, f"min{run}")
            else:
                ncrst = working_dir / f"min{run - 1}.ncrst"
                _run_pmemd(min_input, prmtop, ncrst, working_dir, f"min{run}")
            last_ncrst = working_dir / f"min{run}.ncrst"

        return last_ncrst
    return _run()