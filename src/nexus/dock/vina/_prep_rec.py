from dataclasses import dataclass
from pathlib import Path
from string import Template
from nexus.core.executors.shell import shell
from nexus.core.executors.base import base
from nexus.core.trackers.main_tracker import main_tracker


@dataclass(frozen=True)
class VinaReceptorBundle:
    receptor: Path
    vina_config: Path
    name: str


def _prep_rec(dcfg, receptor_bundle):
    if hasattr(receptor_bundle, "receptor"):
        receptor = receptor_bundle.receptor
        bundle = receptor_bundle
    else:
        receptor = receptor_bundle
        bundle = None
    name = Path(receptor).stem
    suffix = dcfg.common.prepared_suffix
    cleaned_receptor_pdb = f"{name}_{suffix}.pdb"
    prepped_receptor_pdbqt = f"{name}_{suffix}.pdbqt"

    @shell(dcfg)
    def clean_rec():
        chimerax = dcfg.libs.chimerax

        with open(Path(__file__).resolve().parents[0] / "templates" / "clean_rec_template.com") as f:
            vina_charge_rec_template = f.read()     

        stdin = Template(vina_charge_rec_template).substitute(
            receptor=receptor,
            cleaned_receptor_pdb=cleaned_receptor_pdb,
        )

        return ([chimerax, "--nogui"], stdin)
    clean_rec()


    @shell(dcfg)
    def meeko_prep_rec():
        padding = dcfg.common.padding
        import pymol2

        if bundle is not None and bundle.reference_path is not None:
            input_file = bundle.reference_path
            selection = "all"

        elif bundle is not None and bundle.selection_string is not None:
            input_file = cleaned_receptor_pdb
            selection = bundle.selection_string

        with pymol2.PyMOL() as pymol:
            pymol.start()
            pymol.cmd.load(input_file, "target")
            pymol.cmd.select("to_delete", f"target and not ({selection})")
            pymol.cmd.remove("to_delete")
            pymol.cmd.save(f"{name}_pocket.pdb", "target")

        cmd = [
                "mk_prepare_receptor.py",
                "-i",
                cleaned_receptor_pdb,
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