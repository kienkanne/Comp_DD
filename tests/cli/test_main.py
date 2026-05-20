import subprocess
import sys


def test_retrieve_help():
    result = subprocess.run([sys.executable, "-m", "compdd.cli.main", "retrieve", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "--config" in result.stdout


def test_validate_run_vina_help():
    result = subprocess.run([sys.executable, "-m", "compdd.cli.main", "validate_run_vina", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "--config" in result.stdout
