import os
from string import Template
from pathlib import Path
import shutil

from nexus.md.analysis._run_cpptraj import _run_cpptraj

def full_analyze(prmtop: Path, trajin: Path, mask: str, name: str, output_dir: Path):
    AMBERHOME = os.environ.get("AMBERHOME")
    if not AMBERHOME:
        raise RuntimeError("AMBERHOME environment variable not set")

    with open(Path(__file__).resolve().parents[0] / "analysis_template.txt") as f:
        analysis_template = f.read()

    cpptraj_input = Template(analysis_template).substitute(prmtop=prmtop, trajin=trajin, mask=mask, name=name)

    _run_cpptraj(cpptraj_input, output_dir=output_dir, name=name)

    shutil.copy2((Path(__file__).resolve().parents[0] / "visual_temnplate.ipynb"), output_dir / f"Visual_{name}.ipynb")
