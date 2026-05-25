from nexus.prep.prep_config import PrepConfig
from nexus.core.executors.shell import shell


def _run_pdb4amber(pcfg: PrepConfig):
    receptor = pcfg.common.input
    receptor_renamed = pcfg.common.working_dir / (f"{receptor.stem}_renamed.pdb")
    cmd = ["pdb4amber", "-i", str(receptor), "-o", str(receptor_renamed)]

    @shell()
    def _run():
        return (cmd, None)
    _run()

    return receptor_renamed
