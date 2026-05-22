import os
import subprocess
from pathlib import Path
import re
from nexus.fetch.fetch_config import FetchConfig
from string import Template

def chimerax_fix(fcfg: FetchConfig, raw_path: str, id: str):
    chimerax = fcfg.chimerax
    fixed_suffix = fcfg.fixed_suffix
    output_dir = fcfg.output_dir
    format = fcfg.format
    with open(Path(__file__).resolve().parents[0] / "chimerax_fix_template.com") as f:
        vina_charge_rec_template = f.read()     

    if fixed_suffix == "":
        fixed_path = os.path.join(output_dir, f"{id}.{format}")
    else:
        fixed_path = os.path.join(output_dir, f"{id}_{fixed_suffix}.{format}")

    stdin = Template(vina_charge_rec_template).substitute(
        raw_path=raw_path      ,
        fixed_path=fixed_path,
    )
    """
    chimerax_fix_template.com:
    open $raw_path
    delete ligand
    delete solvent
    delete H
    dockprep
    info residues all attribute amber_name
    dssp
    save $fixed_path
    """
    result = subprocess.run([chimerax, "--nogui"], input=stdin, text=True, capture_output=True, check=True)

    special_residues = {'HIE', 'HID', 'HIP', 'GLH', 'ASH', 'LYN', 'CYM'}
    flagged_residues = []

    # Iterate through the ChimeraX output line by line
    for line in result.stdout.splitlines():
        if "amber_name" in line and "residue id" in line:
            # Matches strings like: "residue id /A:8 amber_name HID index 7"
            match = re.search(r"residue id (\S+) amber_name (\S+)", line)
            if match:
                res_id, amber_name = match.groups()
                # If the residue is special, verify if the user explicitly asked for it
                if amber_name in special_residues:
                    flagged_residues.append((res_id, amber_name))

    ## 5. Output Results
    print(f"✅ Saved fixed biological assembly receptor to {format.upper()} -> {fixed_path}")
    
    if flagged_residues:
        print("\n⚠️  ChimeraX assigned non-standard protonation states:")
        for res_id, name in flagged_residues:
            print(f"   - {res_id} was assigned {name}")

    return fixed_path
