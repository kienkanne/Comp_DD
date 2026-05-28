from nexus.md.md_config import MDConfig
from openmm.app import Simulation
from openmm.unit import kelvin
from nexus.md.openmm._setup import set_positional_restraint_strength
from nexus.md.openmm._reporter import add_reporters
from nexus.core.trackers.main_tracker import main_tracker


@main_tracker("Equilibration")
def equilibrate(mcfg: MDConfig, simulation: Simulation):
    working_dir = mcfg.common.working_dir
    dt = mcfg.common.dt
    
    n_eq_runs = mcfg.eq.n_eq_runs
    eq_time = mcfg.eq.eq_time
    restraints = mcfg.eq.restraints

    # Reset repoters and clock
    simulation.reporters.clear()
    simulation.context.setStepCount(0)
    simulation.context.setTime(0.0)
    
    simulation, e_outputs = add_reporters(simulation, "eq", working_dir, 10000, int(eq_time * n_eq_runs / dt))

    for run in range(n_eq_runs):
        set_positional_restraint_strength(simulation, restraints[run])
        simulation.step(int(eq_time / dt))

    return simulation