import subprocess
from pathlib import Path
import re

def chimerax_mutate(input_path: Path, output_path: Path, mutations: dict, chimerax: Path) -> Path:

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
        setattr_commands.extend([
            f"select {sel}",
            "delete H&sel",
            f"setattr sel residue name {new_name}",
            "addh sel",
            "addcharge sel",
            "info residues sel attribute amber_name"
                                 ])

    ## 2. Dynamically Build the ChimeraX Script
    script_lines = [
        f"open {input_path}"
    ]

    script_lines.extend(setattr_commands)

    script_lines.extend([
        f"save {output_path}",
        "exit"
    ])
    
    stdin = "\n".join(script_lines)

    ## 3. Execute Subprocess 
    result = subprocess.run(
        [chimerax, "--nogui"], 
        input=stdin, 
        text=True, 
        capture_output=True, 
        check=True
    )

    ## 4. Output Results
## 4. Parse the Log for Selection Failures
    log_lines = result.stdout.splitlines()
    failed_selections = []

    for i, line in enumerate(log_lines):
        # Check if ChimeraX reported an empty selection
        if "Nothing selected" in line or "Selection is empty" in line:
            # Look backwards up to 3 lines to find the command that caused it
            command_context = "Unknown command"
            for lookback in range(1, 4):
                if i - lookback >= 0 and "Executing: select" in log_lines[i - lookback]:
                    command_context = log_lines[i - lookback].strip()
                    break
            
            failed_selections.append((command_context, line.strip()))

    mutated_residues = []
    for line in result.stdout.splitlines():
        if "amber_name" in line and "residue id" in line:
            # Matches strings like: "residue id /A:8 amber_name HID index 7"
            match = re.search(r"residue id (\S+) amber_name (\S+)", line)
            if match:
                res_id, amber_name = match.groups()
                mutated_residues.append((res_id, amber_name))

    # Report clean, uncluttered errors if any occurred
    if failed_selections:
        print("\n⚠️  Warning: ChimeraX reported empty selections during execution!")
        for cmd, failure in failed_selections:
            print(f"  ❌ {failure}")
            print(f"     Triggered by: {cmd}")

    else:
        print("\n✅ Requested mutations completed: ")
        for res_id, name in mutated_residues:
            print(f"   - {res_id} was assigned {name}")

    print(f"✅ Saved mutated receptor to -> {output_path}")

    return None