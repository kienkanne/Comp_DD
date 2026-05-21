from pathlib import Path
import os
import gemmi
from rcsbapi.data import DataQuery
from rcsbapi.model import ModelQuery

from nexus.fetch.fetch_config import FetchConfig

STANDARD_AMINO_ACIDS = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE", 
    "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL"
}

# Expanded common crystallization agents and ions
IGNORED_LIGANDS = {"HOH", "DOD", "SO4", "PO4", "GOL", "EDO", "NA", "CL", "MG", "ZN", "CA", "DMS", "ACT"}


def get_ligands_in_structure(id):
    """
    Only retrieve non-covalent ligands
    """
    query = DataQuery(
        input_type="entries",
        input_ids=[id],
        return_data_list=[
            "nonpolymer_entities.pdbx_entity_nonpoly.comp_id",
            "nonpolymer_entities.pdbx_entity_nonpoly.name"
        ]
    )
    query.exec()
    response = query.get_response()
    
    ligand_ids = []
    entries = response.get("data", {}).get("entries", []) or []
    if not entries:
        return ligand_ids
        
    for entry in entries:
        # Safe fallback if nonpolymer_entities is explicitly Null/None
        nonpoly_entities = entry.get("nonpolymer_entities") or []
        for entity in nonpoly_entities:
            comp = entity.get("pdbx_entity_nonpoly", {}) or {}
            comp_id = comp.get("comp_id")
            if comp_id and comp_id not in IGNORED_LIGANDS:
                ligand_ids.append(comp_id)
                
    return ligand_ids


def fetch_rcsb(fcfg: FetchConfig):
    raw_assembly_suffix = fcfg.raw_assembly_suffix
    cleaned_suffix = fcfg.cleaned_suffix
    ligand_suffix = fcfg.ligand_suffix

    remove_waters = fcfg.remove_waters
    kept_residues = fcfg.kept_residues

    output_dir = fcfg.output_dir
    remove_raw_assembly = fcfg.remove_raw_assembly

    id_list = fcfg.id_list

    os.makedirs(output_dir, exist_ok=True)

    for id in id_list:
        print(f"\n--- Processing {id} ---")
        ligands = get_ligands_in_structure(id)
        
        model_api = ModelQuery(download=True, file_directory=output_dir)
        
        # Download Ligands as SDF
        for lig_id in ligands:
            if ligand_suffix is None:
                ligand_file = f"{id}_{lig_id}.sdf"
            elif isinstance(ligand_suffix, str):
                ligand_file = f"{id}_{ligand_suffix}.sdf"

            try:
                model_api.get_ligand(
                    entry_id=id,
                    label_comp_id=lig_id,
                    encoding="sdf",
                    filename=ligand_file
                )
                print(f"✅ Saved ligand -> {ligand_file}")
            except Exception as e:
                print(f"❌ Failed to download {lig_id}: {e}")

        # Download Biological Assembly in CIF format
        raw_assembly_file = f"{id}_{raw_assembly_suffix}.cif"
        model_api.get_assembly(
            entry_id=id, 
            encoding="cif",
            filename=raw_assembly_file
        )
        
        # 3. Clean Receptor via Gemmi
        retrieved_path = os.path.join(output_dir, raw_assembly_file)
        if cleaned_suffix == "":
            receptor_out = os.path.join(output_dir, f"{id}.cif")
        else:
            receptor_out = os.path.join(output_dir, f"{id}_{cleaned_suffix}.cif")

        doc = gemmi.cif.read_file(retrieved_path)

        st = gemmi.make_structure_from_block(doc.sole_block())
        if remove_waters:
            st.remove_waters()

        removed_ligands = set()
        for model in st:
            for chain in model:
                # Loop backwards to safely delete items while iterating
                for i in reversed(range(len(chain))):
                    res_name = chain[i].name.upper()
                    KEPT_RESIDUES = [i.upper() for i in kept_residues]

                    # Non-standard residues and covalently attached ligands are removed here
                    if res_name not in STANDARD_AMINO_ACIDS and res_name not in KEPT_RESIDUES:
                        removed_ligands.add(res_name)
                        del chain[i]

        st.make_mmcif_document().write_file(receptor_out)
        
        if removed_ligands:
            print(f"✂️  Stripped structural components/ligands: {removed_ligands}")

        if KEPT_RESIDUES:
            str_kept_residues = ", ".join(KEPT_RESIDUES)
            print (f"❗ Non-standard residues kept: {str_kept_residues}")

        if remove_raw_assembly:
            print (f"❗ Removing {retrieved_path}")
            Path(retrieved_path).unlink(missing_ok=True)
        
        print(f"✅ Saved cleaned biological assembly receptor to mmCIF -> {receptor_out}")