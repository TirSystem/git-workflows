"""Offline tests for the reusable C++ and C# quality-check workflows (ADR-0008).

The shell steps run with stub tools in a throwaway git repository, so no
network, no clang and no .NET SDK are needed.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

from workflow_source import REPO_ROOT

CPP_WORKFLOW = REPO_ROOT / ".gitea" / "workflows" / "quality-checks-cpp.yml"
CSHARP_WORKFLOW = REPO_ROOT / ".gitea" / "workflows" / "quality-checks-csharp.yml"
CPP_SCRIPT = REPO_ROOT / "tools" / "quality-checks-cpp.sh"
CSHARP_SCRIPT = REPO_ROOT / "tools" / "quality-checks-csharp.sh"
BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(BASH is None, reason="bash is needed to run the workflow steps")

# A script run: the finished process and the tool calls the stubs logged.
Run = tuple[subprocess.CompletedProcess[str], list[str]]


def load(path: Path) -> dict[str, Any]:  # parsed YAML has no fixed shape
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def inputs_of(path: Path) -> dict[str, Any]:
    return load(path)[True]["workflow_call"]["inputs"]  # PyYAML reads `on` as True


@pytest.mark.parametrize(
    "workflow, script, job",
    [
        (CPP_WORKFLOW, "quality-checks-cpp.sh", "quality-checks-cpp"),
        (CSHARP_WORKFLOW, "quality-checks-csharp.sh", "quality-checks-csharp"),
    ],
    ids=["cpp", "csharp"],
)
class TestDefinition:
    def test_has_least_privilege_and_needs_no_secret(self, workflow: Path, script: str, job: str) -> None:
        document = load(workflow)
        assert document["jobs"][job]["permissions"] == {"contents": "read"}
        assert "secrets" not in workflow.read_text(encoding="utf-8").replace("needs no secret", "")

    def test_embeds_no_script_and_runs_the_file_in_three_steps(
        self,
        workflow: Path,
        script: str,
        job: str,
    ) -> None:
        steps = load(workflow)["jobs"][job]["steps"]
        commands = [step["run"] for step in steps if "run" in step]
        assert commands == [f"bash shared-scripts/tools/{script} {c}" for c in ("validate", "install", "run")]

    def test_fetches_the_script_at_the_tools_ref_input(self, workflow: Path, script: str, job: str) -> None:
        steps = load(workflow)["jobs"][job]["steps"]
        fetch = next(step for step in steps if step.get("name") == "Fetch the shared script")
        assert fetch["with"] == {
            "repository": "TirSystem/github-action",
            "ref": "${{ inputs.tools-ref }}",
            "path": "shared-scripts",
        }
        assert inputs_of(workflow)["tools-ref"]["default"] == "v1"

    def test_inputs_reach_the_script_only_through_the_environment(
        self,
        workflow: Path,
        script: str,
        job: str,
    ) -> None:
        for step in load(workflow)["jobs"][job]["steps"]:
            assert "${{" not in step.get("run", "")

    def test_script_is_a_file_that_parses(self, workflow: Path, script: str, job: str) -> None:
        result = subprocess.run(
            [BASH, "-n", str(REPO_ROOT / "tools" / script)], text=True, capture_output=True
        )
        assert result.returncode == 0, result.stderr

    def test_unknown_command_is_refused(self, workflow: Path, script: str, job: str) -> None:
        result = subprocess.run(
            [BASH, str(REPO_ROOT / "tools" / script), "bogus"], text=True, capture_output=True
        )
        assert result.returncode == 2


def test_cpp_inputs_and_exact_defaults() -> None:
    inputs = inputs_of(CPP_WORKFLOW)
    assert set(inputs) == {
        "working-directory",
        "std",
        "compile-commands-dir",
        "clang-format-version",
        "clang-tidy-version",
        "tools-ref",
    }
    assert inputs["std"]["default"] == "c++20"
    assert inputs["compile-commands-dir"]["default"] == ""
    assert inputs["clang-format-version"]["default"] == "23.1.3"
    assert inputs["clang-tidy-version"]["default"] == "22.1.8"


def test_csharp_inputs_and_exact_sdk_default() -> None:
    inputs = inputs_of(CSHARP_WORKFLOW)
    assert set(inputs) == {"working-directory", "project", "dotnet-sdk-version", "tools-ref"}
    assert inputs["dotnet-sdk-version"]["default"] == "10.0.401"


def test_cpp_script_and_workflow_do_not_mention_cppcheck() -> None:
    for path in (CPP_SCRIPT, CPP_WORKFLOW):
        assert "cppcheck" not in path.read_text(encoding="utf-8").lower(), path.name


# ----------------------------------------------------------------- helpers
def make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return root


def add_files(root: Path, *relative: str) -> None:
    for name in relative:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n", encoding="utf-8", newline="\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)


def stub(directory: Path, name: str) -> Path:
    path = directory / name
    path.write_text(
        "#!/usr/bin/env bash\n"
        'name="$(basename "$0")"\n'
        '[ "$name" = dotnet ] && name="dotnet $1"\n'
        'echo "$name :: $*" >> "$STUB_LOG"\n'
        'case ",${STUB_FAIL}," in\n'
        '  *",$name,"*) echo "src/a.cpp:3:1: stub finding from $name"; exit 1 ;;\n'
        "esac\n"
        "exit 0\n",
        encoding="utf-8",
        newline="\n",
    )
    path.chmod(0o755)
    return path


def run_script(script: Path, command: str, cwd: Path, tmp_path: Path, **env: str) -> Run:
    log = tmp_path / "tools.log"
    environment = dict(os.environ)
    environment.update({"STUB_LOG": log.as_posix(), "STUB_FAIL": ""})
    environment.update(env)
    result = subprocess.run(
        [BASH, str(script), command], cwd=cwd, env=environment, text=True, capture_output=True
    )
    calls = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    return result, calls


# --------------------------------------------------------------------- C++
@pytest.fixture
def cpp_bin(tmp_path: Path) -> Path:
    directory = tmp_path / "bin"
    directory.mkdir()
    for tool in ("clang-format", "clang-tidy"):
        stub(directory, tool)
    return directory


def cpp_env(cpp_bin: Path, **extra: str) -> dict[str, str]:
    values = {
        "WORKING_DIRECTORY": ".",
        "STD": "c++20",
        "COMPILE_COMMANDS_DIR": "",
        "CLANG_FORMAT_VERSION": "23.1.3",
        "CLANG_TIDY_VERSION": "22.1.8",
        "QC_VENV": "/nonexistent",
        "QC_BIN": cpp_bin.as_posix(),
    }
    values.update(extra)
    return values


class TestCppValidate:
    def run(self, tmp_path: Path, cpp_bin: Path, **extra: str) -> Run:
        return run_script(CPP_SCRIPT, "validate", tmp_path, tmp_path, **cpp_env(cpp_bin, **extra))

    def test_accepts_the_defaults(self, tmp_path: Path, cpp_bin: Path) -> None:
        result, _ = self.run(tmp_path, cpp_bin)
        assert result.returncode == 0, result.stdout

    @pytest.mark.parametrize("std", ["c++17", "c++23", "gnu++20"])
    def test_accepts_a_cpp_standard(self, tmp_path: Path, cpp_bin: Path, std: str) -> None:
        assert self.run(tmp_path, cpp_bin, STD=std)[0].returncode == 0

    @pytest.mark.parametrize("std", ["", "c17", "c++", "latest", "c++20; rm"])
    def test_rejects_a_value_that_is_not_a_cpp_standard(
        self,
        tmp_path: Path,
        cpp_bin: Path,
        std: str,
    ) -> None:
        result, _ = self.run(tmp_path, cpp_bin, STD=std)
        assert result.returncode == 1 and "[configuration]" in result.stdout

    @pytest.mark.parametrize("directory", ["/etc", "..", "../x", "a/../..", ""])
    def test_rejects_a_working_directory_outside_the_repository(
        self,
        tmp_path: Path,
        cpp_bin: Path,
        directory: str,
    ) -> None:
        result, _ = self.run(tmp_path, cpp_bin, WORKING_DIRECTORY=directory)
        assert result.returncode == 1 and "working-directory" in result.stdout

    @pytest.mark.parametrize("directory", ["/tmp/build", "../build"])
    def test_rejects_a_compile_commands_dir_outside_the_repository(
        self,
        tmp_path: Path,
        cpp_bin: Path,
        directory: str,
    ) -> None:
        result, _ = self.run(tmp_path, cpp_bin, COMPILE_COMMANDS_DIR=directory)
        assert result.returncode == 1 and "compile-commands-dir" in result.stdout

    @pytest.mark.parametrize("name", ["CLANG_FORMAT_VERSION", "CLANG_TIDY_VERSION"])
    @pytest.mark.parametrize("version", ["", "latest", "23", ">=23", "23.1.3 --pre"])
    def test_rejects_a_version_that_is_not_exact(
        self,
        tmp_path: Path,
        cpp_bin: Path,
        name: str,
        version: str,
    ) -> None:
        result, _ = self.run(tmp_path, cpp_bin, **{name: version})
        assert result.returncode == 1 and "exact version" in result.stdout


class TestCppRun:
    @pytest.fixture
    def repo(self, tmp_path: Path) -> Path:
        root = make_repo(tmp_path)
        add_files(root, ".clang-format")
        return root

    def run(self, repo: Path, tmp_path: Path, cpp_bin: Path, **extra: str) -> Run:
        return run_script(CPP_SCRIPT, "run", repo, tmp_path, **cpp_env(cpp_bin, **extra))

    def test_runs_clang_format_once_and_clang_tidy_per_language(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        add_files(repo, "src/a.cpp", "src/a.hpp", "lib/c.c")
        result, calls = self.run(repo, tmp_path, cpp_bin)

        assert result.returncode == 0, result.stdout + result.stderr
        assert [c.split(" :: ")[0] for c in calls] == ["clang-format", "clang-tidy", "clang-tidy"]
        assert "--dry-run -Werror" in calls[0]
        assert "src/a.cpp" in calls[0] and "lib/c.c" in calls[0]
        assert "-- -std=c++20" in calls[1] and "lib/c.c" not in calls[1]
        assert "-- -std=c17" in calls[2] and "lib/c.c" in calls[2]
        assert "All selected checks passed." in result.stdout

    def test_the_std_input_reaches_clang_tidy(self, repo: Path, tmp_path: Path, cpp_bin: Path) -> None:
        add_files(repo, "a.cpp")
        _, calls = self.run(repo, tmp_path, cpp_bin, STD="c++17")
        assert "-- -std=c++17" in calls[1]

    def test_a_compile_database_is_used_instead_of_a_standard(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        add_files(repo, "a.cpp", "build/compile_commands.json")
        result, calls = self.run(repo, tmp_path, cpp_bin, COMPILE_COMMANDS_DIR="build")
        assert result.returncode == 0, result.stdout
        assert len(calls) == 2
        database = re.search(r"-p (\S+)", calls[1])
        assert database is not None and database.group(1).endswith(f"/{repo.name}/build")
        assert "-std=" not in calls[1]

    def test_clang_tidy_gets_default_checks_without_a_clang_tidy_file(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        add_files(repo, "a.cpp")
        _, calls = self.run(repo, tmp_path, cpp_bin)
        assert "--checks=clang-diagnostic-*,clang-analyzer-*" in calls[1]
        assert "--checks=" not in calls[0]

    def test_no_default_checks_when_a_clang_tidy_file_is_in_the_repository_root(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        add_files(repo, "a.cpp", ".clang-tidy")
        _, calls = self.run(repo, tmp_path, cpp_bin)
        assert len(calls) == 2
        assert not any("--checks=" in call for call in calls)

    @pytest.mark.parametrize(
        ("files", "extra", "tidy_calls"),
        [
            (("a.cpp", "lib/c.c"), {}, 2),
            (("a.cpp", ".clang-tidy"), {}, 1),
            (("a.cpp", "build/compile_commands.json"), {"COMPILE_COMMANDS_DIR": "build"}, 1),
        ],
        ids=["no-clang-tidy-file", "clang-tidy-file", "compile-database"],
    )
    def test_every_clang_tidy_call_treats_warnings_as_errors(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
        files: tuple[str, ...],
        extra: dict[str, str],
        tidy_calls: int,
    ) -> None:
        add_files(repo, *files)
        _, calls = self.run(repo, tmp_path, cpp_bin, **extra)
        tidy = [c for c in calls if c.startswith("clang-tidy")]
        assert len(tidy) == tidy_calls
        assert all("--warnings-as-errors=*" in call for call in tidy)
        assert "--warnings-as-errors" not in calls[0] and calls[0].startswith("clang-format")

    def test_no_default_checks_when_a_clang_tidy_file_is_above_the_working_directory(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        add_files(repo, "service/a.cpp", ".clang-tidy")
        _, calls = self.run(repo, tmp_path, cpp_bin, WORKING_DIRECTORY="service")
        assert len(calls) == 2
        assert not any("--checks=" in call for call in calls)

    def test_a_compile_database_is_resolved_from_the_repository_root(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        add_files(repo, "service/a.cpp", "build/compile_commands.json")
        result, calls = self.run(
            repo, tmp_path, cpp_bin, WORKING_DIRECTORY="service", COMPILE_COMMANDS_DIR="build"
        )
        assert result.returncode == 0, result.stdout
        database = re.search(r"-p (\S+)", calls[1])
        assert database is not None and database.group(1).endswith(f"/{repo.name}/build")

    def test_a_compile_database_only_inside_the_working_directory_is_not_found(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        add_files(repo, "service/a.cpp", "service/build/compile_commands.json")
        result, calls = self.run(
            repo, tmp_path, cpp_bin, WORKING_DIRECTORY="service", COMPILE_COMMANDS_DIR="build"
        )
        assert result.returncode == 1 and "[configuration]" in result.stdout
        assert calls == []

    def test_a_missing_compile_database_is_a_configuration_error(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        add_files(repo, "a.cpp")
        result, calls = self.run(repo, tmp_path, cpp_bin, COMPILE_COMMANDS_DIR="build")
        assert result.returncode == 1 and "compile_commands.json" in result.stdout
        assert calls == []

    def test_a_missing_clang_format_file_is_a_configuration_error(
        self,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        repo = make_repo(tmp_path)
        add_files(repo, "a.cpp")
        result, calls = self.run(repo, tmp_path, cpp_bin)
        assert result.returncode == 1
        assert "[configuration]" in result.stdout and ".clang-format" in result.stdout
        assert calls == []

    def test_a_clang_format_file_above_the_working_directory_is_found(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        add_files(repo, "service/a.cpp")
        result, _ = run_script(
            CPP_SCRIPT,
            "run",
            repo,
            tmp_path,
            **cpp_env(cpp_bin, WORKING_DIRECTORY="service"),
        )
        assert result.returncode == 0, result.stdout

    def test_a_failing_tool_fails_the_job_and_the_other_still_runs(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        add_files(repo, "src/a.cpp")
        result, calls = self.run(repo, tmp_path, cpp_bin, STUB_FAIL="clang-format")
        assert result.returncode == 1
        assert len(calls) == 2, "clang-tidy runs after clang-format failed"
        assert "::group::clang-format" in result.stdout
        assert "src/a.cpp:3:1: stub finding from clang-format" in result.stdout
        assert "FAIL clang-format" in result.stdout and "PASS clang-tidy (C++)" in result.stdout
        assert "Quality checks failed: clang-format" in result.stdout

    def test_a_repository_without_c_or_cpp_files_passes_with_a_notice(
        self,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        repo = make_repo(tmp_path)
        add_files(repo, "README.md")
        result, calls = self.run(repo, tmp_path, cpp_bin)
        assert result.returncode == 0 and calls == []
        assert "No C or C++ files" in result.stdout

    def test_only_tracked_files_under_the_working_directory_are_checked(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        add_files(repo, "top.cpp", "service/api.cpp")
        (repo / "service" / "untracked.cpp").write_text("x\n", encoding="utf-8")
        _, calls = self.run(repo, tmp_path, cpp_bin, WORKING_DIRECTORY="service")
        text = "\n".join(calls)
        assert "api.cpp" in text and "top.cpp" not in text and "untracked" not in text

    def test_no_file_is_changed(self, repo: Path, tmp_path: Path, cpp_bin: Path) -> None:
        add_files(repo, "a.cpp")

        def snapshot() -> dict[str, bytes]:
            return {p.name: p.read_bytes() for p in repo.iterdir() if p.is_file()}

        before = snapshot()
        self.run(repo, tmp_path, cpp_bin, STUB_FAIL="clang-tidy (C++)")
        assert snapshot() == before

    def test_a_missing_working_directory_is_a_configuration_error(
        self,
        repo: Path,
        tmp_path: Path,
        cpp_bin: Path,
    ) -> None:
        result, _ = self.run(repo, tmp_path, cpp_bin, WORKING_DIRECTORY="nope")
        assert result.returncode == 1 and "[configuration]" in result.stdout


def test_cpp_install_pins_both_tools_to_the_exact_versions(tmp_path: Path) -> None:
    """`install` creates the venv and installs `==` versions; checked with a fake pip."""
    venv = tmp_path / "venv"
    fake_python = tmp_path / "bin"
    fake_python.mkdir()
    log = tmp_path / "pip.log"
    python3 = fake_python / "python3"
    python3.write_text(
        "#!/usr/bin/env bash\n"
        'mkdir -p "$3/bin"\n'
        "printf '#!/usr/bin/env bash\\necho \"$*\" >> \"%s\"\\n' > \"$3/bin/pip\"\n" % log.as_posix()
        + 'chmod +x "$3/bin/pip"\n',
        encoding="utf-8",
        newline="\n",
    )
    python3.chmod(0o755)
    environment = dict(os.environ)
    environment["PATH"] = f"{fake_python.as_posix()}:{environment['PATH']}"
    environment.update(
        {
            "QC_VENV": venv.as_posix(),
            "CLANG_FORMAT_VERSION": "23.1.3",
            "CLANG_TIDY_VERSION": "22.1.8",
        }
    )
    result = subprocess.run(
        [BASH, str(CPP_SCRIPT), "install"], env=environment, text=True, capture_output=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    installed = log.read_text(encoding="utf-8")
    assert "clang-format==23.1.3" in installed
    assert "clang-tidy==22.1.8" in installed


# --------------------------------------------------------------------- C#
@pytest.fixture
def dotnet_stub(tmp_path: Path) -> Path:
    directory = tmp_path / "dotnet-bin"
    directory.mkdir()
    return stub(directory, "dotnet")


def csharp_env(dotnet_stub: Path, tmp_path: Path, **extra: str) -> dict[str, str]:
    values = {
        "WORKING_DIRECTORY": ".",
        "PROJECT": "",
        "DOTNET_SDK_VERSION": "10.0.401",
        "DOTNET_ROOT": (tmp_path / "dotnet-root").as_posix(),
        "QC_DOTNET": dotnet_stub.as_posix(),
    }
    values.update(extra)
    return values


class TestCsharpValidate:
    def run(self, tmp_path: Path, dotnet_stub: Path, **extra: str) -> Run:
        return run_script(
            CSHARP_SCRIPT, "validate", tmp_path, tmp_path, **csharp_env(dotnet_stub, tmp_path, **extra)
        )

    @pytest.mark.parametrize("version", ["10.0.401", "10.0.100", "11.0.100", "100.1.2"])
    def test_accepts_an_exact_sdk_of_version_10_or_later(
        self,
        tmp_path: Path,
        dotnet_stub: Path,
        version: str,
    ) -> None:
        assert self.run(tmp_path, dotnet_stub, DOTNET_SDK_VERSION=version)[0].returncode == 0

    @pytest.mark.parametrize(
        "version",
        ["", "8.0.425", "9.0.100", "10.0", "10", "10.0.x", "latest", "10.0.401-rc.1", "10.0.401 --verbose"],
    )
    def test_rejects_an_old_or_inexact_sdk(self, tmp_path: Path, dotnet_stub: Path, version: str) -> None:
        result, _ = self.run(tmp_path, dotnet_stub, DOTNET_SDK_VERSION=version)
        assert result.returncode == 1
        assert "[configuration]" in result.stdout and "dotnet-sdk-version" in result.stdout

    @pytest.mark.parametrize("directory", ["/etc", "..", "../x", ""])
    def test_rejects_a_working_directory_outside_the_repository(
        self,
        tmp_path: Path,
        dotnet_stub: Path,
        directory: str,
    ) -> None:
        result, _ = self.run(tmp_path, dotnet_stub, WORKING_DIRECTORY=directory)
        assert result.returncode == 1 and "working-directory" in result.stdout

    @pytest.mark.parametrize("project", ["/etc/x.sln", "../x.sln"])
    def test_rejects_a_project_outside_the_working_directory(
        self,
        tmp_path: Path,
        dotnet_stub: Path,
        project: str,
    ) -> None:
        result, _ = self.run(tmp_path, dotnet_stub, PROJECT=project)
        assert result.returncode == 1 and "project" in result.stdout


class TestCsharpInstall:
    def test_installs_the_exact_version_with_the_official_script(
        self,
        tmp_path: Path,
        dotnet_stub: Path,
    ) -> None:
        root = tmp_path / "dotnet-root"
        installer = tmp_path / "dotnet-install.sh"
        installer.write_text(
            "#!/usr/bin/env bash\n"
            'echo "$*" >> "$STUB_LOG"\n'
            'dir=""\n'
            'while [ "$#" -gt 0 ]; do [ "$1" = --install-dir ] && dir="$2"; shift; done\n'
            'mkdir -p "$dir"\n'
            "printf '#!/usr/bin/env bash\\necho 10.0.401\\n' > \"$dir/dotnet\"\n"
            'chmod +x "$dir/dotnet"\n',
            encoding="utf-8",
            newline="\n",
        )
        result, calls = run_script(
            CSHARP_SCRIPT,
            "install",
            tmp_path,
            tmp_path,
            **csharp_env(dotnet_stub, tmp_path, QC_DOTNET_INSTALL_SCRIPT=installer.as_posix()),
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert calls and "--version 10.0.401" in calls[0]
        assert f"--install-dir {root.as_posix()}" in calls[0]
        assert "10.0.401" in result.stdout


class TestCsharpRun:
    @pytest.fixture
    def repo(self, tmp_path: Path) -> Path:
        return make_repo(tmp_path)

    def run(self, repo: Path, tmp_path: Path, dotnet_stub: Path, **extra: str) -> Run:
        return run_script(
            CSHARP_SCRIPT, "run", repo, tmp_path, **csharp_env(dotnet_stub, tmp_path, **extra)
        )

    def test_runs_format_and_build_on_the_single_solution(
        self,
        repo: Path,
        tmp_path: Path,
        dotnet_stub: Path,
    ) -> None:
        add_files(repo, "App.sln", "src/App.csproj", "src/Program.cs")
        result, calls = self.run(repo, tmp_path, dotnet_stub)

        assert result.returncode == 0, result.stdout + result.stderr
        assert [c.split(" :: ")[0] for c in calls] == ["dotnet format", "dotnet build"]
        assert "App.sln" in calls[0] and "--verify-no-changes" in calls[0]
        assert "App.sln" in calls[1] and "-warnaserror" in calls[1]
        assert "All selected checks passed." in result.stdout

    def test_uses_the_single_project_when_there_is_no_solution(
        self,
        repo: Path,
        tmp_path: Path,
        dotnet_stub: Path,
    ) -> None:
        add_files(repo, "src/App.csproj", "src/Program.cs")
        _, calls = self.run(repo, tmp_path, dotnet_stub)
        assert "src/App.csproj" in calls[0]

    def test_several_projects_without_a_solution_need_the_project_input(
        self,
        repo: Path,
        tmp_path: Path,
        dotnet_stub: Path,
    ) -> None:
        add_files(repo, "a/A.csproj", "b/B.csproj", "a/P.cs")
        result, calls = self.run(repo, tmp_path, dotnet_stub)
        assert result.returncode == 1 and calls == []
        assert "[configuration]" in result.stdout
        assert "a/A.csproj" in result.stdout and "b/B.csproj" in result.stdout

    def test_the_project_input_picks_one(self, repo: Path, tmp_path: Path, dotnet_stub: Path) -> None:
        add_files(repo, "a/A.csproj", "b/B.csproj", "a/P.cs")
        result, calls = self.run(repo, tmp_path, dotnet_stub, PROJECT="b/B.csproj")
        assert result.returncode == 0 and "b/B.csproj" in calls[0]

    def test_a_missing_project_file_is_a_configuration_error(
        self,
        repo: Path,
        tmp_path: Path,
        dotnet_stub: Path,
    ) -> None:
        add_files(repo, "a/P.cs")
        result, calls = self.run(repo, tmp_path, dotnet_stub, PROJECT="nope.csproj")
        assert result.returncode == 1 and "does not exist" in result.stdout and calls == []

    def test_csharp_files_without_a_project_are_a_configuration_error(
        self,
        repo: Path,
        tmp_path: Path,
        dotnet_stub: Path,
    ) -> None:
        add_files(repo, "Program.cs")
        result, calls = self.run(repo, tmp_path, dotnet_stub)
        assert result.returncode == 1 and calls == []
        assert "[configuration]" in result.stdout and "no solution or project" in result.stdout

    def test_a_repository_without_csharp_files_passes_with_a_notice(
        self,
        repo: Path,
        tmp_path: Path,
        dotnet_stub: Path,
    ) -> None:
        add_files(repo, "README.md")
        result, calls = self.run(repo, tmp_path, dotnet_stub)
        assert result.returncode == 0 and calls == []
        assert "No C# files" in result.stdout

    def test_a_failing_tool_fails_the_job_and_the_other_still_runs(
        self,
        repo: Path,
        tmp_path: Path,
        dotnet_stub: Path,
    ) -> None:
        add_files(repo, "App.sln", "Program.cs")
        result, calls = self.run(repo, tmp_path, dotnet_stub, STUB_FAIL="dotnet format")
        assert result.returncode == 1 and len(calls) == 2
        assert "::group::dotnet format --verify-no-changes" in result.stdout
        assert "FAIL dotnet format --verify-no-changes" in result.stdout
        assert "PASS dotnet build -warnaserror" in result.stdout
        assert "Quality checks failed: dotnet format --verify-no-changes" in result.stdout

    def test_only_files_under_the_working_directory_are_considered(
        self,
        repo: Path,
        tmp_path: Path,
        dotnet_stub: Path,
    ) -> None:
        add_files(repo, "Top.sln", "svc/Svc.csproj", "svc/P.cs", "Top.cs")
        result, calls = self.run(repo, tmp_path, dotnet_stub, WORKING_DIRECTORY="svc")
        assert result.returncode == 0
        assert "Svc.csproj" in calls[0] and "Top.sln" not in calls[0]

    def test_a_missing_working_directory_is_a_configuration_error(
        self,
        repo: Path,
        tmp_path: Path,
        dotnet_stub: Path,
    ) -> None:
        result, _ = self.run(repo, tmp_path, dotnet_stub, WORKING_DIRECTORY="nope")
        assert result.returncode == 1 and "[configuration]" in result.stdout
