from pydantic import BaseModel
from nexus.prep.prep_config import PrepConfig
from nexus.core.extract_files import extract_files
from nexus.prep.mutate._chimerax_mutate import chimerax_mutate


class MutatePipeline(BaseModel):
    pcfg: PrepConfig

    def _run(self):
        input = self.pcfg.common.input
        output = self.pcfg.common.output
        format = self.pcfg.common.format
        suffix = self.pcfg.common.suffix

        input = extract_files(input, ".pdb") + extract_files(input, ".cif")
        
        if not input:
            raise ValueError("Invalid input, no pdb of cif file found.")
        if format not in ("pdb", "cif"):
            raise ValueError("Output receptor format must be 'pdb' or 'cif'.")
        
        if len(input) > 1:
            output.mkdir(parents=True, exist_ok=True)
            output = [output / f"{input_file.stem}_{suffix}.{format}" for input_file in input]

        mutations: dict = self.pcfg.mutate.mutations ######

        for input_path, output_path in zip(input, output):
            chimerax_mutate(input_path, output_path)
