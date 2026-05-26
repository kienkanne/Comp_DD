from types import SimpleNamespace

from nexus.core.executors.gnu_parallel import gnu_parallel


def test_gnu_parallel_quotes_commands_and_uses_joblog(tmp_path, monkeypatch):
    calls = {}

    class FakeNamedTemporaryFile:
        def __init__(self, mode, dir, delete):
            self.path = tmp_path / "joblog.tsv"
            self.name = str(self.path)

        def __enter__(self):
            self.path.write_text("")
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_makedirs(path, exist_ok):
        calls["scratch"] = path

    def fake_run(cmd, capture_output, text, input, env):
        calls["cmd"] = cmd
        calls["input"] = input
        calls["env"] = env
        joblog = cmd[cmd.index("--joblog") + 1]
        with open(joblog, "w") as handle:
            handle.write("Seq\tHost\tStarttime\tJobRuntime\tSend\tReceive\tExitval\tSignal\tCommand\n")
            handle.write("1\t:\t0\t0\t0\t0\t0\t0\techo hello\n")
        return SimpleNamespace(
            stdout="1\thello\n",
            stderr="",
            returncode=0,
            check_returncode=lambda: None,
        )

    monkeypatch.setattr("nexus.core.executors.gnu_parallel.os.makedirs", fake_makedirs)
    monkeypatch.setattr("nexus.core.executors.gnu_parallel.tempfile.NamedTemporaryFile", FakeNamedTemporaryFile)
    monkeypatch.setattr("nexus.core.executors.gnu_parallel.subprocess.run", fake_run)

    @gnu_parallel(n_jobs=2)
    def get_cmds():
        return [["echo", "hello world"]]

    assert get_cmds() == ["hello"]
    assert calls["cmd"][:2] == ["parallel", "--tag"]
    assert "-j" in calls["cmd"]
    assert "echo 'hello world'" in calls["input"]
    assert calls["env"]["TMPDIR"] == calls["scratch"]
