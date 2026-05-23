import subprocess
from pathlib import Path
import re

def chimerax_mutate(input_path: Path, output_path: Path, mutations: str) -> Path:

    ## 1. Parse and Validate Selections
    user_requested_states = {}
    setattr_commands = []
    
    for sel, new_name in mutations.items():
        # Enforce the strict {something}&:{RES} syntax
        # match.group(1) will capture the base ID (e.g., /A:41)
        # match.group(2) captures the old residue name (e.g., HIS)
        match = re.match(r"^(.*)&:([A-Za-z0-9]{3})$", sel)
        if not match:
            raise ValueError(f"Invalid selection syntax: '{sel}'. Must match '{{specifier}}&:{{RES}}'")
        
        base_id = match.group(1)
        user_requested_states[base_id] = new_name
        setattr_commands.append(f"setattr {sel} residue name {new_name}")

    ## 2. Dynamically Build the ChimeraX Script

    script_lines = [
        f"open {input_path}",
        "delete ligand",
        "delete solvent",
        "delete H"
    ]

    script_lines.extend(setattr_commands)

    script_lines.extend([
        "dockprep",
        "info residues all attribute amber_name",
        "dssp"
    ])

    # If the requested format is cif, then pdb is written first, then is converted to cif
    if output_path.suffix == "cif":
        pdb_output_path = output_path.with_suffix(".pdb")
        script_lines.extend([
            f"save {pdb_output_path}"
            f"open {pdb_output_path}"
            f"run (session, 'save {output_path}')"
        ])
    elif output_path.suffix == "pdb":
        script_lines.extend([f"save {output_path}"])
    
    stdin = "\n".join(script_lines)

    ## 3. Execute Subprocess 
    result = subprocess.run(
        ["chimerax", "--nogui", "script.py"], 
        input=stdin, 
        text=True, 
        capture_output=False, 
        check=True
    )

    if format == "cif":
        Path(output_path).unlink(missing_ok=True)

    ## 4. Output Results
    print(f"✅ Saved mutated receptor to -> {output_path}")
    
    print("\n✅ Requested mutations completed: ")
    for res_id, name in user_requested_states.items():
        print(f"   - {res_id} was assigned {name}")

    return None