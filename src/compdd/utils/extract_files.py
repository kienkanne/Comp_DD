from pathlib import Path

def extract_files(input_path, pattern, recursive=False):
    """
    Accepts exactly one file path or exactly one directory path.

    - If `input_path` is a file, returns a list containing that file (no pattern filtering).
    - If `input_path` is a directory, returns child files matching `*{pattern}`. Recursive is an option

    NOTE: Passing a list is no longer supported to avoid ambiguity when matching references/selections.
    """
    # Normalize input and enforce single-path API
    if isinstance(input_path, (str, Path)):
        path = Path(input_path)
    else:
        raise TypeError("extract_files() expects a single file path or a single directory path, not a list.")

    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if path.is_dir():
        if recursive:
            matched = sorted(list(path.rglob(f'*{pattern}')))
        else:
            matched = sorted(list(path.glob(f'*{pattern}')))
        return matched
    else:
        return [path]
