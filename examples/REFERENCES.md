# NexusMol Structure Preparation Reference Guide

This guide provides a concise reference for **ChimeraX selection syntax** and **AMBER amino acid naming conventions**, used across the NexusMol pipeline to isolate structural components and define precise protonation states.

---

## Part 1: ChimeraX Selection Syntax

ChimeraX uses a strict hierarchical syntax to isolate models, chains, residues, and specific atoms.

### 1. The Selection Hierarchy
Elements are specified linearly from the largest container (the model) down to the smallest (the atom), using dedicated prefixes:

| Level | Prefix | Example | Description |
| :--- | :---: | :--- | :--- |
| **Model** | `#` | `#1` | Model 1 |
| **Chain** | `/` | `/A` | Chain A |
| **Residue** | `:` | `:145` | Residue 145 |
| **Atom** | `@` | `@CA` | Alpha carbon atom |

*Example:* `#1/A:145@CA` targets the **Alpha Carbon** of **Residue 145** on **Chain A** of **Model 1**.

### 2. Ranges, Lists, and Wildcards
* **Ranges (`-`):** `:41-100` *(Residues 41 through 100)*
* **Lists (`,`):** `:41,145` *(Residues 41 and 145)*
* **Wildcards (`*`):** `@H*` *(All hydrogen atoms)*
* **Combined Example:** `#1/A,B:41,145@CA` *(Alpha carbons of residues 41 and 145 on chains A and B of model 1)*

### 3. Built-in Classifications & Shorthand
ChimeraX includes predefined shorthand identifiers for standard biochemical groupings:
* **`protein`** – All amino acid residues
* **`nucleic`** – RNA and DNA residues
* **`solvent`** – Water molecules (`HOH`, `WAT`, etc.)
* **`ligand`** – Non-solvent, non-polymer organic molecules/ions
* **`ions`** – Elemental ions

### 4. Logical Operators
Combine criteria using boolean operators:
* **Intersection (`&` or `AND`):** `/A & protein` *(Only protein residues on Chain A)*
* **Union (`|` or `OR`):** `:HIS | :CYS` *(All Histidine and Cysteine residues)*
* **Negation (`~` or `NOT`):** `/A & ~solvent` *(Everything on Chain A except solvent)*

---

## Part 2: AMBER Protonation State Conventions

When preparing structures for molecular dynamics or docking, standard residue designations must often be updated to specific AMBER variants to handle explicit protonation states at target pH levels.

### 1. Histidine (HIS)
Histidine can exist as two distinct neutral tautomers depending on which imidazole nitrogen holds the hydrogen, or as a positively charged conjugate acid.

| AMBER Code | Protonation State | Structural Description |
| :--- | :--- | :--- |
| **`HID`** | Neutral ($\delta$-protonated) | Hydrogen is bound to the delta nitrogen (`ND1`). |
| **`HIE`** | Neutral ($\epsilon$-protonated) | Hydrogen is bound to the epsilon nitrogen (`NE2`). Standard solution default. |
| **`HIP`** | Positively Charged | Both `ND1` and `NE2` are protonated (net charge +1). Common in acidic environments or active sites. |

### 2. Carboxylic Acids: Aspartate (ASP) & Glutamate (GLU)
Typically deprotonated and negatively charged under physiological conditions, these can become neutral when buried or in low local pH environments.

| AMBER Code | Standard Code | Protonation State | Net Charge |
| :--- | :---: | :--- | :---: |
| **`ASP`** | `ASP` | Deprotonated / Negative carboxylate | -1 |
| **`ASH`** | `ASP` | Neutral / Protonated carboxylic acid | 0 |
| **`GLU`** | `GLU` | Deprotonated / Negative carboxylate | -1 |
| **`GLH`** | `GLU` | Neutral / Protonated carboxylic acid | 0 |

### 3. Cysteine (CYS)
Cysteine coordination depends heavily on the surrounding chemical environment and disulfide network.

| AMBER Code | Condition / Protonation State | Description |
| :--- | :--- | :--- |
| **`CYS`** | Neutral / Free Sulfhydryl | Standard reduced cysteine side chain (`-SH`). |
| **`CYX`** | Disulfide Bound | Deprotonated sulfur involved in a covalent cross-link (`-S-S-`) with another `CYX`. |
| **`CYM`** | Deprotonated (Sulfide Ion) | Negatively charged deprotonated cysteine (`-S⁻`). Often coordinates catalytic metals or acts as a nucleophile. |

### 4. Lysine (LYS)
Lysine is typically protonated at physiological pH but can surrender its proton in specific enzyme pockets.

| AMBER Code | Standard Code | Protonation State | Net Charge |
| :--- | :---: | :--- | :---: |
| **`LYS`** | `LYS` | Protonated / Positive primary amine (`-NH3⁺`) | +1 |
| **`LYSN`** (or `LYN`) | `LYS` | Neutral / Deprotonated primary amine (`-NH2`) | 0 |

---

## Official Documentation
For advanced selection expressions, zone definitions, and attribute matching, consult the official [ChimeraX User Guide: Atom Specification](https://www.rbvi.ucsf.edu/chimerax/docs/user/commands/atomspec.html).