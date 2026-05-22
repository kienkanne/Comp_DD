from dataclasses import dataclass
from pathlib import Path
import os
from nexus.core.executors.shell import shell
from nexus.core.executors.base import base
from nexus.core.trackers.main_tracker import main_tracker
from nexus.dock.dock_config import DockConfig


@dataclass(frozen=True)
class VinaReceptorBundle:
    receptor: Path
    vina_config: Path
    name: str


def _prep_rec(dcfg: DockConfig, receptor_bundle: VinaReceptorBundle):
    if hasattr(receptor_bundle, "receptor"):
        receptor = receptor_bundle.receptor
        bundle = receptor_bundle
    else:
        receptor = receptor_bundle
        bundle = None
    name = Path(receptor).stem
    suffix = dcfg.common.prepared_suffix
    prepped_receptor_pdbqt = f"{name}_{suffix}.pdbqt"
    pocket = f"{name}_pocket.pdb"

    @shell(dcfg)
    def generate_site():
        chimerax = dcfg.libs.chimerax

        if bundle is not None and bundle.reference_path is not None:
            input_file = bundle.reference_path
            delete_selection = "clear"

        elif bundle is not None and bundle.selection_string is not None:
            input_file = receptor
            delete_selection = f"~{bundle.selection_string}"

        stdin = [
            f"open {input_file}",
            f"select {delete_selection}",
            "delete sel",
            f"save {pocket}"
        ]

        stdin = "\n".join(stdin)

        return ([chimerax, "--nogui"], stdin)
    generate_site()

    wd = dcfg.common.working_dir
    if not os.path.exists(wd / pocket):
        raise FileNotFoundError(f"{wd / pocket} was not created. Check selection string or reference.")

    if os.path.getsize(wd / pocket) == 0:
        raise IOError(f"{wd / pocket} is empty. Check selection string or reference.")

    @shell(dcfg)
    def meeko_prep_rec():
        padding = dcfg.common.padding

        cmd = [
                "mk_prepare_receptor.py",
                "-i",
                receptor,
                "-o",
                f"{name}_{suffix}",
                "-a",
                "-p",  # Generate receptor PDBQT
                "-v",
                f"{name}_{suffix}_vina_config.txt",  # Generate Vina config file
                "--box_enveloping",
                f"{name}_pocket.pdb",  # Wrap around this molecule
                "--padding",
                str(padding),  # Padding buffer in Angstroms
            ]
        
        return (cmd, None)
    meeko_prep_rec()

    @base(dcfg, "add_configs()")
    def add_configs():
        exhaustiveness = dcfg.vina.exhaustiveness
        num_modes = dcfg.vina.num_modes
        extra_configs = {
                    "exhaustiveness": exhaustiveness,
                    "num_modes": num_modes,
                }
        with open(f"{name}_{suffix}_vina_config.txt", "a") as config_file:
            config_file.write("\n")
            for key, value in extra_configs.items():
                config_file.write(f"{key} = {value}\n")
    add_configs()       

    return VinaReceptorBundle(
        receptor=Path(prepped_receptor_pdbqt),
        vina_config=Path(f"{name}_{suffix}_vina_config.txt"),
        name=name,
    )


from nexus.core.executors.python_parallel import python_parallel
from nexus.core.trackers.main_tracker import main_tracker
from functools import partial


def vina_prep_rec(dcfg):
    @main_tracker(dcfg, "Prepare receptor for Vina")
    @python_parallel(dcfg, "prep_rec()", skip=True)
    def _run():
        tasks = []
        bundles = getattr(dcfg.receptors, "bundles", None)
        if bundles:
            for b in bundles:
                tasks.append(partial(_prep_rec, dcfg, b))
        else:
            raise ValueError()
        return tasks
    return _run()