# Developer Guide

Quick notes for contributors and developers.

## Local setup

1. Create the conda environment and activate it:

```bash
conda env create -n compdd -f environment.yaml
conda activate compdd
pip install -e .
```

2. Run a pipeline locally for quick testing:

```bash
compdd vina --config sample_configs/default.yaml
```

Check `artifacts/` and `results/` for produced files during development.

## Adding a new pipeline backend

1. Create a new package `compdd.<backend>` with a `<backend>_pipeline.py` implementing a dataclass with a `run()` method mirroring `VinaPipeline`/`DOCK6Pipeline`.
2. Implement backend helpers and decorate IO/exec functions with `@main_tracker` and `@base`/`@gnu_parallel`.
3. Add a subparser in `src/compdd/cli/main.py` and call your pipeline when the subcommand is used.

## Testing

- The repository includes basic tests under `tests/`. Run them with `pytest`.

## Debugging tips

- Check `run.log` in the configured `working_dir` for runtime output and stack traces.
- Inspect `manifest.json` and `state.json` to see which stages completed and their timings.
- When developing, use small ligand CSVs and reduce `n_jobs` to iterate quickly.
