import typer
from pathlib import Path

app = typer.Typer(help="Run molecular docking pipelines")

@app.command()
def vina(config: Path = typer.Option(..., "-c", "--config", help="Path to config YAML")):
    """Run the Vina dock pipeline."""
    from nexus.dock.vina.pipeline import VinaPipeline
    from nexus.dock.dock_config import load_dock_config
    VinaPipeline(load_dock_config(config))._run()

@app.command()
def dock6(config: Path = typer.Option(..., "-c", "--config")):
    """Run the DOCK6 dock pipeline."""
    from nexus.dock.dock6.pipeline import DOCK6Pipeline
    from nexus.dock.dock_config import load_dock_config
    DOCK6Pipeline(load_dock_config(config))._run()