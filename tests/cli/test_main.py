import os
import subprocess
import sys

ENV = dict(os.environ, PYTHONPATH=os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "src")))


def test_nexus_cli_help():
    result = subprocess.run([sys.executable, "-m", "nexus.cli.main", "--help"], env=ENV, capture_output=True, text=True)
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "dock" in output
    assert "validate" in output
    assert "fetch" in output


def test_nexus_validate_help():
    result = subprocess.run([sys.executable, "-m", "nexus.cli.main", "validate", "--help"], env=ENV, capture_output=True, text=True)
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "vina" in output
    assert "dock6" in output


def test_nexus_fetch_help():
    result = subprocess.run([sys.executable, "-m", "nexus.cli.main", "fetch", "--help"], env=ENV, capture_output=True, text=True)
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "rcsb" in output


def test_nexus_md_analyze_help():
    result = subprocess.run([sys.executable, "-m", "nexus.cli.main", "md", "analyze", "--help"], env=ENV, capture_output=True, text=True)
    assert result.returncode == 0
    output = result.stdout + result.stderr
    assert "--prmtop" in output
    assert "--trajin" in output
    assert "--mask" in output
