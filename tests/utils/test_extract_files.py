from pathlib import Path
import tempfile
import os

from nexus.dock.utils.extract_files import extract_files


def test_extract_files_directory_and_file(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    f1 = d / "a.sdf"
    f2 = d / "b.sdf"
    f3 = d / "ignore.txt"
    f1.write_text("x")
    f2.write_text("y")
    f3.write_text("z")

    files = extract_files(d, ".sdf")
    names = sorted([p.name for p in files])
    assert names == ["a.sdf", "b.sdf"]

    single = extract_files(f1, ".sdf")
    assert single == [f1]


def test_extract_files_accepts_list_input(tmp_path):
    f1 = tmp_path / "a.sdf"
    f1.write_text("x")
    result = extract_files([f1], ".sdf")
    assert result == [f1]
