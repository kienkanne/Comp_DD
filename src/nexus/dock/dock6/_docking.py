from pathlib import Path
from string import Template

from nexus.core.executors.shell import shell
from nexus.core.executors.python_parallel import python_parallel
from functools import partial
from nexus.core.trackers.main_tracker import main_tracker


def _run_dock6(dcfg, receptor_bundle, prepped_lig):
    dock_home = dcfg.libs.dock_home
    max_orientations = dcfg.dock6.max_orientations
    working_dir = dcfg.common.working_dir

    selected_spheres = receptor_bundle.selected_spheres
    grid_prefix = receptor_bundle.grid_prefix
    receptor_name = receptor_bundle.name
    required_files = [f"{grid_prefix}.in", f"{grid_prefix}.bmp", f"{grid_prefix}.nrg", f"{grid_prefix}.out"]
    missing_files = [file_name for file_name in required_files if not Path(file_name).is_file()]

    if missing_files:
        raise FileNotFoundError(f"Missing required files in '{dcfg.common.working_dir}': {', '.join(missing_files)}")

    with open(Path(__file__).resolve().parents[0] / "templates" / "flex_template.txt") as f:
        flex_template = f.read()

    #ligand_name = _strip_prepared_suffix(prepped_lig, suffix)
    ligand_name = prepped_lig.stem

    output_prefix = f"{receptor_name}_{ligand_name}"

    output_path = working_dir / f"{output_prefix}_scored.mol2"

    input_file = Template(flex_template).substitute(
        prepped_lig=prepped_lig,
        dock_home=dock_home,
        selected_spheres=str(selected_spheres),
        grid_prefix=str(grid_prefix),
        output_path_prefix=str(working_dir / output_prefix),
        receptor_name=receptor_name,
        max_orientations=max_orientations,
    )

    flex = working_dir / f"flex_{output_prefix}.in"
    with open(flex, "w") as file:
        file.write(input_file)

    cmd = [dock_home / "bin" / "dock6", "-i", flex]

    with shell(cmd, title=f"dock6 docking for {output_prefix}"):
        pass

    return output_path


@main_tracker("Batch docking with DOCK6")
def dock6_parallel_docking(dcfg, pairs):
    tasks = []
    for receptor_bundle, prepped_lig in pairs:
        tasks.append(partial(_run_dock6, dcfg, receptor_bundle, prepped_lig))

    with python_parallel(tasks, dcfg.common.n_jobs, "dock6_parallel_docking()", skip=True) as out_paths:
        pass

    return out_paths
