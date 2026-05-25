import typer
from pathlib import Path

from nexus.md.md_config import MDConfig, load_md_config

app = typer.Typer(help="Run molecular dynamics pipelines")

@app.command()
def amber(config: Path = typer.Option(..., "-c", "--config", help="Path to config YAML")):
    """Run the amber MD pipeline."""
    from nexus.md.amber.pipeline import AmberPipeline
    print (config)
    AmberPipeline(mcfg=load_md_config(config))._run()


@app.command()
def openmm(config: Path = typer.Option(..., "-c", "--config", help="Path to config YAML")):
    """Run the openmm MD pipeline."""
    print ("Work in progress ...")
    pass


@app.command()
def analyze(
    prmtop: Path = typer.Option(..., "-p", "--prmtop", help="Path to prmtop file"),
    trajin: Path = typer.Option(..., "-t", "--trajin", help="Path to trajectory file"),
    mask: str = typer.Option(..., "-m", "--mask", help="CPPTRAJ mask expression"),
    name: str | None = typer.Option(None, "-n", "--name", help="Analysis name (defaults to prmtop.stem)"),
    output_dir: Path | None = typer.Option(None, "-o", "--output-dir", help="Output directory (defaults to current working directory)"),
):
    """Run full analysis using CPPTRAJ."""
    from nexus.md.analysis.full_analyze import full_analyze

    if name is None:
        name = prmtop.stem
    if output_dir is None:
        output_dir = Path.cwd()

    full_analyze(prmtop=prmtop, trajin=trajin, mask=mask, name=name, output_dir=output_dir)
