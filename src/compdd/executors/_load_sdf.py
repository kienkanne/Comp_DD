from pathlib import Path
from rdkit import Chem

def load_sdf_pipeline(input_inputs):
    """
    Accepts a single file path, a folder path, or a list of file/folder paths.
    Automatically discovers all .sdf files and yields RDKit molecules.
    """
    # 1. Normalize the input into a list of Path objects
    if isinstance(input_inputs, (str, Path)):
        input_list = [Path(input_inputs)]
    elif isinstance(input_inputs, list):
        input_list = [Path(p) for p in input_inputs]
    else:
        raise TypeError("Input must be a string path, Path object, or a list of them.")

    # 2. Resolve folders into individual SDF file paths
    final_file_list = []
    for path in input_list:
        if not path.exists():
            print(f"Warning: Path does not exist, skipping: {path}")
            continue

        if path.is_dir():
            # Find all .sdf files in the folder (case-insensitive)
            # Use path.rglob('*.sdf') instead if you want to search subfolders recursively
            folder_sdfs = sorted(list(path.glob('*.sdf')) + list(path.glob('*.SDF')))
            final_file_list.extend(folder_sdfs)
        else:
            final_file_list.append(path)

    # 3. Stream the molecules from the discovered files
    for file_path in final_file_list:
        with open(file_path, 'rb') as f:
            supplier = Chem.ForwardSDMolSupplier(f)
            for mol in supplier:
                if mol is not None:
                    yield mol
                else:
                    print(f"Warning: A molecule could not be read in {file_path}")