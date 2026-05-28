import shutil
from pathlib import Path
from nexus.core.trackers.main_tracker import main_tracker, PipelineContext


@main_tracker("Final copy to results")
def final_copy(dcfg, rec_bundles, docking_summary, out_files):
    ctx = PipelineContext.get_ctx()
    logger = ctx.logger
    manifest = ctx.manifest
    manifest.finalize(success=True)
    logger.info("Pipeline completed")

    working_dir = dcfg.common.working_dir
    results_dir = dcfg.common.results_dir

    results_dir.mkdir(parents=True, exist_ok=True)

    mode = getattr(dcfg.common, "mode", "mix")

    if mode == "mix":
        rec_names = [r.name for r in rec_bundles]
        groups = {name: [] for name in rec_names}
        for out in out_files:
            stem = Path(out).stem
            for rec in rec_names:
                if stem.startswith(f"{rec}_"):
                    groups[rec].append(out)
                    break

        # Copy per-receptor
        for item, rec_name in zip(rec_bundles, rec_names):
            rec_dir = results_dir / rec_name
            (rec_dir / "poses").mkdir(parents=True, exist_ok=True)

            # copy outputs
            for out in groups.get(rec_name, []):
                src = working_dir / out
                dst = rec_dir / "poses" / Path(out).name
                if src.exists():
                    shutil.copy2(src, dst)

            # copy receptor file
            rec_path = item.receptor
            if rec_path.exists():
                shutil.copy2(rec_path, rec_dir / rec_path.name)

            # copy receptor-specific config if present on bundle
            pocket = None
            if hasattr(item, "pocket"):
                pocket = item.pocket
            if pocket and pocket.exists():
                shutil.copy2(pocket, rec_dir)

        # copy docking summary files to respective receptor dirs or to root
        csv_paths_dict = {} # Used to add to metadata
        if isinstance(docking_summary, (list, tuple)):
            for csv in docking_summary:
                for rec in rec_names:
                    if rec in str(csv.stem):
                        src = working_dir / csv
                        dst = results_dir / rec / Path(csv).name
                        if src.exists():
                            shutil.copy2(src, dst)
                        csv_paths_dict[rec] = dst
                        break

        for name, csv_path in csv_paths_dict.items():
            setattr(dcfg.metadata, name, str(csv_path))

    ### DISABLED
    else:  # match mode -> single csv and a 'details' folder with everything
        details = results_dir / "details"
        details.mkdir(parents=True, exist_ok=True)
        (details / "poses").mkdir(parents=True, exist_ok=True)

        # copy all outputs into details/poses
        for out in out_files:
            src = working_dir / out
            dst = details / "poses" / Path(out).name
            if src.exists():
                shutil.copy2(src, dst)

        # copy all receptors and configs into details
        for item in rec_bundles:
            rec_path = item.receptor
            if rec_path.exists():
                shutil.copy2(rec_path, details / rec_path.name)
            # possible config fields
            if hasattr(item, "pocket"):
                pocket = item.pocket
                if pocket.exists():
                    shutil.copy2(pocket, details)
            if hasattr(item, "selected_spheres"):
                sp = Path(item.selected_spheres)
                if sp.exists():
                    shutil.copy2(sp, details / sp.name)

        # copy single csv to root as summary
        if isinstance(docking_summary, (list, tuple)):
            # pick first
            csv = docking_summary[0] if docking_summary else None
        else:
            csv = docking_summary
        if csv:
            src = working_dir / csv
            dst = results_dir / Path(csv).name
            if src.exists():
                shutil.copy2(src, dst)
        ### DISABLED


    # Copy to root
    project_name = dcfg.common.project_name
    for f in [f"{project_name}_run.log", 
                f"{project_name}_manifest.json", 
                f"{project_name}_state.json"]:
        src = working_dir / f
        dst = results_dir / f
        if src.exists():
            shutil.copy2(src, dst)

    # Finally, dump json meta with csv file paths

    metadata_dict = dcfg.metadata.model_dump() 
    metadata_path = results_dir / f"{project_name}_metadata.json"

    import json
    if metadata_dict is not None:
        # Serialize the dictionary to a pretty-printed JSON file
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata_dict, f, indent=4)
    
