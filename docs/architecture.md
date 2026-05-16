# Architecture

## Overview

This project implements end-to-end molecular docking pipelines organized around a small set of reusable components: a CLI entrypoint, a typed configuration object, pipeline classes for each docking backend, lightweight executors for running external programs, and helper utilities for logging, manifesting, and checkpointing.

The high-level pipeline sequence is:

- Prepare ligands
- Prepare receptor / define box or spheres
- Run docking jobs (parallelized)
- Parse scores and write a summary CSV
- Copy selected outputs to `results`
- Finalize manifest/state

## Package layout

- `compdd.cli` — CLI entrypoint and subcommands ([src/compdd/cli/main.py](src/compdd/cli/main.py#L1-L80)).
- `compdd.config` — Pydantic models and `load_config()` that builds `RootConfig` and attaches `logger`, `manifest`, and `runstate` ([src/compdd/config.py](src/compdd/config.py#L1-L200)).
- `compdd.vina`, `compdd.dock6` — pipeline orchestrators (`VinaPipeline` and `DOCK6Pipeline`) that call a small set of helpers in `docking_utils`.
- `compdd.docking_utils` — step implementations (ligand prep, receptor prep, parsing, summary, copying) such as `_ligands_prep.py`, `_write_summary_csv.py`, and `_copy_to_results.py`.
- `compdd.executors` — process runners and decorators (`base.py`, `gnu_parallel.py`) that manage working directories and invoke external commands via GNU `parallel`.
- `compdd.utils` — supporting utilities: `logging_utils`, `manifest`, `runstate` and `main_tracker` for logging, metadata, checkpointing, and stage tracking.

## Execution model

Pipelines are implemented as small dataclass wrappers (e.g., `VinaPipeline(cfg).run()`) which orchestrate a sequence of pure helper functions. Helpers that perform IO or execute external programs are wrapped with decorators:

- `@main_tracker(cfg, "Stage Name")` — records stage start/done/failed in the manifest and `runstate`, and logs progress.
- `@base(cfg)` — switches to the configured working directory for the duration of the wrapped function and ensures the original cwd is restored.
- `@gnu_parallel(cfg)` — builds commands returned by the inner function and runs them through GNU `parallel`, capturing stdout/stderr and returning per-job outputs.

This keeps orchestration code simple while providing consistent logging, manifesting, and checkpointing.

## Pipelines

- `VinaPipeline` ([src/compdd/vina/vina_pipeline.py](src/compdd/vina/vina_pipeline.py#L1-L200)) — calls `_ligands_prep`, `_vina_prep_rec`, `_vina_docking`, `_write_summary_csv`, and `_copy_to_results`.
- `DOCK6Pipeline` ([src/compdd/dock6/dock6_pipeline.py](src/compdd/dock6/dock6_pipeline.py#L1-L200)) — similar flow but uses DOCK6-specific prep and docking helpers.

## Checkpointing & metadata

`Manifest` writes a safe JSON manifest with stage timings and overall status (`manifest.json`). `State` provides simple checkpointing (`state.json`) that `main_tracker` can consult to skip completed stages when configured to do so.

## Outputs

- `run.log` — combined console + file log
- `manifest.json` — stage metadata and timings
- `state.json` — checkpointing state
- `poses/` — per-ligand scored pose files
- `<receptor>_docking_summary.csv` — summary CSV of top poses

Working paths are configured via `common.working_dir` and `common.results_dir`. `load_config()` appends the `project_name` to both paths, so the effective working and results folders are under the configured parents.

## Extensibility

To add a new backend pipeline:

1. Add a new subpackage `compdd.<backend>` containing a `<backend>_pipeline.py` that follows the pattern in `vina`/`dock6`.
2. Implement helper functions in `docking_utils` (or new helpers in the backend package) and decorate IO/exec functions with `@main_tracker` and `@base`/`@gnu_parallel` as appropriate.
3. Add a CLI subparser in `src/compdd/cli/main.py` that constructs and runs the new pipeline.

## Useful files

- CLI: [src/compdd/cli/main.py](src/compdd/cli/main.py#L1-L120)
- Config: [src/compdd/config.py](src/compdd/config.py#L1-L220)
- Executors: [src/compdd/executors/base.py](src/compdd/executors/base.py#L1-L120), [src/compdd/executors/gnu_parallel.py](src/compdd/executors/gnu_parallel.py#L1-L240)
- Helpers: [src/compdd/docking_utils/_ligands_prep.py](src/compdd/docking_utils/_ligands_prep.py#L1-L220)
- Utilities: [src/compdd/utils/manifest.py](src/compdd/utils/manifest.py#L1-L240), [src/compdd/utils/runstate.py](src/compdd/utils/runstate.py#L1-L240)

---

This document is intended as a starting point for developers; see `docs/data_flow.md` and `docs/configuration.md` for complementary details.
