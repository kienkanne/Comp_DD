import shutil
from pathlib import Path
from nexus.core.trackers.main_tracker import main_tracker, PipelineContext
from nexus.md.md_config import MDConfig

@main_tracker("Copying to results")
def final_copy(mcfg: MDConfig, outputs):

    ctx = PipelineContext.get_ctx()
    logger = ctx.logger
    manifest = ctx.manifest
    manifest.finalize(success=True)
    logger.info("Pipeline completed")

    prmtop = mcfg.common.prmtop

    working_dir = mcfg.common.working_dir
    results_dir = mcfg.common.results_dir

    shutil.copy2(prmtop, results_dir)

    for (prod_nc, prod_ncrst, prod_out) in outputs:
        shutil.copy2(prod_nc, results_dir)
        shutil.copy2(prod_ncrst, results_dir)
        shutil.copy2(prod_out, results_dir)
        # Safely delete trajectory in artifacts
        if Path(results_dir / Path(prod_nc).name).is_file():
            Path(prod_nc).unlink(missing_ok=True)

    project_name = mcfg.common.project_name
    for f in [f"{project_name}_run.log", 
                f"{project_name}_manifest.json", 
                f"{project_name}_state.json"]:
        src = working_dir / f
        dst = results_dir / f
        if src.exists():
            shutil.copy2(src, dst)

        return True


        