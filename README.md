# Computational tools for drug discovery

## Introduction

This repository runs end-to-end molecular docking workflows for a receptor PDB and a CSV of ligands. It currently supports:

- AutoDock Vina
- DOCK6

The pipeline prepares the receptor, prepares each ligand from SMILES, docks ligands in parallel with GNU parallel, copies selected outputs to a results folder, and writes a docking summary CSV sorted by the best pose score.

## Installation

Install Conda (Miniconda or Anaconda), then create the environment:

```bash
conda env create -n myproject -f environment.yaml
conda activate myproject
```

Install the Python package in editable mode from the repository root:

```bash
pip install -e .
```

Other needed tools that have to be installed:

- DOCK6: See [https://github.com/docking-org/dock6](https://github.com/docking-org/dock6)
- MGLTOOLS: See [https://ccsb.scripps.edu/mgltools/downloads](https://ccsb.scripps.edu/mgltools/downloads)
- ChimeraX: See [https://www.cgl.ucsf.edu/chimerax/download.html](https://www.cgl.ucsf.edu/chimerax/download.html)
- Chimera: See [https://www.cgl.ucsf.edu/chimera/download.html](https://www.cgl.ucsf.edu/chimera/download.html) 

Most command-line tools can be installed into the active conda/mamba environment and referenced by executable name in the config:

```yaml
obabel: "obabel"
parallel: "parallel"
vina: "vina"
```

Some others needed to be pointed at their installed directories:

```yaml
mgltools: "$HOME/Apps/mgltools_1.5.7/mgltools_x86_64Linux2_1.5.7/"
dock_home: "$HOME/Apps/dock6/"
```

## Running

Use the CLI with a config file:

```bash
compdd run-vina --config sample_configs/default.yaml
compdd run-dock6 --config sample_configs/default.yaml
```

## Ligand CSV

The ligand file must be a CSV with exactly this header:

```csv
smiles,name
CC(=O)OC1=CC=CC=C1C(=O)O,aspirin
CC1=C(C=C(C=C1)C(C)C)O,carvacrol
```

Ligand names are used in output filenames, so keep them short and file-friendly. The loader sanitizes names and raises an error for duplicate names after sanitization. Each SMILES string is validated with Open Babel before docking starts.

## Config Format

See [sample_configs/default.yaml](sample_configs/default.yaml) for a working example.

### `libs`

Tool locations and executable names.

```yaml
libs:
  chimerax: "/usr/local/chimerax/bin/ChimeraX"
  chimera: "/usr/local/chimera/chimera-1.8/bin/chimera"

  mgltools: "/localscratch/kbui/Apps/mgltools_1.5.7/mgltools_x86_64Linux2_1.5.7/"
  dock_home: "/localscratch/kbui/Apps/dock6/"

  obabel: "obabel"
  parallel: "parallel"
  vina: "vina"
```

### `common`

Inputs, scratch directory, results directory, and batch settings.

```yaml
common:
  project_name: vina_mpro_catalytic
  working_dir: "/localscratch/kbui/Comp_DD/artifacts"
  results_dir: "/localscratch/kbui/Comp_DD/results/"

  receptor: "/localscratch/kbui/Comp_DD/data/6W63.pdb"
  ligands_csv: "/localscratch/kbui/Comp_DD/data/ligands_list.csv"
  
  pocket_selection: "chain A and resi 41+145+140+143+144+145+163+166"
  padding: 5.0
  n_jobs: 16
  max_poses: 8
```
- `project_name`: name of the folder in working_dir and results_dir
- `working_dir`: parent folder of scratch space where intermediate files are written.
- `results_dir`: parent folder of where final selected outputs and summary CSV are copied.
- `receptor`: starting receptor PDB.
- `ligand`: CSV path with `smiles,name`.
- `n_jobs`: total concurrent jobs.
- `max_poses`: maximum number of scores to parse per ligand into the summary CSV.

### `vina`

Vina-specific settings.

```yaml
  exhaustiveness: 32
  num_modes: 8
  reference: "/localscratch/kbui/Comp_DD/data/ref_ligand.pdb"
  cpu: 1
  write_box: True
```

- `cpu` is the CPU count per ligand job.
- `reference`: uses to represent the pocket, set to None if uses pocket_selection instead

### `dock6`

DOCK6-specific settings.

```yaml
dock6:
  max_orientations: 1000
  radius: 10.0
```

DOCK6 jobs are single-core, so the parallel job count is `common.total_cpu`.

## Outputs

The results directory contains selected final files:

- Vina poses: `*_scored.pdbqt`
- DOCK6 poses: `*_scored.mol2`
- Pipeline logs: `run.log`, `manifest.json`, `state.json`
- Summary CSV: `<receptor_stem>_docking_summary.csv`

The summary CSV has this format:

```csv
name,pose1,pose2,pose3,...
aspirin,-2.383,-1.596,-1.454,...
carvacrol,-1.917,-1.528,-1.319,...
```

Rows are sorted by `pose1`, with lower scores first.

## More Documentation

- [Architecture](docs/architecture.md)
- [Data Flow](docs/data_flow.md)
- [Configuration Reference](docs/configuration.md)
