from string import Template
from pathlib import Path

from nexus.core.trackers.main_tracker import main_tracker
from nexus.md.amber._run_pmemd import _run_pmemd
from nexus.md.md_config import MDConfig


@main_tracker("Heating")
def heat(mcfg: MDConfig, prmtop: Path, last_min_ncrst: Path):
    '''Heating takes the output coordinates of the last minimization step.
    There is only 1 heating step, so the output coordinates are saved as heat.ncrst'''
    
    working_dir = mcfg.common.working_dir

    dt = mcfg.common.dt
    cut = mcfg.common.cut
    mask = mcfg.common.mask
    temp = mcfg.common.temp

    mid_temp = mcfg.heat.mid_temp
    time_mid_temp = mcfg.heat.time_mid_temp
    time_temp = mcfg.heat.time_temp
    total_time = mcfg.heat.total_time
    restraint = mcfg.heat.restraint

    nstlim = int((total_time) / dt)
    ntpr = ntwx = ntwr = int(nstlim // 100) or 10000

    with open(Path(__file__).resolve().parents[0] / "templates" / "heat_template.txt") as f:
        heat_template = f.read()

    heat_input = Template(heat_template).substitute(
        dt=dt,
        mid_temp=mid_temp,
        temp=temp,
        cut=cut,
        restraint=restraint,
        nstlim=nstlim,
        ntpr=ntpr,
        ntwx=ntwx,
        ntwr=ntwr,
        istep_mid_temp=int((time_mid_temp) / dt),
        istep_mid_temp_plus1=int((time_mid_temp) / dt) + 1,
        istep_temp=int((time_temp) / dt),
        mask=mask,
    )

    _run_pmemd(heat_input, prmtop, last_min_ncrst, working_dir, "heat")

    last_heat_ncrst = working_dir / "heat.ncrst"
    return last_heat_ncrst