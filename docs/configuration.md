# Configuration Reference

This project uses a Pydantic-backed `RootConfig` loaded from YAML via `load_config(path)` in [src/compdd/config.py](src/compdd/config.py#L1-L220).

Top-level sections:

- `libs` — locations or executable names for external programs. Example keys: `obabel`, `parallel`, `vina`, `mgltools`, `dock_home`, `chimerax`, `chimera`.
- `common` — shared inputs and runtime options:
  - `project_name` (string): appended to `working_dir` and `results_dir`.
  - `working_dir` (path): parent path for scratch; `load_config()` appends `project_name`.
  - `results_dir` (path): parent for final results; `load_config()` appends `project_name`.
  - `receptor` (path): receptor PDB file.
  - `ligands_csv` (path): CSV with `smiles,name`.
  - `padding` (float, optional): pocket padding (default 5.0).
  - `n_jobs` (int): number of parallel jobs for GNU `parallel`.
  - `max_poses` (int): how many top poses to parse into the summary CSV.

- `vina` — Vina-specific options:
  - `exhaustiveness`, `num_modes`, `cpu`, `reference`, `write_box`.

- `dock6` — DOCK6-specific options:
  - `max_orientations`, `radius`, etc.

Notes:

- `load_config()` will attach runtime-only objects to `cfg.common`: `logger`, `manifest`, and `runstate`. These are not expected in your YAML file.
- For DOCK6, each job runs single-core; set `common.n_jobs` appropriately to utilize available CPU resources.

See `sample_configs/default.yaml` for a practical example.
