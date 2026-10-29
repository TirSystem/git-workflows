"""Offline tests for tools/opengrep_scan.py: a fake opengrep, fake download, no network."""

import hashlib
import json
import runpy
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any  # JSON documents and YAML trees have no fixed shape

import pytest
import yaml
from workflow_source import REPO_ROOT, load_script

SCOPED_WORKFLOW = REPO_ROOT / ".gitea" / "scoped_workflows" / "opengrep.yml"
BINARY = b"#!/bin/sh\necho 1.33.0\n"


@pytest.fixture()
def scan(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Any:  # the loaded script module
    monkeypatch.setenv("OPENGREP_REPORT", str(tmp_path / "report.json"))
    monkeypatch.setenv("OPENGREP_HOME", str(tmp_path / "home"))
    monkeypatch.delenv("OPENGREP_BIN", raising=False)
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    module = load_script(REPO_ROOT / "tools" / "opengrep_scan.py", "opengrep_scan")
    monkeypatch.setattr(module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(module.platform, "machine", lambda: "x86_64")
    return module


def finding(
    severity: str,
    path: str = "src/app.py",
    line: int = 3,
    rule: str = "python.example.rule",
) -> dict[str, Any]:
    return {
        "check_id": rule,
        "path": path,
        "start": {"line": line},
        "extra": {"severity": severity, "message": "A message\nover two lines."},
    }


def fake_opengrep(
    monkeypatch: pytest.MonkeyPatch,
    scan: ModuleType,
    report: dict[str, Any] | None,
    returncode: int = 0,
) -> list[list[str]]:
    """Replace subprocess.run: write ``report`` where --output points and return ``returncode``."""
    calls: list[list[str]] = []

    def run(command: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if "--output" in command and report is not None:
            Path(command[command.index("--output") + 1]).write_text(json.dumps(report), encoding="utf-8")
        return subprocess.CompletedProcess(command, returncode)

    monkeypatch.setattr(scan.subprocess, "run", run)
    return calls


def fake_download(monkeypatch: pytest.MonkeyPatch, scan: ModuleType, data: bytes) -> list[str]:
    """Replace the download: write ``data`` to the target and record the URL."""
    urls: list[str] = []

    def download(url: str, target: str) -> None:
        urls.append(url)
        Path(target).write_bytes(data)

    monkeypatch.setattr(scan, "download", download)
    return urls


def test_the_scan_passes_one_config_per_rule_directory(scan: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = fake_opengrep(monkeypatch, scan, {"paths": {"scanned": []}})
    scan.run()
    command = calls[0]
    configs = [command[i + 1] for i, item in enumerate(command) if item == "--config"]
    assert [Path(config).name for config in configs] == list(scan.RULE_DIRECTORIES)
    assert all(Path(config).parent == Path(scan.rules_dir()) for config in configs)
    assert command[1] == "scan"
    for flag in ("--json", "--quiet", "--disable-version-check"):
        assert flag in command
    assert "--metrics=off" not in command


def test_a_blocking_finding_fails_the_run(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_opengrep(monkeypatch, scan, {"paths": {"scanned": ["a.py"]}, "results": [finding("ERROR")]})
    with pytest.raises(SystemExit) as stop:
        scan.run()
    out = capsys.readouterr().out
    assert stop.value.code == 1
    assert "::error file=src/app.py,line=3::[finding] python.example.rule: A message over two lines." in out
    assert "::error::[finding] 1 finding(s) of severity ERROR" in out


def test_warnings_are_listed_and_do_not_fail(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    results = [finding("WARNING"), finding("INFO", line=9)]
    fake_opengrep(monkeypatch, scan, {"paths": {"scanned": ["a.py"]}, "results": results, "version": "1.33.0"})
    scan.run()
    out = capsys.readouterr().out
    assert "::warning file=src/app.py,line=3::" in out
    assert "::notice file=src/app.py,line=9::" in out
    assert "OpenGrep 1.33.0 scanned 1 files: 2 findings, 0 blocking." in out


def test_a_repository_with_no_scanned_file_is_skipped(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_opengrep(monkeypatch, scan, {"paths": {"scanned": []}, "results": []})
    scan.run()
    assert "nothing to scan" in capsys.readouterr().out


def test_an_opengrep_failure_is_a_tool_error(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_opengrep(monkeypatch, scan, None, returncode=2)
    with pytest.raises(SystemExit):
        scan.run()
    assert "::error::[tool] OpenGrep exited with code 2." in capsys.readouterr().out


def test_a_missing_opengrep_is_a_tool_error(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def missing(command: list[str], check: bool = False) -> None:
        raise FileNotFoundError("no such file")

    monkeypatch.setattr(scan.subprocess, "run", missing)
    with pytest.raises(SystemExit):
        scan.run()
    assert "::error::[tool] OpenGrep cannot be started" in capsys.readouterr().out


def test_an_unreadable_report_is_a_tool_error(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    fake_opengrep(monkeypatch, scan, None)
    (tmp_path / "report.json").write_text("not json", encoding="utf-8")
    with pytest.raises(SystemExit):
        scan.run()
    assert "::error::[tool] The OpenGrep report" in capsys.readouterr().out


def test_the_job_summary_lists_the_findings(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    results = [finding("WARNING", line=n) for n in range(scan.SUMMARY_LIMIT + 2)]
    fake_opengrep(monkeypatch, scan, {"paths": {"scanned": ["a.py"]}, "results": results})
    scan.run()
    text = summary.read_text(encoding="utf-8")
    assert "52 findings, 0 of severity ERROR" in text
    assert "| WARNING | `python.example.rule` | src/app.py:0 |" in text
    assert "2 more in the log" in text


def test_the_bin_variable_replaces_the_installed_binary(scan: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    assert scan.opengrep_command() == scan.binary_path()
    monkeypatch.setenv("OPENGREP_BIN", "/opt/opengrep")
    assert scan.opengrep_command() == "/opt/opengrep"


def test_the_pinned_values_have_the_expected_shape(scan: ModuleType) -> None:
    assert scan.OPENGREP_VERSION == "v1.33.0"
    assert scan.OPENGREP_VERSION in scan.OPENGREP_URL
    assert len(scan.OPENGREP_SHA256) == 64
    assert len(scan.RULES_COMMIT) == 40


def test_install_verifies_the_binary_and_fetches_the_pinned_rules(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(scan, "OPENGREP_SHA256", hashlib.sha256(BINARY).hexdigest())
    urls = fake_download(monkeypatch, scan, BINARY)
    calls = fake_opengrep(monkeypatch, scan, None)
    scan.install()
    binary = Path(scan.binary_path())
    assert urls == [scan.OPENGREP_URL]
    assert binary.read_bytes() == BINARY
    rules = scan.rules_dir()
    assert calls == [
        ["git", "init", "--quiet", rules],
        ["git", "-C", rules, "fetch", "--quiet", "--depth", "1", scan.RULES_REPOSITORY, scan.RULES_COMMIT],
        ["git", "-C", rules, "checkout", "--quiet", "FETCH_HEAD"],
    ]


def test_a_hash_mismatch_is_a_tool_error_and_removes_the_binary(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_download(monkeypatch, scan, b"tampered")
    calls = fake_opengrep(monkeypatch, scan, None)
    with pytest.raises(SystemExit) as stop:
        scan.install()
    assert stop.value.code == 1
    assert "::error::[tool] The OpenGrep download has sha256" in capsys.readouterr().out
    assert not Path(scan.binary_path()).exists()
    assert calls == []


@pytest.mark.parametrize(("system", "machine"), [("Darwin", "arm64"), ("Linux", "aarch64"), ("Windows", "AMD64")])
def test_an_unsupported_platform_is_a_configuration_error(
    scan: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    system: str,
    machine: str,
) -> None:
    monkeypatch.setattr(scan.platform, "system", lambda: system)
    monkeypatch.setattr(scan.platform, "machine", lambda: machine)
    urls = fake_download(monkeypatch, scan, BINARY)
    with pytest.raises(SystemExit):
        scan.install()
    assert "::error::[configuration] OpenGrep v1.33.0 is supported on Linux x86_64 only" in capsys.readouterr().out
    assert urls == []


def test_a_failed_rules_fetch_is_a_tool_error(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_opengrep(monkeypatch, scan, None, returncode=128)
    with pytest.raises(SystemExit):
        scan.fetch_rules()
    assert "::error::[tool] 'git init --quiet" in capsys.readouterr().out


class FakeResponse:
    def __init__(self, data: bytes) -> None:
        self.data = data

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self) -> bytes:
        return self.data


def test_download_writes_the_response_to_the_target(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(scan.urllib.request, "urlopen", lambda url, timeout: FakeResponse(b"data"))
    scan.download("https://example.invalid/x", str(tmp_path / "x"))
    assert (tmp_path / "x").read_bytes() == b"data"


def test_a_failed_download_is_a_tool_error(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    def refuse(url: str, timeout: int) -> None:
        raise OSError("offline")

    monkeypatch.setattr(scan.urllib.request, "urlopen", refuse)
    with pytest.raises(SystemExit):
        scan.download("https://example.invalid/x", str(tmp_path / "x"))
    assert "::error::[tool] https://example.invalid/x cannot be downloaded: offline" in capsys.readouterr().out


@pytest.mark.parametrize("argv", [["x"], ["x", "other"], ["x", "run", "extra"]])
def test_a_wrong_command_is_a_configuration_error(
    scan: ModuleType, capsys: pytest.CaptureFixture[str], argv: list[str]
) -> None:
    with pytest.raises(SystemExit):
        scan.main(argv)
    assert "::error::[configuration] usage" in capsys.readouterr().out


def test_main_dispatches_to_the_step(scan: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[str] = []
    monkeypatch.setattr(scan, "run", lambda: called.append("run"))
    monkeypatch.setattr(scan, "install", lambda: called.append("install"))
    scan.main(["x", "run"])
    assert called == ["run"]


def test_load_report_returns_an_empty_report_when_fail_returns(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    messages: list[str] = []
    monkeypatch.setattr(scan, "fail", lambda category, message: messages.append(category))
    assert scan.load_report(str(tmp_path / "missing.json")) == {}
    assert messages == ["tool"]


def test_the_script_runs_main_when_executed(
    scan: ModuleType, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["opengrep_scan.py"])
    with pytest.raises(SystemExit) as stop:
        runpy.run_path(str(REPO_ROOT / "tools" / "opengrep_scan.py"), run_name="__main__")
    assert stop.value.code == 1
    assert "::error::[configuration] usage" in capsys.readouterr().out


class TestWorkflow:
    @pytest.fixture()
    def workflow(self) -> dict[Any, Any]:
        loaded: dict[Any, Any] = yaml.safe_load(SCOPED_WORKFLOW.read_text(encoding="utf-8"))
        return loaded

    def test_it_reads_files_only_and_uses_no_secret(self, workflow: dict[Any, Any]) -> None:
        text = SCOPED_WORKFLOW.read_text(encoding="utf-8")
        assert workflow["jobs"]["opengrep"]["permissions"] == {"contents": "read"}
        assert "secrets." not in text

    def test_it_runs_on_pull_requests_pushes_and_by_hand(self, workflow: dict[Any, Any]) -> None:
        triggers = workflow["on"] if "on" in workflow else workflow[True]
        assert set(triggers) == {"pull_request", "push", "workflow_dispatch"}
        assert triggers["push"]["branches"] == ["main"]

    def test_it_runs_the_script_of_this_repository_at_the_major_tag(self, workflow: dict[Any, Any]) -> None:
        steps = workflow["jobs"]["opengrep"]["steps"]
        fetch = next(step for step in steps if step.get("with", {}).get("repository"))
        assert fetch["with"]["repository"] == "TirSystem/git-workflows"
        assert fetch["with"]["ref"] == "v3"
        runs = [step.get("run", "") for step in steps]
        assert "python3 shared-scripts/tools/opengrep_scan.py install" in runs
        assert "python3 shared-scripts/tools/opengrep_scan.py run" in runs
