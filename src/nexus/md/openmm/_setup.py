from openmm import LangevinMiddleIntegrator, MonteCarloBarostat
from openmm.app import AmberInpcrdFile, AmberPrmtopFile, HBonds, PME, Simulation
from openmm.unit import atmosphere, kelvin, nanometer, picosecond

from pathlib import Path
import re

from nexus.md.md_config import MDConfig

def setup(mcfg: MDConfig):
    prmtop = AmberPrmtopFile(mcfg.common.prmtop)
    inpcrd = AmberInpcrdFile(mcfg.common.inpcrd)

    dt = mcfg.common.dt # already in picoseconds
    temp = mcfg.common.temp
    cut = mcfg.common.cut / 10 # Convert angstroms to nanometers
    mask = mcfg.common.mask

    system = prmtop.createSystem(
        nonbondedMethod=PME,
        nonbondedCutoff=cut*nanometer,
        constraints=HBonds,
        rigidWater=True
                                 )
    
    mask_pattern = r":(\d+)-(\d+)"

    match = re.search(mask_pattern, mask)
    if match:
        first_residue_i=int(match.group(1))
        stop_residue_i=int(match.group(2))
    else:
        raise ValueError(f"Invalid mask: {mask}")

    add_positional_restraints(topology=prmtop.topology,
                              positions=inpcrd.positions,
                              system=system,
                              first_residue_i=first_residue_i,
                              stop_residue_i=stop_residue_i,
                              k_kcal_per_mol_a2=10)
    
    # Set high friction (5 ps^-1) initially for safe heating stage
    # Set back to (1 ps^-1) for equilibration and production later on
    integrator = LangevinMiddleIntegrator(temp*kelvin, 5.0/picosecond, dt*picosecond)
    print (prmtop.topology.getPeriodicBoxVectors())
    simulation = Simulation(topology=prmtop.topology,
                            system=system,
                            integrator=integrator)
    
    simulation.context.setPositions(inpcrd.getPositions())


    num_forces = system.getNumForces()
    print(f"There are {num_forces} force terms in this system.")

    # Loop through to find a specific force object by its class name
    for i in range(num_forces):
        force = system.getForce(i)
        print(f"Index {i}: {type(force).__name__}")




"""Positional restraint helpers for staged OpenMM preparation protocols."""

from openmm import CustomExternalForce
from openmm.unit import kilojoule_per_mole, nanometer


RESTRAINT_PARAMETER_NAME = "positional_restraint_k"


def kcal_per_mol_a2_to_openmm(k_kcal_per_mol_a2):
    """Convert kcal/(mol A^2) force constants to OpenMM kJ/(mol nm^2)."""

    # 1 kcal/mol = 4.184 kJ/mol and 1 A^2 = 0.01 nm^2, so multiply by 418.4.
    return k_kcal_per_mol_a2 * 418.4 * kilojoule_per_mole / nanometer**2


def add_positional_restraints(
    topology,
    positions,
    system,
    first_residue_i,
    stop_residue_i,
    k_kcal_per_mol_a2,
):
    """Add harmonic restraints on atoms whose residue index is in the interval."""

    k = kcal_per_mol_a2_to_openmm(k_kcal_per_mol_a2)
    restraint = CustomExternalForce(
        "0.5*positional_restraint_k*((x-x0)^2 + (y-y0)^2 + (z-z0)^2)"
    )
    # Store each atom's reference coordinates as per-particle parameters.
    restraint.addPerParticleParameter("x0")
    restraint.addPerParticleParameter("y0")
    restraint.addPerParticleParameter("z0")
    # The global force constant lets protocols update restraint strength cheaply.
    restraint.addGlobalParameter(RESTRAINT_PARAMETER_NAME, k)

    for atom, position in zip(topology.atoms(), positions):
        amber_index = int(atom.residue.id)
        if first_residue_i <= amber_index <= stop_residue_i:
            x0, y0, z0 = position.value_in_unit(nanometer)
            restraint.addParticle(atom.index, [x0, y0, z0])

    system.addForce(restraint)
    return restraint


def set_positional_restraint_strength(simulation, k_kcal_per_mol_a2):
    """Update the existing restraint force constant in the active Context."""

    k = kcal_per_mol_a2_to_openmm(k_kcal_per_mol_a2)
    simulation.context.setParameter(RESTRAINT_PARAMETER_NAME, k)


from nexus.md.md_config import load_md_config

setup(load_md_config("/localscratch/kbui/NexusMol/examples/amber_md.yaml"))