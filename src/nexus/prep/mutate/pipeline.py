from pydantic import BaseModel
from nexus.prep.prep_config import PrepConfig
from nexus.core.extract_files import extract_files
from nexus.prep.mutate._chimerax_mutate import chimerax_mutate


class MutatePipeline(BaseModel):
    pcfg: PrepConfig

    def _run(self):
        input = self.pcfg.common.input
        output = self.pcfg.common.output
        suffix = self.pcfg.common.suffix
        chimerax = self.pcfg.common.chimerax
        
        if self.pcfg.mutate.mutations is not None:
            sel_res = self.pcfg.mutate.mutations.split("-")
            sel = sel_res[0]
            res = sel_res[1]
            mutations = {sel: res}

        input = extract_files(input, [".pdb", ".cif"])
        if not input:
            raise ValueError("Invalid input, no pdb of cif file found.")
        
        if suffix is None:
            suffix = "mutated.pdb"
        if ".pdb" not in suffix and ".cif" not in suffix:
            raise ValueError("Output receptor format must be 'pdb' or 'cif'.")

        if len(input) > 1:
            output = output if output is not None else input[0].parent # Make output a directory
            output.mkdir(parents=True, exist_ok=True)
            for input_path in input:
                output_path = input_path.parent / f"{input_path.stem}_{suffix}"
                chimerax_mutate(input_path, output_path, mutations, chimerax)

        else:
            input = input[0]
            output = output if output is not None else input.parent / f"{input.stem}_{suffix}"
            chimerax_mutate(input, output, mutations, chimerax)

