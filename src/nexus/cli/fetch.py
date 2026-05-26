import typer
from typing import Optional, List
from pathlib import Path


app = typer.Typer(help="Run fetch protein and ligand (noncovalent only) structures from RCSB pipelines")

@app.command()
def rcsb(input: Optional[List[str]] = typer.Option(None, "-i", "--input", help="Input PDB ids or text file containing id in each row"),
         output_dir: Optional[Path] = typer.Option(None, "-o", "--output_dir", help="Output directory"),
         ligand_name: Optional[str] = typer.Option(None, "-l", "--ligand_name", help="Option to include ligand name from CCD in output file")):
    """Run the fetch from RCSB pipeline."""

    from nexus.fetch.fetch_config import FetchConfig

    fcfg = FetchConfig(input=input,
                       output_dir=output_dir,
                       ligand_name=ligand_name)

    from nexus.fetch.pipeline import FetchPipeline
    FetchPipeline(fcfg=fcfg).run()
