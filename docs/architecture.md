# Architecture

## Overview

This project implements end-to-end molecular docking pipelines organized around a small set of reusable components: a CLI entrypoint, a typed configuration object, pipeline classes for each docking backend, lightweight executors for running external programs, and helper utilities for logging, manifesting, and checkpointing.

The high-level pipeline sequence is:

- Resolve or prepare ligands
- Prepare receptor / define box or spheres
- Run docking jobs (parallelized)
- Parse scores and write a summary CSV
- Copy selected outputs to `results`
- Finalize manifest/state

## Package layout

- `nexus.cli` — CLI entrypoint and command groups ([src/nexus/cli/main.py](src/nexus/cli/main.py)).
- `nexus.cli.dock` — docking commands for `nexus dock vina` and `nexus dock dock6`.
- `nexus.cli.validate` — validation commands for `nexus validate vina` and `nexus validate dock6`.
- `nexus.cli.fetch` — fetch commands for `nexus fetch rcsb`.
- `nexus.dock` — docking configuration and shared docking helpers.
- `nexus.dock.vina` — Vina pipeline implementation.
- `nexus.dock.dock6` — DOCK6 pipeline implementation.
- `nexus.fetch` — RCSB fetch configuration, pipeline, and CIF assembly support.
- `nexus.validate` — validation config loader and RMSD analysis.
- `nexus.core.executors` — process runners and parallel execution wrappers.
- `nexus.core.trackers` — logging, manifest, and runstate support.

## Execution model

Pipelines are implemented as small dataclass wrappers (e.g., `VinaPipeline(cfg, ligands_cfg).run()`) which orchestrate a sequence of pure helper functions. Helpers that perform IO or execute external programs are wrapped with decorators:

- `@main_tracker(cfg, "Stage Name")` — records stage start/done/failed in the manifest and `runstate`, and logs progress.
- `@base(cfg)` — switches to the configured working directory for the duration of the wrapped function and ensures the original cwd is restored.
- `@shell(cfg)` — runs shell commands in the working directory and captures output.
- `@python_parallel(cfg)` — parallelizes tasks across multiple processes, with each task receiving pre-built partial functions (e.g., receptor bundles) that contain all resolved config values needed for execution.

As of 1.3.2, receptor bundles are built at config-load time and passed directly to prep functions, eliminating runtime parsing of selection CSVs and reference matching logic.

This keeps orchestration code simple while providing consistent logging, manifesting, and checkpointing.

## Pipelines

- `VinaPipeline` ([src/nexus/dock/vina/pipeline.py](src/nexus/dock/vina/pipeline.py)) — calls `_ligands_prep`, `_vina_prep_rec`, `_vina_docking`, `_write_summary_csv`, and `_copy_to_results`.
- `DOCK6Pipeline` ([src/nexus/dock/dock6/pipeline.py](src/nexus/dock/dock6/pipeline.py)) — similar flow but uses DOCK6-specific prep and docking helpers.

## Checkpointing & metadata

`Manifest` writes a safe JSON manifest with stage timings and overall status (`manifest.json`). `State` provides simple checkpointing (`state.json`) that `main_tracker` can consult to skip completed stages when configured to do so.

## Outputs

- `run.log` — combined console + file log
- `manifest.json` — stage metadata and timings
- `state.json` — checkpointing state
- `poses/` — per-ligand scored pose files
- `<project_name>_<receptor>_docking_summary.csv` — summary CSV of top poses

Working paths are configured via `common.working_dir` and `common.results_dir`. The dock config loader appends `project_name` to both paths, so the effective working and results folders are under the configured parents.

## Extensibility

To add a new backend pipeline:

1. Add a new subpackage under `src/nexus/dock/` containing a backend pipeline class.
2. Implement helper functions and decorate IO/exec functions with `@main_tracker` and the appropriate execution wrappers.
3. Add a new command in `src/nexus/cli/dock.py` and expose it via `src/nexus/cli/main.py`.

## Useful files

- CLI: [src/nexus/cli/main.py](src/nexus/cli/main.py)
- Dock config: [src/nexus/dock/dock_config.py](src/nexus/dock/dock_config.py)
- Docking pipelines: [src/nexus/dock/vina/pipeline.py](src/nexus/dock/vina/pipeline.py), [src/nexus/dock/dock6/pipeline.py](src/nexus/dock/dock6/pipeline.py)
- Fetch: [src/nexus/fetch/pipeline.py](src/nexus/fetch/pipeline.py), [src/nexus/fetch/rcsb.py](src/nexus/fetch/rcsb.py)
- Validation: [src/nexus/validate/validate_config.py](src/nexus/validate/validate_config.py), [src/nexus/validate/rmsd.py](src/nexus/validate/rmsd.py)
- Executors: [src/nexus/core/executors/base.py](src/nexus/core/executors/base.py), [src/nexus/core/executors/gnu_parallel.py](src/nexus/core/executors/gnu_parallel.py)
- Trackers: [src/nexus/core/trackers/manifest.py](src/nexus/core/trackers/manifest.py), [src/nexus/core/trackers/runstate.py](src/nexus/core/trackers/runstate.py)

---

This document is intended as a starting point for developers; see `docs/data_flow.md` and `docs/configuration.md` for complementary details.
