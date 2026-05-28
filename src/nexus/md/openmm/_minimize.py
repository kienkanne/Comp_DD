from nexus.md.md_config import MDConfig
from openmm.app import Simulation
from openmm.unit import kelvin
from nexus.md.openmm._setup import set_positional_restraint_strength

from nexus.core.trackers.main_tracker import main_tracker, PipelineContext

@main_tracker("Minimization")
def minimize(mcfg: MDConfig, simulation: Simulation):
    logger = PipelineContext.get_ctx().logger

    n_min_runs = mcfg.min.n_min_runs
    maxcyc = mcfg.min.maxcyc
    restraints = mcfg.min.restraints

    state = simulation.context.getState(getEnergy=True)
    logger.info(f"Initial PE: {state.getPotentialEnergy()}")

    for run in range(n_min_runs):
        set_positional_restraint_strength(simulation, restraints[run])
        simulation.minimizeEnergy(maxIterations=maxcyc)

    state = simulation.context.getState(getEnergy=True)
    logger.info(f"Final PE: {state.getPotentialEnergy()}")

    return simulation