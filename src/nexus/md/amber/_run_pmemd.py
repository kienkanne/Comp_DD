from pathlib import Path
from nexus.core.executors.shell import shell


def _run_pmemd(mdin_input: str, prmtop: Path, inpcrd: Path, working_dir: Path, stepname: str):
    mdin = working_dir / f"{stepname}.in"
    mdin.write_text(mdin_input)

    out = Path(working_dir) / f"{stepname}.out"
    ncrst = Path(working_dir) / f"{stepname}.ncrst"
    nc = Path(working_dir) / f"{stepname}.nc"
    mdinfo = Path(working_dir) / f"{stepname}.info"
    
    pmemd_cmd = [
    "pmemd.cuda",
    "-AllowSmallBox",
    "-O",
    "-i", str(mdin),
    "-o", str(out),
    "-p", str(prmtop),
    "-c", str(inpcrd),
    "-ref", str(inpcrd),
    "-r", str(ncrst),
    "-x", str(nc),
    "-inf", str(mdinfo)
    ]

    with shell(pmemd_cmd):
        pass

    return True
        