from nexus.prep.prep_config import PrepConfig
from nexus.core.executors.shell import shell
from pathlib import Path

def _run_antechamber_parmchk2(pcfg: PrepConfig):
    ligand = pcfg.sysmd.ligand
    ligand_charged = pcfg.sysmd.working_dir / f"{ligand.stem}_charged.mol2"
    antechamber_cmd = ["antechamber", "-i", str(ligand), "-fi", "mol2", 
                       "-o", str(ligand_charged), "-fo", "mol2", 
                       "-c", "bcc", "-nc", "0", "-pf", "yes"]

    @shell()
    def _a_run():
        return (antechamber_cmd, None)
    _a_run()

    # clean up
    sqm_files = ["sqm.in", "sqm.out", "sqm.pdb"]
    for sqm in sqm_files:
        Path(sqm).unlink(missing_ok=True)

    ligand_frcmod = ligand_charged.with_suffix(".frcmod") 
    
    parmchk2_cmd = ["parmchk2", "-i", str(ligand_charged), "-f", "mol2","-o", str(ligand_frcmod)]

    @shell()
    def _p_run():
        return (parmchk2_cmd, None)
    _p_run()    

    return ligand_charged, ligand_frcmod
