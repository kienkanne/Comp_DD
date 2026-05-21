import typer
from pathlib import Path
from nexus.fetch.fetch_config import load_fetch_config
from nexus.fetch.pipeline import FetchPipeline

app = typer.Typer(help="Run fetch protein and ligand structures from RCSB pipelines")

@app.command()
def rcsb(config: Path = typer.Option(..., "-c", "--config", help="Path to config YAML")):
    """Run the fetch from RCSB pipeline."""
    FetchPipeline(load_fetch_config(config)).run()
