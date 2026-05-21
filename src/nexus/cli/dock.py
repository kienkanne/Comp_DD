import typer
from pathlib import Path
from nexus.dock.dock_config import load_dock_config

app = typer.Typer(help="Run molecular docking pipelines")

@app.command()
def vina(config: Path = typer.Option(..., "-c", "--config", help="Path to config YAML")):
    """Run the Vina dock pipeline."""
    from nexus.dock.vina.pipeline import VinaPipeline
    VinaPipeline(load_dock_config(config)).run()

@app.command()
def dock6(config: Path = typer.Option(..., "-c", "--config")):
    """Run the DOCK6 dock pipeline."""
    from nexus.dock.dock6.pipeline import DOCK6Pipeline
    DOCK6Pipeline(load_dock_config(config)).run()