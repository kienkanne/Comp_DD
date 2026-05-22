open $raw_path
delete ligand
delete solvent
delete H
dockprep
info residues all attribute amber_name
dssp
save $fixed_path