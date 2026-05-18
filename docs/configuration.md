# Configuration Reference

CompDD now uses two Pydantic-backed YAML configs:

- Docking config: loaded with `load_docking_config(path)` from `src/compdd/configs/docking_config.py`.
- Ligand config: loaded with `load_ligands_config(path, program=...)` from `src/compdd/configs/ligands_config.py`.

Run commands pass the docking program into both configs at runtime:

```bash
compdd run_vina --config sample_configs/sample_docking.yaml --ligands sample_configs/sample_ligands.yaml
compdd run_dock6 --config sample_configs/sample_docking.yaml --ligands sample_configs/sample_ligands.yaml
```

## Docking Config

- `libs` — locations or executable names for external programs: `obabel`, `parallel`, `vina`, `mgltools`, `dock_home`, `chimerax`, and `chimera`.
- `common.project_name` — appended to `working_dir` and `results_dir`.
- `common.working_dir` — parent path for scratch; the loader appends `project_name`.
- `common.results_dir` — parent path for final results; the loader appends `project_name`.
- `common.receptor` — receptor PDB file.
- `common.prepared_suffix` — suffix used as `<name>_<prepared_suffix>.<ext>` for prepared receptor files.
- `common.padding`, `common.n_jobs`, `common.max_poses`, `common.pocket_selection` — shared runtime options.
- `vina` — `exhaustiveness`, `num_modes`, `cpu`, `reference`, and `write_box`.
- `dock6` — `max_orientations` and `radius`.

The docking loader attaches runtime-only objects to `cfg.common`: `logger`, `manifest`, and `runstate`. The CLI also sets `cfg.common.program` to `vina` or `dock6`.

## Ligand Config

- `source: smiles` prepares ligands from `smiles_csv`.
- `source: files` reads prepared ligands from `ligands_dir`.
- `prepared_suffix` is interpreted as `<ligand_name>_<prepared_suffix>.<ext>`.
- `prepare_tool: obabel` uses Open Babel and, for Vina, MGLTools.
- `prepare_tool: meeko` uses RDKit/Meeko to produce PDBQT and converts to MOL2 with Open Babel for DOCK6.
- Vina reads `*_<prepared_suffix>.pdbqt`.
- DOCK6 reads `*_<prepared_suffix>.mol2`.

See `sample_configs/sample_docking.yaml` and `sample_configs/sample_ligands.yaml` for practical examples.
