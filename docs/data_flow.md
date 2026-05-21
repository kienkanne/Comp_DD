# Data Flow

This document explains the per-run data flow from inputs to final outputs.

1. Inputs

   - Receptor files or directories configured under `receptors`.
   - Docking config YAML that points to executables, receptor input, and common parameters.
   - Ligand input configured under `ligands` in the same unified config file.

2. Configuration loading

   - `load_dock_config(path)` builds a `DockConfig` and:
     - Calls `validate_and_normalize_receptors()` to:
       - Parse per-receptor selection CSVs (if `pocket_option: selection` and a CSV file is provided).
       - Match reference pocket files to receptors by base name (if `pocket_option: reference` and multiple references are provided).
       - Build `ReceptorConfigBundle` objects with resolved selection/reference for each receptor.
       - Attach bundles to `cfg.receptors.bundles`.
     - Augments `cfg.common` with:
       - `working_dir` and `results_dir` (each appended with `project_name`)
       - `logger` (file + stdout)
       - `manifest` (writes `manifest.json`)
       - `runstate` (writes `state.json` for checkpoints)
   - The pipeline uses receptor bundles from `cfg.receptors.bundles` directly when calling prep functions.

3. Pipeline orchestration

   - CLI triggers one of the docking commands (`nexus dock vina`, `nexus dock dock6`) or validation commands (`nexus validate vina`, `nexus validate dock6`).
   - Each pipeline executes a fixed sequence of stages:
     - Resolve or prepare ligands.
     - Prepare receptors (using pre-built bundles from `cfg.receptors.bundles`).
     - Docking.
     - Write summary CSV.
     - Copy outputs.
   - Validation workflows additionally compute per-receptor RMSD CSVs for the scored poses.

4. Parallel execution

   - Per-ligand external steps are executed via `nexus.core.executors.gnu_parallel`, which builds command lists and invokes GNU `parallel` with `common.n_jobs`.

5. Outputs

   - The working directory contains intermediate files and `run.log`, `manifest.json`, and `state.json`.
   - The results directory mirrors selected outputs and contains a `poses/` folder and the `<project_name>_<receptor>_docking_summary.csv`.

6. Checkpointing and resume

   - `main_tracker` and `State` allow stages to be checkpointed; state can be inspected to resume completed outputs.

7. Example files

   - `run.log` — combined console/file log.
   - `manifest.json` — stage timings and final status.
   - `state.json` — per-stage checkpoint outputs.



