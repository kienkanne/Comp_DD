# Configuration Reference

This repository uses Pydantic-backed YAML configuration models with a unified dock config and specialized loaders for validation and fetch.

- Root docking config: loaded with `load_dock_config(path)` from `src/nexus/dock/dock_config.py`.
- Validation config: loaded with `load_validate_config(path)` from `src/nexus/validate/validate_config.py`.
- Fetch config: loaded with `load_fetch_config(path)` from `src/nexus/fetch/fetch_config.py`.

Run commands use a single unified config YAML file for docking and validation. Fetch uses a dedicated fetch config, while preparatory MD/system setup uses dedicated sysmd and MD configs:

```bash
nexus dock vina -c build/sample_configs/sample_docking.yaml
nexus dock dock6 -c build/sample_configs/sample_docking.yaml
nexus validate vina -c build/sample_configs/sample_docking.yaml
nexus validate dock6 -c build/sample_configs/sample_docking.yaml
nexus prep sysmd -c examples/sysmd_config.yaml
nexus md amber -c build/sample_configs/amber_md.yaml
nexus fetch rcsb -c build/sample_configs/fetch_rcsb.yaml
```

The `fetch` command downloads and cleans mmCIF receptor assemblies and SDF ligands from the RCSB API.

## Docking Config

- `libs` — locations or executable names for external programs: `obabel`, `parallel`, `vina`, `mgltools`, `dock_home`, `chimerax`, and `chimera`.
- `common.project_name` — appended to `working_dir` and `results_dir`.
- `common.working_dir` — parent path for scratch; the loader appends `project_name`.
- `common.results_dir` — parent path for final results; the loader appends `project_name`.
- `common.padding`, `common.n_jobs`, `common.max_poses` — shared runtime options.

### Receptor Configuration (resolved at config-load time)

- `receptors.source` — path to a single PDB/CIF file, a directory, or a list of paths.
- `receptors.pocket_option` — `selection` (use a selection string or CSV mapping) or `reference` (use reference pocket files).
- `receptors.selection` — selection string used for all receptors, or path to a per-receptor selection CSV file.
- `receptors.reference` — single reference pocket file, directory of references, or path; matched to receptors by base name.
- `receptors.reference_suffix` — file suffix used when matching references (default: `_pocket.pdb`).

At config-load time, `validate_and_normalize_receptors()` normalizes these fields:
- Extracts all receptor files from the provided paths/directories.
- If `pocket_option: selection` and a CSV file is provided, parses it to map receptor names to selection strings.
- If `pocket_option: reference` and multiple references are provided, matches them to receptors by base name.
- Builds `ReceptorConfigBundle` objects containing the resolved selection string or reference path for each receptor.
- Attaches these bundles to `cfg.receptors.bundles` so prep functions can use them directly.

### Docking options

- `vina` — `exhaustiveness`, `num_modes`, `cpu`, and `write_box`.
- `dock6` — `max_orientations` and `radius`.

The config loader attaches runtime-only objects to `cfg.common`: `logger`, `manifest`, and `runstate`. The CLI also sets `cfg.common.program` to `vina` or `dock6`. Receptor bundles are attached to `cfg.receptors.bundles` after validation and normalization.

## Ligand Config

- `source: smiles` prepares ligands from a SMILES CSV.
- `source: files` reads prepared ligands from a directory of files.
- `source: existing` uses already-prepared ligand files.
- `suffix` selects prepared ligand files by file suffix.
- `prepare_tool: obabel` uses Open Babel and, for Vina, MGLTools.
- `prepare_tool: meeko` uses RDKit/Meeko to produce PDBQT and converts to MOL2 with Open Babel for DOCK6.
- Vina uses `.pdbqt` prepared ligand files.
- DOCK6 uses `.mol2` prepared ligand files.

See `build/sample_configs/sample_docking.yaml`, `examples/vina_config.yaml`, and `examples/dock6_config.yaml` for practical examples.

## Prep Config

The `nexus prep` command loads a preparatory config with `load_prep_config(path)`. The `sysmd` pipeline uses this config to build solvated Amber systems for MD.

- `common.input` — receptor input file or folder.
- `common.output_dir` — output directory for generated system files.
- `common.working_dir` — scratch directory used during `sysmd` processing.
- `sysmd.system_name` — base name for the solvated system outputs.
- `sysmd.ligand` — optional prepared ligand pose file used to build a receptor-ligand complex.
- `sysmd.pose_num` — pose number to select from the supplied ligand (1-based pose index).
- `sysmd.force_field` — Amber force field name, e.g. `ff14SB` or `ff19SB`.
- `sysmd.water_model` — water model name, e.g. `tip3p` or `opc`.
- `sysmd.box_type` — solvent box type: `Box` or `Oct`.
- `sysmd.box_size` — box padding size in Angstroms.
- `sysmd.salt_conc` — salt concentration in molar units.

## MD Config

The `nexus md amber` command loads an MD config with `load_md_config(path)`.

- `common.prmtop` — input Amber topology file.
- `common.inpcrd` — input Amber coordinate file.
- `common.mask` — optional atom mask for restraints or analysis.
- `min`, `heat`, `eq`, `prod` — stage-specific settings for minimization, heating, equilibration, and production.
- `common.working_dir` / `common.results_dir` — working and results directories for MD outputs.

`nexus md openmm` currently exists as a placeholder command and is not implemented yet.

## Validation Config

Validation mode reuses the same unified docking config file, but the validation loader overwrites receptor and ligand inputs when `validation.data` is set.

- `validation.data` — path to a validation dataset root.

The validation loader expects a recursive data tree containing:

- receptor proteins as `*_protein.pdb`
- reference pockets as `*_pocket.pdb`
- ligand definitions as `*_ligand.sdf`

For example, the recommended structure under `/path/to/coreset` is:

```text
/path/to/coreset/
  entry1/
    entry1_protein.pdb
    entry1_pocket.pdb
    entry1_ligand.sdf
  entry2/
    entry2_protein.pdb
    entry2_pocket.pdb
    entry2_ligand.sdf
```

This layout is recommended for other test sets as well, since the validation loader scans recursively and matches entries by suffix.

During validation:

- receptors are loaded from `*_protein.pdb`
- reference pockets are loaded from `*_pocket.pdb`
- ligands are loaded from `*_ligand.sdf`
- `common.mode` is set to `match`

See `docs/validation.md` for the validation workflow, command usage, and expected dataset structure.
