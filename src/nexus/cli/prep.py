import typer
from typing import Optional
from pathlib import Path
from nexus.prep.prep_config import load_prep_config, PrepConfig


app = typer.Typer(help="Run fetch protein and ligand structures from RCSB pipelines")

@app.command()
def rec(config: Optional[Path] = typer.Option(None, "-c", "--config", help="Path to config YAML"),
          input: Optional[Path] = typer.Option(None, "-i", "--input", help="Input receptor to be prepared"),
          output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output protein to be prepared"),
          suffix: Optional[str] = typer.Option(None, "-s", "--suffix", help="Suffix of output protein"),
          dry: bool = typer.Option(False, "-d", "--dry", help="Remove water from protein")):
    """Run the protein cleaning preparation with ChimeraX pipeline."""
    from nexus.prep.rec.pipeline import RecPipeline

    if config and config.exists():
        pcfg = load_prep_config(config)
    else:
        pcfg = PrepConfig()

    # Config flag is already enough for all inputs
    # If additional flags are used, they overwrite the config
    cli_overrides = {
        "common": {
            k: v for k, v in {
                "input": input,
                "output": output,
                "suffix": suffix
            }.items() if v is not None
        },
        "rec": {
            k: v for k, v in {
                "dry": dry,
            }.items() if v is not None        
        }
    }

    if config and config.exists():
        pcfg = load_prep_config(config)
    else:
        # Safely creates defaults for everything
        pcfg = PrepConfig() 

    if cli_overrides:
        # Deep merge using a simple dict unpacking trick
        full_data = pcfg.model_dump()
        for key, sub_dict in cli_overrides.items():
            full_data[key] = {**full_data.get(key, {}), **sub_dict}
            
        pcfg = PrepConfig.model_validate(full_data)

    # 5. Run pipeline
    RecPipeline(pcfg=pcfg)._run()
