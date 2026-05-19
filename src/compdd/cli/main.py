import argparse
from pathlib import Path
from compdd.configs.docking_config import load_config
from compdd.configs.ligands_config import load_ligands_config


def add_config_arg(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to config YAML file",
    )
    return parser


def add_ligands_arg(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--ligands",
        type=Path,
        required=True,
        help="Path to ligand preparation/input YAML file",
    )
    return parser


def main():
    parser = argparse.ArgumentParser(prog="compdd", description="Computational tools for drug discovery")
    subparsers = parser.add_subparsers(dest="command", required=True)

    vina_parser = subparsers.add_parser("run_vina", help="Full Vina docking pipeline")
    add_config_arg(vina_parser)
    add_ligands_arg(vina_parser)

    dock6_parser = subparsers.add_parser("run_dock6", help="Full DOCK6 docking pipeline")
    add_config_arg(dock6_parser)
    add_ligands_arg(dock6_parser)

    amber_md_parser = subparsers.add_parser("amber_md", help="Full AMBER molecular dynamics pipeline")
    add_config_arg(amber_md_parser)

    args = parser.parse_args()

    if args.command == "run_vina":
        from compdd.vina.vina_pipeline import VinaPipeline

        cfg = load_config(args.config)
        cfg.common.program = "vina"
        ligands_cfg = load_ligands_config(args.ligands, program=cfg.common.program)
        VinaPipeline(cfg, ligands_cfg).run()
        return True

    elif args.command == "run_dock6":
        from compdd.dock6.dock6_pipeline import DOCK6Pipeline

        cfg = load_config(args.config)
        cfg.common.program = "dock6"
        ligands_cfg = load_ligands_config(args.ligands, program=cfg.common.program)
        DOCK6Pipeline(cfg, ligands_cfg).run()
        return True

    elif args.command == "amber_md":
        return False  


if __name__ == "__main__":
    main()
