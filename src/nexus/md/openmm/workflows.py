from nexus.md.md_config import MDConfig
from openmm.app import Simulation
from openmm.unit import kelvin
from nexus.md.openmm._setup import set_positional_restraint_strength

def minimize(mcfg: MDConfig, simulation: Simulation):
    n_min_runs = mcfg.min.n_min_runs
    maxcyc = mcfg.min.maxcyc
    restraints = mcfg.min.restraints

    for run in len(n_min_runs):
        set_positional_restraint_strength(simulation, restraints[run])
        simulation.minimizeEnergy(maxIterations=maxcyc)

    return simulation


def heating(mcfg: MDConfig, simulation: Simulation):
    def continuous_heat(simulation: Simulation, curr_temp: float, total_steps: int, top_temperature: float):
        import numpy as np
        """Divide a step count across windows while preserving the exact total."""
        number_of_windows = 100
        temp_range = top_temperature - curr_temp
        # np.repeat creates a flat array of 1s, and array_split divides it evenly/smoothly
        # Then we sum each split section to get the step counts per window
        dummy_array = np.ones(total_steps, dtype=int)
        step_windows = np.array([len(w) for w in np.array_split(dummy_array, number_of_windows)])

        # Each temperature window stores the temperature to increase, proportional to the step size
        temperature_windows = np.array([s/total_steps*temp_range for s in step_windows])
        
        for step, temp_increase in zip(step_windows, temperature_windows):
            curr_temp += temp_increase
            simulation.context.setVelocitiesToTemperature(mid_temp * kelvin)
            simulation.step(step)

        return simulation, curr_temp

    temp = mcfg.common.temp # This temp here is the final desired temperature
    mid_temp = mcfg.heat.mid_temp # Adjustable middle temp for heating strategy

    dt = mcfg.common.dt
    time_mid_temp = mcfg.heat.time_mid_temp # Timestamp when mid_temp is reached
    time_temp = mcfg.heat.time_temp # Timestap when temp is reached
    total_time = mcfg.heat.total_time

    restraint = mcfg.heat.restraint
    set_positional_restraint_strength(simulation, restraint)

    curr_temp = 0
    # From 0 to time_mid_temp picoseconds
    simulation, curr_temp = continuous_heat(simulation, curr_temp, int(time_mid_temp / dt), mid_temp)

    # From time_mid_temp to time_temp
    simulation, curr_temp = continuous_heat(simulation, curr_temp, int((time_temp - time_mid_temp) / dt), temp) 

    # Finally, current temp should be at temp, and we step the rest from time_temp to total_time
    simulation.step(int((total_time - time_temp) / dt))
    

def equilbrate(mcfg: MDConfig, simulation: Simulation):
    dt = mcfg.common.dt

    n_eq_runs = mcfg.eq.n_eq_runs
    eq_time = mcfg.eq.eq_time
    restraints = mcfg.eq.restraints

    for run in len(n_eq_runs):
        set_positional_restraint_strength(simulation, restraints[run])
        simulation.step(int(eq_time / dt))

    return simulation


def produce(mcfg: MDConfig, simulation: Simulation):
    dt = mcfg.common.dt
    temp = mcfg.common.temp

    num_seeds = mcfg.prod.num_seeds
    rand_time = mcfg.prod.rand_time
    prod_time = mcfg.prod.prod_time
    prod_freq = mcfg.prod.prod_freq # TODO: Build Reporter

    set_positional_restraint_strength(simulation, 0)

    simulations = []
    for i in range(1, num_seeds + 1):
        # Reset the simulation to the base, and randomize velocities
        simulation_i = simulation
        simulation.context.setVelocitiesToTemperature(temp)

        simulation_i.step(int(rand_time / dt))
        simulation_i.step(int(prod_time / dt))

        simulations.append(simulation)
