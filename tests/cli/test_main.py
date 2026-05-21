import subprocess
import sys


def test_nexus_cli_help():
    result = subprocess.run([sys.executable, "-m", "nexus.cli.main", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "dock" in output
    assert "validate" in output
    assert "fetch" in output


def test_nexus_validate_help():
    result = subprocess.run([sys.executable, "-m", "nexus.cli.main", "validate", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "vina" in output
    assert "dock6" in output


def test_nexus_fetch_help():
    result = subprocess.run([sys.executable, "-m", "nexus.cli.main", "fetch", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "rcsb" in output
