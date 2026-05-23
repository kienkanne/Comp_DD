from pathlib import Path

def _strip_prepared_suffix(path, prepared_suffix):
    stem = Path(path).stem
    marker = f"_{prepared_suffix}"
    if stem.endswith(marker):
        return stem[: -len(marker)]
    return stem