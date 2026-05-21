import typer
from pathlib import Path

app = typer.Typer(help="Run molecular dynamics pipelines")

@app.command()
def amber(config: Path = typer.Option(..., "-c", "--config", help="Path to config YAML")):
    """Run the amber MD pipeline."""
    print ("Work in progress ...")
    pass

@app.command()
def openmm(config: Path = typer.Option(..., "-c", "--config", help="Path to config YAML")):
    """Run the openmm MD pipeline."""
    print ("Work in progress ...")
    pass
