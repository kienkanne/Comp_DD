from pathlib import Path
from nexus.core.executors.shell import shell
import os

def _run_cpptraj(cpptraj_input: str, output_dir: Path, name: str= "", logger=None):
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        os.chdir(output_dir)
        @shell(logger=logger)
        def _run():

            cpptraj_in = output_dir / f"{name}.in"
            cpptraj_in.write_text(cpptraj_input)
            
            cpptraj_cmd = [
            "cpptraj",
            "-i",
            str(cpptraj_in),
            ]

            return (cpptraj_cmd, None)
        return _run()
        
    except Exception as e:
        raise RuntimeError(f"Failed to change working directory to {output_dir}: {e}")
    
    finally:
        os.chdir(Path.cwd())