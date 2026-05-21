from nexus.dock.dock_config import DockConfig, _setup_dirs, validate_and_normalize_receptors
from nexus.dock.utils.extract_files import extract_files
from pathlib import Path


def load_validate_config(path):
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f)
    vcfg = DockConfig.model_validate(data)

    data = Path(vcfg.validation.data)
    protein_suffix = vcfg.validation.protein_suffix
    pocket_suffix = vcfg.validation.pocket_suffix
    ligand_suffix = vcfg.validation.ligand_suffix

    pdbs = extract_files(data, protein_suffix, recursive=True)
    reference = extract_files(data, pocket_suffix, recursive=True)
    sdfs = extract_files(data, ligand_suffix, recursive=True)

    vcfg.receptors.source = "pdb"
    vcfg.receptors.pdbs = pdbs
    vcfg.receptors.pocket_option = "reference"
    vcfg.receptors.reference = reference
    vcfg.receptors.reference_suffix = pocket_suffix

    vcfg.ligands.source = "sdf"
    vcfg.ligands.sdfs = sdfs
    vcfg.ligands.output_dir = vcfg.common.working_dir

    vcfg.common.mode = "match"

    vcfg = _setup_dirs(vcfg)

    validate_and_normalize_receptors(vcfg, vcfg.receptors.reference_suffix)

    return vcfg
