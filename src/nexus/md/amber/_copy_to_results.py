import shutil
from pathlib import Path
from nexus.core.trackers.main_tracker import main_tracker
from nexus.md.md_config import MDConfig


def copy_to_results(mcfg: MDConfig, outputs):
    @main_tracker(mcfg, "Copying to results")
    def _run():
        logger = mcfg.common.logger
        manifest = mcfg.common.manifest
        manifest.finalize(success=True)
        logger.info("Pipeline completed")

        prmtop = mcfg.common.prmtop

        working_dir = mcfg.common.working_dir
        results_dir = mcfg.common.results_dir

        shutil.copy2(prmtop, results_dir)

        for (prod_ncrst, prod_out) in outputs:
            shutil.copy2(prod_ncrst, results_dir)
            shutil.copy2(prod_out, results_dir)
            # Delete trajectory in artifacts
            Path(prod_ncrst).unlink(missing_ok=True)

        root_files = ["run.log", "manifest.json", "state.json"]
        for f in root_files:
            src = working_dir / f
            dst = results_dir / f
            if src.exists():
                shutil.copy2(src, dst)

        return True
    return _run()

        