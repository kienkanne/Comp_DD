# Developer Guide

Quick notes for contributors and developers.

## Local setup

1. Create the conda environment and activate it:

```bash
conda env create -f environment.yaml
conda activate myproject
pip install -e .
```

2. Run a pipeline locally for quick testing:

```bash
nexus dock vina -c build/sample_configs/sample_docking.yaml
nexus dock dock6 -c build/sample_configs/sample_docking.yaml
nexus prep sysmd -c examples/sysmd_config.yaml
nexus md amber -c build/sample_configs/amber_md.yaml
```

Check `artifacts/` and `results/` for produced files during development.

## Receptor Bundle Architecture

Receptor configuration is fully normalized at config-load time:

1. `load_dock_config()` calls `validate_and_normalize_receptors()` in `src/nexus/dock/dock_config.py`.
2. This function:
   - Extracts receptor files from the configured paths/directories.
   - Parses per-receptor selection CSVs (if provided) to map receptor names to selection strings.
   - Matches reference pocket files to receptors by base name (if multiple references are provided).
   - Builds `ReceptorConfigBundle` objects with:
     - `receptor: Path` — the receptor file path.
     - `name: str` — the receptor name.
     - `selection_string: Optional[str]` — the resolved PyMOL selection.
     - `reference_path: Optional[Path]` — the matched reference pocket file.
   - Attaches the list of bundles to `cfg.receptors.bundles`.
3. Prep functions in Vina and DOCK6 accept receptor bundles and prefer their pre-resolved values:
   - If a bundle has `selection_string`, it is used directly.
   - If a bundle has `reference_path`, it is used directly.
   - Legacy `cfg.receptors.selection`/`cfg.receptors.reference` parsing is preserved for compatibility.

This design ensures selection CSV parsing and reference matching happen once at config-load time, making errors visible immediately and avoiding confusing runtime failures.

## Adding a new pipeline backend

1. Create a new backend package under `src/nexus/dock/` with a pipeline class.
2. Implement helper functions and decorate IO/exec functions with `@main_tracker` and the execution wrappers in `src/nexus/core/executors`.
3. Add a command in `src/nexus/cli/dock.py` and expose it from `src/nexus/cli/main.py`.

## Testing

- The repository includes basic tests under `tests/`. Run them with `pytest`.
- When testing receptor configuration, verify that `validate_and_normalize_receptors()` correctly parses selection CSVs and resolves references before the pipeline runs.
- Test multiple receptors with per-receptor selection CSVs to ensure bundle-building logic handles CSV parsing correctly.

## Debugging tips

- Check `run.log` in the configured `working_dir` for runtime output and stack traces.
- Inspect `manifest.json` and `state.json` to see which stages completed and their timings.
- When developing, use small ligand CSVs and reduce `n_jobs` to iterate quickly.

## Validation development

The validation workflow is implemented in `src/nexus/validate/validate_config.py` and `src/nexus/validate/rmsd.py`.

- `load_validate_config()` loads the unified config and overwrites receptor/ligand inputs when `validation.data` is set.
- `compute_validation_rmsds()` computes RMSDs for Vina (`.pdbqt`) and DOCK6 (`.mol2`) outputs.
- CLI support is provided by `nexus validate vina` and `nexus validate dock6`.

The validation dataset structure is intentionally generic and is recommended for future test sets. Use a single root folder containing recursive validation entries with `_protein.pdb`, `_pocket.pdb`, and `_ligand.sdf` files.
