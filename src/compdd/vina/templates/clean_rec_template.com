open $receptor
delete solvent
delete ligand
dockprep
save ${cleaned_receptor_pdb}
