from nexus.prep.prep_config import PrepConfig
from nexus.core.executors.shell import shell
from pathlib import Path

def _process_ligand(pcfg: PrepConfig, ligand_pose: Path):
    """
    Antechamber, and parmchk2
    """
    ### TODO: -nc is hardcoded
    ligand_charged = pcfg.common.working_dir / f"{ligand_pose.stem}_charged.mol2"
    antechamber_cmd = ["antechamber", "-i", str(ligand_pose), "-fi", "mol2", 
                       "-o", str(ligand_charged), "-fo", "mol2", 
                       "-c", "bcc", "-nc", "0", "-pf", "yes"]   

    with shell(antechamber_cmd):
        pass

    # clean up
    sqm_files = ["sqm.in", "sqm.out", "sqm.pdb"]
    for sqm in sqm_files:
        Path(sqm).unlink(missing_ok=True)

    ligand_frcmod = ligand_charged.with_suffix(".frcmod") 
    
    parmchk2_cmd = ["parmchk2", "-i", str(ligand_charged), "-f", "mol2","-o", str(ligand_frcmod)]

    with shell(parmchk2_cmd):
        pass

    return ligand_charged, ligand_frcmod
