# Security and Bug Analysis

This document records code-quality, logic, reliability, and security observations from the current source tree. It is intentionally separate from user-facing workflow documentation.

## Summary

NexusMol mostly avoids shell injection by passing command arguments as lists to `subprocess.run()` or by shell-quoting commands before GNU Parallel. The larger risks are reliability issues around config handling, disabled validation paths, non-portable hard-coded paths, and workflow edge cases that can silently produce incomplete results.

Do not run NexusMol with untrusted YAML or untrusted molecular input files. Config files control executable paths, working directories, and external tool inputs.

## Findings

### Critical: CLI Import Can Require Network Access *** FIXED: Move imports to functions ***

Severity: High

Evidence:

- `src/nexus/cli/main.py:2` imports all command modules at startup.
- `src/nexus/cli/fetch.py:5` imports `FetchPipeline`.
- `src/nexus/fetch/rcsb_fetch.py:2` imports `DataQuery` at module import time.
- In the current environment, `PYTHONPATH=src python -m nexus.cli.main --help` failed because `rcsb-api` attempted to fetch the RCSB schema from `https://data.rcsb.org/graphql`.

Impact:

- `nexus --help` can fail without network access.
- Any command group can be blocked by a fetch-only dependency.
- CLI startup becomes slower and less reliable than necessary.

Recommended fix:

Move RCSB imports into the functions that use them:

```python
def get_ligands_in_structure(id):
    from rcsbapi.data import DataQuery
    ...

def rcsb_fetch(fcfg: FetchConfig):
    from rcsbapi.model import ModelQuery
    ...
```

Also keep pipeline imports inside CLI command bodies where practical, so unrelated commands do not import optional workflow dependencies.

### 1. Fetch `--config` Is Ignored *** FIXED: Fetch is small enough to remove config entirely, may add back later ***

Severity: High

Evidence:

- `src/nexus/cli/fetch.py:11` exposes `config`.
- `src/nexus/cli/fetch.py:17` always constructs `FetchConfig` from flags and never calls `load_fetch_config()`.
- `src/nexus/cli/fetch.py:13` names the Python parameter `ouput_dir`, which works for the Typer option but is easy to misuse internally.

Impact:

- Users can pass `-c fetch.yaml` and believe it was used when it was not.
- Calling `nexus fetch rcsb -c fetch.yaml` without `-i` can fail later because `fcfg.input` is `None`.

Recommended fix:

```python
@app.command()
def rcsb(
    config: Optional[Path] = typer.Option(None, "-c", "--config", help="Path to config YAML"),
    input: Optional[List[str]] = typer.Option(None, "-i", "--input", help="PDB IDs or file of IDs"),
    output_dir: Optional[Path] = typer.Option(None, "-o", "--output_dir", help="Output directory"),
    ligand_name: Optional[str] = typer.Option(None, "-l", "--ligand_name", help="Ligand output name"),
):
    if config is not None:
        fcfg = load_fetch_config(config)
        data = fcfg.model_dump()
    else:
        data = {}

    overrides = {
        "input": input,
        "output_dir": output_dir,
        "ligand_name": ligand_name,
    }
    data.update({k: v for k, v in overrides.items() if v is not None})

    fcfg = FetchConfig.model_validate(data)
    if not fcfg.input:
        raise typer.BadParameter("Provide PDB IDs with -i or set input in the config file.")

    FetchPipeline(fcfg=fcfg).run()
```

### 2. `prep sysmd` Receptor-Only Mode Fails *** FIXED ***

Severity: High

Evidence:

- `SysmdConfig.ligand` is optional in `src/nexus/prep/prep_config.py:35`.
- `SysmdPipeline` passes `None` for ligand files when no ligand is configured.
- `run_tleap()` converts `None` to the string `"None"` at `src/nexus/prep/sysmd/_tleap.py:69-70`.
- `build_tleap_cmd()` checks `is not None` at `src/nexus/prep/sysmd/_tleap.py:23`, so `"None"` is treated as a real ligand path.

Impact:

- Receptor-only sysmd configs try to load `None` as a ligand in `tleap`.
- The docs and schema imply this should work, but current command construction does not.

Recommended fix:

```python
input_dict = {
    "force_field": force_field,
    "water_model": water_model,
    "receptor_renamed": str(receptor_renamed),
    "ligand_charged": str(ligand_charged) if ligand_charged is not None else None,
    "ligand_frcmod": str(ligand_frcmod) if ligand_frcmod is not None else None,
    "box_model_solvate": f"solvate{box_type}",
    "water_model_box": f"{water_model.upper()}BOX",
    "box_size": str(box_size),
    "output_suffix": str(output_suffix),
    "n_ions": str(n_ions_dummy),
}
```

Also remove `print(stdin)` from `_tleap.py:46` or route it through a logger.

### 3. Validation Commands Are Disabled and the Validation Backend Is Stale *** Removed entirely from CLI ***

Severity: High

Evidence:

- `src/nexus/cli/validate.py:11` and `src/nexus/cli/validate.py:19` return before doing any work.
- `src/nexus/validate/rmsd.py:124` reads `vcfg.common.prepared_suffix`, which is not defined on `DockConfig.common`.
- `src/nexus/validate/rmsd.py:119` prints the full config object directly.

Impact:

- `nexus validate vina` and `nexus validate dock6` appear in CLI help but silently do nothing.
- Re-enabling the unreachable code would likely fail due to stale assumptions.

Recommended fix:

Choose one of two paths:

1. Hide validation commands until they are implemented.
2. Re-enable and update the backend.

For the second path, add an explicit config field or derive the prepared suffix from the selected backend:

```python
prepared_suffix = "_prepared"
if hasattr(vcfg.common, "prepared_suffix") and vcfg.common.prepared_suffix:
    prepared_suffix = vcfg.common.prepared_suffix
```

Then remove the early `return None` statements and add tests that verify a small validation fixture writes RMSD CSV output.

### 4. `common.mode: match` Is Incompletely Wired *** TODO: Mode "match" is experimental ***

Severity: Medium

Evidence:

- `matchmixer()` accepts a `mode` argument in `src/nexus/dock/utils/matchmixer.py:4`.
- `VinaPipeline` calls `matchmixer(rec_bundles, lig_paths)` without passing `dcfg.common.mode` at `src/nexus/dock/vina/pipeline.py:21`.
- `DOCK6Pipeline` has the same issue at `src/nexus/dock/dock6/pipeline.py:24`.
- Later code does read `dcfg.common.mode` for output naming and summary generation.

Impact:

- A config with `common.mode: match` still creates a receptor/ligand cross product, while downstream files may be named and summarized as if matching occurred.

Recommended fix:

```python
pairs = matchmixer(
    rec_bundles,
    lig_paths,
    mode=getattr(self.dcfg.common, "mode", "mix"),
)
```

Also add a test for one-to-one receptor/ligand matching by prepared names.

### 5. `final_copy()` Has a Match-Mode Attribute Bug *** FIXED ***

Severity: Medium

Evidence:

- In the `match` branch, `src/nexus/dock/utils/final_copy.py:88` loops as `for item in rec_bundles`.
- `src/nexus/dock/utils/final_copy.py:89` then reads `rec_bundles.receptor` instead of `item.receptor`.

Impact:

- If match mode is reached, result copying fails with an attribute error because the list has no `receptor` attribute.

Recommended fix:

```python
for item in rec_bundles:
    rec_path = item.receptor
    if rec_path.exists():
        shutil.copy2(rec_path, details / rec_path.name)
```

### 6. MD Analysis Does Not Restore the Original Working Directory *** FIXED ***

Severity: Medium

Evidence:

- `_run_cpptraj()` changes into `output_dir` at `src/nexus/md/analysis/_run_cpptraj.py:8`.
- The `finally` block calls `os.chdir(Path.cwd())` at `src/nexus/md/analysis/_run_cpptraj.py:28`; after the earlier `chdir`, `Path.cwd()` is already `output_dir`.

Impact:

- After `nexus md analyze`, the Python process remains in the analysis output directory.
- This is especially risky for library use, future multi-step CLI commands, or tests.

Recommended fix:

```python
def _run_cpptraj(cpptraj_input: str, output_dir: Path, name: str = "", logger=None):
    output_dir.mkdir(parents=True, exist_ok=True)
    original_cwd = Path.cwd()
    try:
        os.chdir(output_dir)
        ...
    finally:
        os.chdir(original_cwd)
```

### 7. MD Analysis Template Ignores the User Mask During Clustering *** FIXED ***

Severity: Medium

Evidence:

- Most analysis lines use `$mask`.
- `src/nexus/md/analysis/analysis_template.txt:50` hard-codes `rms :1-198@C,N,O,CA,CB`.

Impact:

- Users can pass `--mask`, see it applied to RMSD and hydrogen-bond sections, but clustering still runs on residues `1-198`.
- Small systems and non-198-residue systems can fail or produce misleading clustering.

Recommended fix:

```text
rms ${mask}@C,N,O,CA,CB \
```

Consider making the clustering atom selection a separate flag if protein masks are not always compatible.

### 8. Packaging Metadata Omits Required Runtime Dependencies

Severity: Medium

Evidence:

- `pyproject.toml:8` declares only `rcsb-api`.
- The source imports Typer, PyYAML, Pydantic, RDKit, Meeko, and other packages that are only present in `environment.yaml`.
- `full_analyze.py` copies `visual_temnplate.ipynb`, but `pyproject.toml:20` package data includes text, `.com`, and template `.py` files, not notebooks.

Impact:

- `pip install -e .` outside the conda environment can produce a broken CLI.
- Installed packages may miss the visualization notebook.

Recommended fix:

Move Python runtime dependencies that are import-time requirements into `pyproject.toml`, and include the notebook package data:

```toml
[project]
dependencies = [
  "rcsb-api",
  "typer",
  "pyyaml",
  "pydantic",
]

[tool.setuptools.package-data]
nexus = ["**/*.txt", "**/*.com", "**/templates/*.py", "**/*.ipynb"]
```

Keep heavy conda-only chemistry packages in `environment.yaml` if they are not pip-installable in the target environment, but document that pip-only installs support only a subset.

### 9. GNU Parallel Uses a Hard-Coded User-Specific Scratch Path *** FIXED ***

Severity: Medium

Evidence:

- `src/nexus/core/executors/gnu_parallel.py:15` sets `scratch_tmp = "/localscratch/kbui/tmp"`.

Impact:

- The executor is not portable across users, clusters, containers, or CI.
- It may fail with permissions errors or write outside expected project directories.

Recommended fix:

```python
scratch_tmp = os.environ.get("NEXUS_TMPDIR") or os.environ.get("TMPDIR")
if scratch_tmp is None:
    scratch_tmp = tempfile.gettempdir()
scratch_tmp = str(Path(scratch_tmp).expanduser())
```

Optionally expose `common.tmp_dir` in config for workflows that need cluster-local scratch.

### 10. Amber MD Results Omit Production Trajectories *** FIXED ***

Severity: Medium

Evidence:

- `produce()` creates production trajectory files through `_run_pmemd()` as `prod<i>.nc`.
- `src/nexus/md/amber/_copy_to_results.py:22-24` copies only `prod_ncrst` and `prod_out`.
- `src/nexus/md/amber/_copy_to_results.py:25-26` says "Delete trajectory" but deletes the production restart file from artifacts.

Impact:

- Results directories do not contain the `.nc` files that users need for `nexus md analyze`.
- The code comment does not match behavior.

Recommended fix:

Return trajectory paths from `produce()`:

```python
prod_nc = Path(working_dir) / f"prod{i}.nc"
outputs.append((prod_ncrst, prod_out, prod_nc))
```

Then copy all intended final files:

```python
for prod_ncrst, prod_out, prod_nc in outputs:
    shutil.copy2(prod_ncrst, results_dir)
    shutil.copy2(prod_out, results_dir)
    shutil.copy2(prod_nc, results_dir)
```

Only delete large artifact files after confirming the intended copy succeeded.

### 11. Ligdock Config Schema Does Not Match Runtime States *** FIXED and added n_jobs flag ***

Severity: Low

Evidence:

- `LigdockConfig.source` allows only `"smiles"` or `"csv"` in `src/nexus/prep/prep_config.py:29`.
- `LigdockPipeline` assigns `"sdf"` at runtime in `src/nexus/prep/ligdock/pipeline.py:22`.

Impact:

- A user cannot write `ligdock.source: sdf` in YAML even though the runtime uses that state internally.
- Current behavior works only because Pydantic assignment validation is not enabled.

Recommended fix:

Either make `source` private/internal or update the literal:

```python
source: Optional[Literal["smiles", "csv", "sdf"]] = "smiles"
```

Better still, remove the user-facing field and derive source from `common.input`.

### 12. Noisy Debug Prints Bypass Logging *** FIXED ***

Severity: Low

Evidence:

- `src/nexus/cli/md.py:12` prints the config path.
- `src/nexus/dock/dock6/pipeline.py:18` prints ligand suffix.
- `src/nexus/prep/sysmd/_tleap.py:46` prints the full generated `tleap` input.
- `src/nexus/validate/rmsd.py:119` prints the full validation config.

Impact:

- Logs are harder to parse.
- Config values and paths can leak to stdout unexpectedly.

Recommended fix:

Remove these prints or replace them with logger calls at `debug` level.

## Security Notes

- The code generally avoids `shell=True`, which reduces shell injection risk.
- GNU Parallel receives shell-quoted command lines. Treat all config paths and input filenames as trusted values.
- External tools parse complex molecular formats. Do not process untrusted structure files in privileged environments.
- Config files can point to arbitrary executables such as `chimerax`, `chimera`, and `dock_home/bin/dock6`. Do not run unreviewed configs.
- Generated scripts are written into output or working directories. Use project-specific scratch directories with appropriate permissions.

## Suggested Remediation Order

1. Move RCSB imports behind fetch-only code paths so CLI help works offline.
2. Fix fetch config handling and input validation.
3. Fix sysmd receptor-only `None` handling.
4. Decide whether validation should be hidden or re-enabled.
5. Repair `match` mode or remove it from public config.
6. Restore cwd correctly in MD analysis and remove the hard-coded clustering mask.
7. Make GNU Parallel scratch configurable.
8. Update packaging metadata and notebook package data.
9. Align MD result copying with expected analysis inputs.
10. Clean up debug prints and the ligdock source schema.
