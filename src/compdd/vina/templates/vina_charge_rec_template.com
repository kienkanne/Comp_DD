open $receptor
delete solvent
delete ligand
dockprep
save ${prepped_receptor_pdb}
