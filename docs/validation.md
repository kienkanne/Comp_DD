# Validation Guide

This repository supports dedicated validation workflows for Vina and DOCK6.

## Commands

Use the same unified docking config YAML file for validation:

```bash
nexus validate vina -c build/sample_configs/sample_docking.yaml
nexus validate dock6 -c build/sample_configs/sample_docking.yaml
```

## Validation dataset structure

The validation loader expects a root directory containing recursive validation entries. Each entry should include:

- `*_protein.pdb` — receptor protein structure
- `*_pocket.pdb` — reference pocket structure
- `*_ligand.sdf` — validation ligand set

Validation suffixes are configurable via `validation.protein_suffix`, `validation.pocket_suffix`, and `validation.ligand_suffix`.

Recommended layout for a coreset root such as `/path/to/coreset`:

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

This layout is recommended for other validation collections as well. The loader scans recursively and matches files by suffix, so directories may be organized however is most convenient.

## Config settings

Add or update the `validation` section in the unified config:

```yaml
validation:
  data: "/path/to/coreset"
```

When `validation.data` is set, the validation loader automatically overrides the receptor and ligand inputs from the main config. It also forces `common.mode` to `match`.

## What validation does

Validation mode performs a full docking workflow on the test dataset and then computes RMSDs for the scored poses.

- `nexus validate vina` uses the Vina docking backend and parses output poses from `.pdbqt` files.
- `nexus validate dock6` uses the DOCK6 backend and parses output poses from `.mol2` files.
- RMSD results are written as per-receptor CSV summaries.

## Output locations

The validation run writes normal pipeline outputs to the configured `common.working_dir` and `common.results_dir`, including:

- intermediate files in the working directory
- final selected output files copied to the results directory
- docking summary CSVs
- validation RMSD CSVs for each receptor

## Recommended workflow

1. Prepare a coreset root matching the expected dataset structure.
2. Use the same unified config file that works for docking.
3. Run `nexus validate vina` or `nexus validate dock6`.
4. Inspect the resulting scoring summaries and RMSD CSVs in `results/`.

## Notes

- Validation does not require a separate config file; it reuses `build/sample_configs/sample_docking.yaml`.
- If your dataset root contains additional files, the loader ignores files that do not match the required suffix patterns.
- Keeping directories organized by entry makes it easier to map receptors, pockets, and ligands during validation.
