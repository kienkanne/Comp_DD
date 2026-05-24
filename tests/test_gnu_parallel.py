import pytest
from types import SimpleNamespace

from nexus.core.executors.gnu_parallel import gnu_parallel


def test_gnu_parallel_skip_filters_failed_jobs(monkeypatch):
    def fake_run(cmd, capture_output, text, input):
        stdout = (
            "__START__0__\nhello\n__STATUS__0__0__\n__END__0__\n"
            "__START__1__\nerror text\n__STATUS__1__1__\n__END__1__\n"
            "__START__2__\nworld\n__STATUS__2__0__\n__END__2__\n"
        )
        return SimpleNamespace(stdout=stdout, stderr="", returncode=1)

    monkeypatch.setattr(
        "nexus.core.executors.gnu_parallel.subprocess.run",
        fake_run,
    )

    @gnu_parallel(n_jobs=2, skip=True)
    def get_cmds():
        return [["echo", "hello"], ["bash", "-lc", "exit 1"], ["echo", "world"]]

    result = get_cmds()

    assert result == ["hello", "world"]
