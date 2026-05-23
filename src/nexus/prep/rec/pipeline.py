from pydantic import BaseModel
from nexus.prep.prep_config import PrepConfig
from nexus.core.trackers.logging_utils import setup_logger
from nexus.core.extract_files import extract_files
from nexus.prep.rec._chimerax_rec_prep import chimerax_rec_prep


class RecPipeline(BaseModel):
    pcfg: PrepConfig

    def _run(self):
        input = self.pcfg.common.input
        output = self.pcfg.common.output
        suffix = self.pcfg.common.suffix
        chimerax = self.pcfg.common.chimerax

        dry = self.pcfg.rec.dry

        input = extract_files(input, [".pdb", ".cif"])
        if not input:
            raise ValueError("Invalid input, no pdb of cif file found.")
        
        if suffix is None:
            suffix = "cleaned.pdb"
        if not any(ext in suffix for ext in ("pdb", "cif")):
            raise ValueError("Output receptor format must be 'pdb' or 'cif'.")

        if len(input) > 1:
            output = output if output is not None else input[0].parent # Make output a directory
            output.mkdir(parents=True, exist_ok=True)
            for input_path in input:
                output_path = input_path.parent / f"{input_path.stem}_{suffix}"
                log_path = setup_logger(input_path.with_suffix(".log"), time_verbose=False)  
                chimerax_rec_prep(input_path, output_path, log_path, dry, chimerax)

        else:
            input = input[0]
            output = output if output is not None else input.parent / f"{input.stem}_{suffix}"
            log_path = setup_logger(input.with_suffix(".log"), time_verbose=False)  
            chimerax_rec_prep(input, output, log_path, dry, chimerax)
