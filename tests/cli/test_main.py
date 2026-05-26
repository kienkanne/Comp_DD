import importlib
import sys
import types

import pytest

if sys.version_info < (3, 10):
    pytest.skip(
        "nexus.cli.md uses Python 3.10+ union type syntax",
        allow_module_level=True,
    )

pytest.importorskip("typer")
from typer.testing import CliRunner


def test_package_import_is_lightweight():
    module = importlib.import_module("nexus")

    assert module is not None


def test_cli_help_with_stubbed_fetch_dependencies():
    from nexus.cli.main import app

    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "dock" in result.output
    assert "fetch" in result.output
    assert "md" in result.output
    assert "prep" in result.output


def test_fetch_module_import_uses_test_local_rcsb_stub():
    fake_data = sys.modules["rcsbapi.data"]

    assert isinstance(fake_data, types.ModuleType)
    assert hasattr(fake_data, "DataQuery")
