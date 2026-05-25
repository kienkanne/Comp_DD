from pathlib import Path
from shutil import which
from nexus.prep.prep_config import PrepConfig
from nexus.core.executors.shell import shell


def _select_pose(pcfg: PrepConfig):
    ligand = pcfg.sysmd.ligand
    pose_num = pcfg.sysmd.pose_num
    working_dir = pcfg.common.working_dir

    ligand_name = working_dir / ligand.stem

    m_cmd = ["obabel", str(ligand), "-O", f"{ligand_name}_pose_.mol2", "-m"]
    
    @shell()
    def _m_run():
        return (m_cmd, None)
    _m_run()
    
    ligand_pose = f"{ligand_name}_pose_{pose_num}.mol2"
    with_h = f"{ligand_name}_pose_{pose_num}_with_H.mol2"

    h_cmd = ["obabel", ligand_pose, "-O", with_h, "-h"]

    @shell()
    def _h_run():
        return (h_cmd, None)
    _h_run()

    return Path(with_h)
