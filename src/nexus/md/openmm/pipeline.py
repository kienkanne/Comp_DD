from nexus.md.md_config import load_md_config
from nexus.md.openmm.workflows import heating
from nexus.md.openmm._setup import setup
mcfg = load_md_config("/localscratch/kbui/NexusMol/examples/amber_md.yaml")
simulation = setup(mcfg)
heating(mcfg, simulation)